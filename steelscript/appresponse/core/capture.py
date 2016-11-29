# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import ServiceClass


class CaptureJobService(ServiceClass):
    """This class manages packet capture jobs."""

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.capture = None
        self.jobs = None

    def real_init(self):

        # init service
        self.capture = self.appresponse.find_service('npm.packet_capture')

        # init resources
        self.jobs = self.capture.bind('jobs')

    def get_jobs(self):
        resp = self.jobs.execute('get')

        return [self.get_job_by_id(item['id'])
                for item in resp.data['items']]

    def create_job(self, config):
        resp = self.jobs.execute('create', _data=config)
        return Job(resp)

    def delete_jobs(self):
        return self.jobs.execute('bulk_delete')

    def bulk_start(self):
        return self.jobs.execute('bulk_start')

    def bulk_stop(self):
        return self.jobs.execute('bulk_stop')

    def get_job_by_id(self, id_):
        return Job(self.capture.bind('job', id=id_))

    def get_job_by_name(self, name):
        return (j for j in self.get_jobs()
                if j.prop.config.name == name).next()


class Job(object):
    """This class manages single packet capture job."""

    def __init__(self, datarep):
        self.datarep = datarep
        data = self.datarep.execute('get').data
        self.prop = DictObject.create_from_dict(data)

    # def set(self):
    #     self.datarep.execute('set')

    def stop(self):
        self.datarep.execute('stop')

    def delete(self):
        self.datarep.execute('delete')

    def start(self):
        self.datarep.execute('start')

    def clear_packets(self):
        self.datarep.execute('clear_packets')

    def get_stats(self):
        return self.datarep.execute('get_stats').data
