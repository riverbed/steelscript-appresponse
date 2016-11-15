# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import time

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import PacketsSource


class ProbeReportService(object):

    def __init__(self, arx):
        self.arx = arx
        self.reports = arx.find_service('npm.probe.reports')
        self.instances = self.reports.bind('instances')
        self.columns = self.reports.bind('source_columns', name='packets')

    def get_column_names(self):
        resp = self.columns.execute('get')
        return [item['id'] for item in resp.data['items']]

    def create_report(self, job, columns, granularity, timefilter):
        """Create a report instance with just one data definition request."""

        report = Report(self.arx)
        report.add(job, columns, granularity, timefilter)
        report.run()
        return report

    def create_instance(self, job_data_defs):
        """Create a report instance with multiple data definition requests."""

        with self.arx.clips.create_clips(job_data_defs) as clips:

            clip_data_defs = []

            for clip, dd in zip(clips, job_data_defs):

                data_def = DataDef.build_criteria(source=PacketsSource(clip),
                                                  columns=dd.columns,
                                                  granularity=dd.granularity,
                                                  timefilter=dd.timefilter)

                clip_data_defs.append(data_def)

            config = dict(data_defs=clip_data_defs)

            instance = ReportInstance(
                self.instances.execute('create', _data=config))

            while not instance.ready:
                time.sleep(1)

            return instance

    def get_instances(self):
        resp = self.instances.execute('get')

        return [ReportInstance(self.get_instance_by_id(instance['id'])
                for instance in resp.data['items'])]

    def bulk_delete(self):
        self.instances.execute('bulk_delete')

    def get_instance_by_id(self, _id):
        resp = self.instances.execute(id=_id)
        return ReportInstance(resp)


class ReportInstance(object):
    """Main interface to  """
    def __init__(self, datarep):
        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)

    @property
    def ready(self):
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
        self.job = job
        self.columns = columns
        self.granularity = granularity
        self.timefilter = timefilter

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


class Report(object):
    """This class is the main interface to build and run a report against
    an AppResponse appliance.
    """

    def __init__(self, arx):
        """Initialize an AppResponse object.

        :param arx: the AppResponse object.
        """
        self.arx = arx
        self.data_defs = []
        self.instance = None

    def add(self, job, columns, granularity, timefilter):
        """Add one data definition request.

        :param job: packet capture job object.
        :param columns: list Key/Value column objects.
        :param str granularity: granularity value.
        :param timefilter: time filter object.
        """
        self.data_defs.append(DataDef(job, columns, granularity, timefilter))

    def run(self):
        if not self.instance:
            self.instance = self.arx.reports.create_instance(self.data_defs)

    def get_data(self):
        return self.instance.get_data()

    def delete(self):
        self.instance.delete()
        self.instance = None
