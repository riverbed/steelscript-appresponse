# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.appresponse.core.types import ServiceClass, \
    AppResponseException, ResourceObject

logger = logging.getLogger(__name__)


class CaptureJobService(ServiceClass):
    """This class manages packet capture jobs."""

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.jobs = None
        self.settings = None
        self.phys_interfaces = None
        self.mifgs = None
        self._job_objs = None

    def _bind_resources(self):

        # init service
        self.servicedef = self.appresponse.find_service('npm.packet_capture')

        # init resources
        self.jobs = self.servicedef.bind('jobs')
        self.settings = self.servicedef.bind('settings')
        self.phys_interfaces = self.servicedef.bind('phys_interfaces')
        self.mifgs = self.servicedef.bind('mifgs')

    def get_jobs(self):

        if not self._job_objs:
            logger.debug("Getting info of capture jobs via resource "
                         "'jobs' link 'get'...")

            resp = self.jobs.execute('get')

            self._job_objs = [Job(data=item, servicedef=self.servicedef)
                              for item in resp.data['items']]

        return self._job_objs

    def create_job(self, config):

        logger.debug("Creating one capture job via resource "
                     "'jobs' link 'create' with data {}".format(config))
        resp = self.jobs.execute('create', _data=config)
        return Job(data=resp.data, datarep=resp)

    def delete_jobs(self):
        return self.jobs.execute('bulk_delete')

    def bulk_start(self):
        return self.jobs.execute('bulk_start')

    def bulk_stop(self):
        return self.jobs.execute('bulk_stop')

    def get_job_by_id(self, id_):
        try:
            logger.debug("Obtaining Job object with id '{}'".format(id_))
            return (j for j in self.get_jobs()
                    if j.id == id_).next()

        except StopIteration:
            raise AppResponseException(
                "No capture job found with ID '{}'".format(id_))

    def get_job_by_name(self, name):

        try:
            logger.debug("Obtaining Job object with name '{}'".format(name))
            return (j for j in self.get_jobs()
                    if j.name == name).next()

        except StopIteration:
            raise AppResponseException(
                "No capture job found with name '{}'".format(name))

    def get_mifgs(self):

        resp = self.mifgs.execute('get')

        return [MIFG(data=item, servicedef=self.servicedef)
                for item in resp.data['items']]


class Job(ResourceObject):
    """This class manages single packet capture job."""
    resource = 'job'

    def __repr__(self):
        return '<{0} {1} on MIFG {2}>'.format(
            self.__class__.__name__,
            self.name,
            self.data.config.mifg_id
        )

    @property
    def status(self):
        return self.data.state.status.state

    def set(self):
        self.datarep.execute('set')

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


class MIFG(ResourceObject):

    resource = 'mifg'
