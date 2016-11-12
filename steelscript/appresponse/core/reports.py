# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import time

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.capture import Job
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

    def create_report(self, source, columns, granularity, timefilter):

        # Check the source, if it is a capture job, create a trace clip
        # and use the clip as the source instead

        if isinstance(source.packets_obj, Job):

            with self.arx.create_clip(source.packets_obj, timefilter) as clip:

                source = PacketsSource(clip)
                return self.create_non_job_report(source, columns, granularity, timefilter)

        else:

            return self.create_non_job_report(source, columns, granularity, timefilter)

    def create_non_job_report(self, source, columns, granularity, timefilter):

        data_def = DataDef.build_criteria(source, columns, granularity, timefilter)

        instance = self.create_instance([data_def])

        while not instance.ready:
            time.sleep(1)

        return instance

    def create_instance(self, data_defs):

        config = {'data_defs': data_defs}
        resp = self.instances.execute('create', _data=config)
        return ReportInstance(resp, self.reports)

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
    """Instance class should """
    def __init__(self, datarep, reports):
        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)

    @property
    def ready(self):
        return all([item['progress']['percent'] == 100 for item in self.status])

    @property
    def status(self):
        return self.datarep.execute('get_status').data

    def get_data(self):
        return self.datarep.execute('get_data').data

    def delete(self):
        return self.datarep.execute('delete')


class DataDef(object):

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

"""
class Report(object):
    def __init__(self, arx):
        self.arx = arx
        self.data_defs = []
        self.instance = None

    def add(self, source, columns, granularity, timefilter):
        if isinstance(source.packets_obj, Job):


        self.data_defs['data_defs'].append(build_data_def(**kwargs))

    def run(self):
        datarep = self.appresponse.reports.create_instance(self.data_defs)
        self.instance = ReportInstance(datarep)

    def get_data(self):
        return self.instance.get_data()


#arx = AppResponse()
#report = arx.create_view(**kwargs)
#report.get_data()

arx = AppResponse()
report = Report(arx)
report.add(**kwargs)
report.add(**kwargs)
report.run()
report.get_data()
"""