# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import time
import logging

from collections import OrderedDict

from steelscript.appresponse.core.types import AppResponseException,\
     TimeFilter, ResourceObject
from steelscript.appresponse.core.clips import Clip
from steelscript.appresponse.core.fs import File
from steelscript.appresponse.core.capture import Job
from steelscript.common._fs import SteelScriptDir

logger = logging.getLogger(__name__)

PACKETS_REPORT_SERVICE_NAME = 'npm.probe.reports'
GENERAL_REPORT_SERVICE_NAME = 'npm.reports'


class Source(object):

    def __init__(self, name, path=None, type_=None, origin=None):
        self.name = name
        self.path = path
        self.type = type_
        self.origin = origin

    def to_dict(self):
        ret = {}
        for k in vars(self):
            v = getattr(self, k)
            if v:
                ret[k] = v
        return ret


class PacketsSource(Source):

    CLIP_PREFIX = 'clips/'
    JOB_PREFIX = 'jobs/'
    FILE_PREFIX = 'fs'

    def __init__(self, packets_obj):
        if isinstance(packets_obj, Clip):
            path = '{}{}'.format(self.CLIP_PREFIX, packets_obj.id)
        elif isinstance(packets_obj, File):
            path = '{}{}'.format(self.FILE_PREFIX, packets_obj.id)
        elif isinstance(packets_obj, Job):
            path = '{}{}'.format(self.JOB_PREFIX, packets_obj.id)
        else:
            raise AppResponseException(
                'Can only support job or clip or file packet source')

        super(PacketsSource, self).__init__(name='packets', path=path)


class ReportService(object):

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self._columns = {}

    def get_sources(self):
        """Get the names and granularites of sources."""
        ret = []
        for svc in [PACKETS_REPORT_SERVICE_NAME,
                    GENERAL_REPORT_SERVICE_NAME]:
            svcdef = self.appresponse.find_service(svc)
            datarep = svcdef.bind('sources')
            ret.extend(datarep.execute('get').data['items'])
        return ret

    def _load_columns(self):
        """Load columns data from local cache file."""
        ss_dir = SteelScriptDir('AppResponse', 'files')

        for service_name in [PACKETS_REPORT_SERVICE_NAME,
                             GENERAL_REPORT_SERVICE_NAME]:

            svcdef = self.appresponse.find_service(service_name)

            for source_name in svcdef.bind('source_names').data:

                version = self.appresponse.versions[service_name]
                columns_filename = source_name + '-columns-' + version + '.pcl'

                columns_file = ss_dir.get_data(columns_filename)
                if not columns_file.data:
                    self._columns[source_name] = \
                        self._fetch_columns(svcdef, source_name)
                    columns_file.data = self._columns[source_name]
                    columns_file.write()
                    logger.debug("Wrote columns data into {}"
                                 .format(columns_filename))
                else:
                    logger.debug("Loading columns data from {}"
                                 .format(columns_filename))
                    columns_file.read()
                    self._columns[source_name] = columns_file.data

    @property
    def columns(self):
        if not self._columns:
            self._load_columns()
        return self._columns

    def _fetch_columns(self, service_def, source_name):
        """Return an ordered dict representing all the columns."""

        logger.debug("Obtaining source columns for source {} via resource "
                     "'source_columns' via link 'get' within service {}"
                     .format(source_name, service_def.servicedef.name))

        datarep = service_def.bind('source_columns', name=source_name)
        cols = datarep.execute('get').data['items']

        # Create a ordered dict
        return OrderedDict(sorted(zip(map(lambda x: x['id'], cols), cols)))

    def get_columns(self):
        return self.columns

    def get_column_names(self):
        """Return a list of column names."""

        return self.columns.keys()

    def create_report(self, data_def_request):
        """Create a report instance with just one data definition request."""

        report = Report(self.appresponse)
        report.add(data_def_request)
        report.run()
        return report

    def create_instance(self, data_defs):
        """Create a report instance with multiple data definition requests.

        :param data_defs: list of DataDef objects
        :return: one ReportInstance object
        """
        if not data_defs:
            msg = 'No data definitions are provided.'
            raise AppResponseException(msg)

        if (any(dd.source.name == 'packets' for dd in data_defs)
                and any(dd.source.name != 'packets' for dd in data_defs)):
            # Two report instance needs to be created, one uses 'npm.reports'
            # service, the other one uses 'npm.probe.reports' service
            # it would create unnecessary complexity to support this case
            # thus report error and let the user to create two separate
            # report instances

            msg = ('Both packets data source and non-packets data source are '
                   'being queried in this report, which is not supported. The '
                   'data source names include {}'
                   .format(', '.join(set([dd.source.name
                                          for dd in data_defs]))))
            raise AppResponseException(msg)

        def _create_and_run(service_name, data_defs):

            config = dict(data_defs=[dd.to_dict() for dd in data_defs])
            logger.debug("Creating instance with data definitions %s" % config)

            svcdef = self.appresponse.find_service(service_name)
            datarep = svcdef.bind('instances')
            resp = datarep.execute('create', _data=config)

            instance = ReportInstance(data=resp.data, datarep=resp)
            while not instance.is_complete():
                time.sleep(1)

            if instance.errors:
                err_msgs = ';\n'.join(instance.errors)
                raise AppResponseException(err_msgs)

            return instance

        if isinstance(data_defs[0].source, (Clip, File, Job)):
            # Needs to create a clip for for capture job packets source
            # Keep the clip till the instance is completed
            with self.appresponse.clips.create_clips(data_defs):
                # capture job data_defs are modified in place
                instance = _create_and_run(PACKETS_REPORT_SERVICE_NAME,
                                           data_defs)
        else:
            instance = _create_and_run(GENERAL_REPORT_SERVICE_NAME,
                                       data_defs)
        return instance


class ReportInstance(ResourceObject):
    """Main interface to interact with a probe report instance. """

    resource = 'instance'

    def __init__(self, data, servicedef=None, datarep=None):
        super(ReportInstance, self).__init__(data, servicedef, datarep)
        self.errors = []

    def is_complete(self):

        status = self.status

        if all([item['progress']['percent'] == 100
                for item in status]):
            # Check errors when all queries have completed
            for item in status:
                if item['state'] == 'error':
                    for m in item['messages']:
                        self.errors.append(m['text'])
                        logger.error("Error msg from status: {}"
                                     .format(m['text']))
            return True
        return False

    @property
    def status(self):
        logger.debug("Getting status of the report instance with id {}"
                     .format(self.id))
        return self.datarep.execute('get_status').data

    def get_data(self):
        return self.datarep.execute('get_data').data

    def delete(self):
        return self.datarep.execute('delete')


class DataDef(object):
    """This class provides an interface to build a data definition request
    suitable for uploading to a report.
    """
    def __init__(self, source, columns, start=None, end=None, duration=None,
                 time_range=None, granularity=None, resolution=None):
        """Initialize a data definition request object.

        :param source: packet source object, i.e. packet capture job;
            Source object for non-packets data sources.
        :param columns: list Key/Value column objects.
        :param start: epoch start time in seconds.
        :param end: epoch endtime in seconds.
        :param duration: string duration of data def request.
        :param time_range: string time range of data def request.
        :param str granularity: granularity in seconds. Required.
        :param str resolution: resolution in seconds. Optional

        For defining the overall time for the report, either a
        single `time_range` string may be used or a combination of
        `start`/`end`/`duration`.

        Further discussion on `granularity` and `resolution`:

        Granularity refers to the amount of time for which the data source
        computes a summary of the metrics it received. The data source
        examines all data and creates summaries for 1 second, 1 minute,
        5 minute, 15 minute, 1 hour, 6 hour and 1 day, etc.  Greater
        granularity (shorter time periods) results in greater accuracy.
        Lesser granularity (1 hour, 6 hours, 1 day) requires less processing
        and therefore the data is returned faster. Granularity must be
        specified as number of seconds.

        Resolution must be multiple of the requested granularity. For
        example, if you specify granularity of 5mins (300 seconds) then the
        resolution can be set to 5mins, 10mins, 15mins, etc. If the
        resolution is set to be equal of the granularity then it has no
        effect to the number of returned samples. The resolution is optional.

        """
        self.source = source
        self.columns = columns
        self.granularity = granularity
        self.resolution = resolution
        self.timefilter = TimeFilter(start=start, end=end,
                                     duration=duration, time_range=time_range)
        self._filters = []
        self._data = None

    def to_dict(self):

        data_def = dict()

        if isinstance(self.source, Source):
            data_def['source'] = self.source.to_dict()
        else:
            data_def['source'] = PacketsSource(self.source).to_dict()

        data_def['group_by'] = [col.name for col in self.columns if col.key]
        data_def['time'] = dict()
        for k in ['start', 'end']:
            v = getattr(self.timefilter, k)
            if v:
                data_def['time'][k] = str(v)

        for k in ['granularity', 'resolution']:
            v = getattr(self, k)
            if v:
                data_def['time'][k] = str(v)

        data_def['columns'] = [col.name for col in self.columns]

        if self._filters:
            data_def['filters'] = self._filters

        return data_def

    def add_filter(self, filter):
        """Add one traffic filter to the data def.

        :param filter: types.TrafficFilter object
        """
        self._filters.append(filter.as_dict())

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        """Set the data of data def as a list of dictionaries."""
        self._data = val


class Report(object):
    """This class is the main interface to build and run a report against
    an AppResponse appliance.
    """

    def __init__(self, appresponse):
        """Initialize a new report against the given AppResponse object.

        :param appresponse: the AppResponse object.
        """
        logger.debug("Initializing Report object with appresponse '{}'"
                     .format(appresponse.host))
        self.appresponse = appresponse
        self._data_defs = []
        self._instance = None

    def add(self, data_def_request):
        """Add one data definition request."""
        logger.debug("Adding a data_def request {}"
                     .format(data_def_request.to_dict()))
        self._data_defs.append(data_def_request)

    def _cast_number(self, result, source_name):
        """ Check records and convert string to integer/float. If the type
        of the column is 'number' or unit is not 'none', then check if
        the column name has 'avg' in its name, if yes, then convert it to
        float, otherwise to integer.

        :param dict result: includes metadata for one data def request
            as well as the response data for the data def request.
        :param string source_name: name of the source.
        """

        logger.debug("Converting string in records into integer/float")

        columns = self.appresponse.reports.columns[source_name]
        functions = [lambda x: x] * len(result['columns'])

        for i, col in enumerate(result['columns']):
            if columns[col]['type'] in ['integer', 'timestamp']:
                functions[i] = lambda x: None if x == 'NULL' else int(x)
            elif columns[col]['type'] in ('number', 'duration'):
                functions[i] = lambda x: None if x == 'NULL' else float(x)

        # operate on each column, then zip back into list of tuples
        datacols = []
        for i, c in enumerate(zip(*result['data'])):
            datacols.append(map(functions[i], c))
        records = zip(*datacols)

        return records

    def run(self):
        """Create a report instance and record the results of multiple
        data definition instances as a list of records (dictionaries).
        """
        if not self._instance:
            self._instance = \
                self.appresponse.reports.create_instance(self._data_defs)

            results = self._instance.get_data()['data_defs']

            for i, res in enumerate(results):
                if isinstance(self._data_defs[i].source, Source):
                    source_name = self._data_defs[i].source.name
                else:
                    source_name = 'packets'
                self._data_defs[i].columns = res['columns']
                if 'data' in res:
                    self._data_defs[i].data = self._cast_number(res,
                                                                source_name)
                else:
                    self._data_defs[i].data = []
                logger.debug("Obtained {} records for the {}th data request."
                             .format(len(self._data_defs[i].data), i))

    def get_data(self, index=0):
        """Return data for the indexed data definition requests.

        :param int index: Set to None to return data from all data definitions,
            defaults to returning the data from just the first data def.
        """
        if index is None:
            return [dd.data for dd in self._data_defs]

        return self._data_defs[index].data

    def get_legend(self, index=0, details=False):
        """Return legend information for the data definition.

        :param int index: Set to None to return data from all data definitions,
            defaults to returning the data from just the first data def.

        :param bool details: If True, return complete column dict, otherwise
            just short label ids for each column will be returned
        """
        def get_cols(cols):
            if details:
                return [self.appresponse.reports.columns[c] for c in cols]
            return [c for c in cols]

        if index is None:
            legend = [get_cols(dd.columns) for dd in self._data_defs]

        else:
            legend = get_cols(self._data_defs[index].columns)

        return legend

    def get_dataframe(self, index=0):
        """Return data in pandas DataFrame format for the indexed
        data definition requests.

        This will return a single DataFrame for the given index, unlike
        ``get_data`` and ``get_legend`` which will optionally return info
        for all data defs in a report.

        **Requires `pandas` library to be available in environment.**

        :param int index: DataDef to process into DataFrame.  Defaults to 0.
        """
        import pandas
        data = self.get_data(index)
        columns = self.get_legend(index)
        df = pandas.DataFrame(data, columns=columns)
        return df

    def delete(self):
        """Delete the report from the appliance."""
        self._instance.delete()
        self._instance = None
        self._data_defs = []
