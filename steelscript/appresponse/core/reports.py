# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import time
import logging

from collections import OrderedDict

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import PacketsSource
from steelscript.common._fs import SteelScriptDir

logger = logging.getLogger(__name__)


class ProbeReportService(object):

    SOURCE_NAME = 'packets'
    SERVICE_NAME = 'npm.probe.reports'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.reports = self.appresponse.find_service(self.SERVICE_NAME)
        self.instances = self.reports.bind('instances')
        self._columns = None

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

        columns = self.reports.bind('source_columns', name=self.SOURCE_NAME)
        cols = columns.execute('get').data['items']

        # Create a ordered dict
        return OrderedDict(sorted(zip(map(lambda x: x['id'], cols), cols)))

    def get_column_names(self):
        """Return a list of column names."""

        return [col['id'] for col in self.columns]

    def create_report(self, data_def_request):
        """Create a report instance with just one data definition request."""

        report = Report(self.appresponse)
        report.add(data_def_request)
        report.run()
        return report

    def create_instance(self, data_def_requests):
        """Create a report instance with multiple data definition requests.

        Currenly only support data definition requests with capture jobs
        as the packets source. Will need to support packets source in
        formats of file, clips, etc.
        """
        with self.appresponse.clips.create_clips(data_def_requests) as clips:

            clip_data_defs = []

            for clip, dd in zip(clips, data_def_requests):

                data_def = DataDef.build_criteria(source=PacketsSource(clip),
                                                  columns=dd.columns,
                                                  granularity=dd.granularity,
                                                  timefilter=dd.timefilter)

                clip_data_defs.append(data_def)

            config = dict(data_defs=clip_data_defs)

            instance = ReportInstance(
                self.instances.execute('create', _data=config))

            logger.debug("Creating instance with data definitions %s" % config)

            while not instance.ready:
                time.sleep(1)

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
    """Main interface to  """
    def __init__(self, datarep):
        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)

    @property
    def ready(self):
        # We only checking the percentage
        # will need to check for errors
        return all([item['progress']['percent'] == 100
                    for item in self.status])

    @property
    def status(self):
        return self.datarep.execute('get_status').data

    def get_data(self):
        return self.datarep.execute('get_data').data

    def delete(self):
        return self.datarep.execute('delete')


class DataDef(object):
    """This class provides an interface to build a data definition request
    as a dict.
    """
    def __init__(self, job, columns, granularity, timefilter):
        """Initialize a data definition request object.

        :param job: packet capture job object.
        :param columns: list Key/Value column objects.
        :param str granularity: granularity value.
        :param timefilter: time filter object.
        """
        self.job = job
        self.columns = columns
        self.granularity = granularity
        self.timefilter = timefilter
        self._data = None

    @classmethod
    def build_criteria(cls, source, columns, granularity, timefilter):
        data_def = dict()
        data_def['source'] = dict(name=source.name, path=source.path)
        data_def['group_by'] = [col.name for col in columns if col.key]
        data_def['time'] = dict(start=str(timefilter.start),
                                end=str(timefilter.end),
                                granularity=granularity)
        data_def['columns'] = [col.name for col in columns]

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
        self.appresponse = appresponse
        self._data_defs = []
        self._instance = None

    def add(self, data_def_request):
        """Add one data definition request.
       """
        self._data_defs.append(data_def_request)

    def run(self):
        """Create a report instance and record the results of multiple
        data definition instances as a list of records (dictionaries).
        """
        if not self._instance:
            self._instance = self.appresponse.reports.create_instance(self.data_defs)

            results = self._instance.get_data()['data_defs']

            for i, res in enumerate(results):
                # For each data def result, build a list of dictionaries
                # from column names and a list of list of values
                self._data_defs[i].data = [dict(zip(res['columns'], rec))
                                           for rec in res['data']]

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
