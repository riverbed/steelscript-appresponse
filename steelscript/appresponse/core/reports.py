# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import time
import logging

from collections import OrderedDict

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import AppResponseException,\
    ServiceClass, TimeFilter
from steelscript.appresponse.core.clips import Clip
from steelscript.appresponse.core.fs import File
from steelscript.appresponse.core.capture import Job
from steelscript.common._fs import SteelScriptDir


logger = logging.getLogger(__name__)


class Source(object):

    def __init__(self, name, path, packets_obj):
        self.name = name
        self.path = path
        self.packets_obj = packets_obj

    def to_dict(self):
        return dict(name=self.name, path=self.path)


class PacketsSource(Source):

    def __init__(self, packets_obj):
        if isinstance(packets_obj, Clip):
            path = 'clips/%s' % packets_obj.prop.id
        elif isinstance(packets_obj, File):
            path = 'fs{}'.format(packets_obj.prop.id)
        elif isinstance(packets_obj, Job):
            path = 'jobs/{}'.format(packets_obj.prop.id)
        else:
            raise AppResponseException(
                'Can only support job or clip or file packet source')

        super(PacketsSource, self).__init__(name='packets', path=path,
                                            packets_obj=packets_obj)


class ProbeReportService(ServiceClass):

    SOURCE_NAME = 'packets'
    SERVICE_NAME = 'npm.probe.reports'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.instances = None
        self.source_columns = None
        self._columns = None

    def _bind_resources(self):

        # Init service
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

        # Init resources
        self.instances = self.servicedef.bind('instances')
        self.source_columns = self.servicedef.bind('source_columns',
                                                   name=self.SOURCE_NAME)

    def _load_columns(self):
        """Load columns data from local cache file."""
        ss_dir = SteelScriptDir('AppResponse', 'files')
        version = self.appresponse.versions[self.SERVICE_NAME]
        columns_filename = self.SOURCE_NAME + '-columns-' + version + '.pcl'

        columns_file = ss_dir.get_data(columns_filename)
        if not columns_file.data:
            self._columns = self.get_columns()
            columns_file.data = self._columns
            columns_file.write()
            logger.debug("Wrote columns data into %s" % columns_filename)
        else:
            logger.debug("Loading columns data from %s" % columns_filename)
            columns_file.read()
            self._columns = columns_file.data

    @property
    def columns(self):
        if self._columns:
            return self._columns

        self._load_columns()
        return self._columns

    def get_columns(self):
        """Return an ordered dict representing all the columns."""

        logger.debug("Obtaining source columns via resource 'source_columns' "
                     "via link 'get'")

        cols = self.source_columns.execute('get').data['items']

        # Create a ordered dict
        return OrderedDict(sorted(zip(map(lambda x: x['id'], cols), cols)))

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

        Currenly only support data definition requests with capture jobs
        as the packets source. Will need to support packets source in
        formats of file, clips, etc.
        """
        with self.appresponse.clips.create_clips(data_defs):

            config = dict(data_defs=[dd.to_dict() for dd in data_defs])
            logger.debug("Creating instance with data definitions %s" % config)

            instance = ReportInstance(
                self.instances.execute('create', _data=config))

            while not instance.is_complete:
                time.sleep(1)

            if instance.errors:
                err_msgs = ';\n'.join(instance.errors)
                raise AppResponseException(err_msgs)

            return instance

    def get_instances(self):
        """Return all report instances."""

        resp = self.instances.execute('get')

        return [ReportInstance(self.get_instance_by_id(instance['id'])
                for instance in resp.data['items'])]

    def bulk_delete(self):
        self.instances.execute('bulk_delete')

    def get_instance_by_id(self, id_):
        """Return the report instance given the id."""

        resp = self.instances.execute(id=id_)
        return ReportInstance(resp)


class ReportInstance(object):
    """Main interface to interact with a probe report instance. """
    def __init__(self, datarep):
        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)
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
                     .format(self.prop.id))
        return self.datarep.execute('get_status').data

    def get_data(self):
        return self.datarep.execute('get_data').data

    def delete(self):
        return self.datarep.execute('delete')


class DataDef(object):
    """This class provides an interface to build a data definition request
    as a dict.
    """
    def __init__(self, source, columns, start=None, end=None, duration=None,
                 granularity=None, resolution=None, time_range=None):
        """Initialize a data definition request object.

        :param source: packet source object, i.e. packet capture job.
        :param columns: list Key/Value column objects.
        :param start: epoch start time in seconds.
        :param end: epoch endtime in seconds.
        :param duration: string duration of data def request.
        :param time_range: string time range of data def request.
        :param resolution string: Resoluion in seconds.
        :param str granularity: granularity value.
        """
        self.source = source
        self.columns = columns
        self.granularity = granularity
        self.resolution = resolution
        self.timefilter = TimeFilter(start=start, end=end,
                                     duration=duration, time_range=time_range)
        self._data = None

    def to_dict(self):
        data_def = dict()
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

        return data_def

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
        """Initialize an AppResponse object.

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

    def _cast_number(self, result):
        """ Check records and convert string to integer/float. If the type
        of the column is 'number' or unit is not 'none', then check if
        the column name has 'avg' in its name, if yes, then convert it to
        float, otherwise to integer.

        :param result dict: including Mata data for one data def request
            as well as the response data for the data def request.
        """

        logger.debug("Converting string in records into integer/float")

        functions = [lambda x: x] * len(result['columns'])

        columns = self.appresponse.reports.columns

        for i, col in enumerate(result['columns']):

            col_dict = columns[col]

            if 'subtype' in col_dict and col_dict['subtype'] == 'float':
                functions[i] = float

            elif (columns[col]['type'] == 'number' or
                  columns[col]['unit'] != 'none'):

                functions[i] = int

        records = []
        if 'data' in result:
            # result['data'] is a list of records
            records = [dict(zip(result['columns'],
                                map(lambda x, y: x(y), functions, rec)))
                       for rec in result['data']]

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
                self._data_defs[i].data = self._cast_number(res)
                logger.debug("Obtained {} records for the {}th data request."
                             .format(len(self._data_defs[i].data), i))

    def get_data(self, index=None):
        """Return data for the indexed data definition requests. If not set, then
        data for all data definition requests will be returned."""
        if not index:
            return [dd.data for dd in self._data_defs]

        return self._data_defs[index].data

    def delete(self):
        self._instance.delete()
        self._instance = None
        self._data_defs = []
