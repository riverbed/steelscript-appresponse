# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.appresponse.core.types import ServiceClass, \
    AppResponseException, ResourceObject
from steelscript.common.exceptions import RvbdHTTPException

logger = logging.getLogger(__name__)


class CaptureJobService(ServiceClass):
    """This class manages packet capture jobs."""

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.jobs = None
        self.settings = None
        self.phys_interfaces = None
        self.vifgs = None
        self._job_objs = None

    def _bind_resources(self):

        # init service
        self.servicedef = self.appresponse.find_service('npm.packet_capture')

        # init resources
        self.jobs = self.servicedef.bind('jobs')
        self.settings = self.servicedef.bind('settings')
        self.phys_interfaces = self.servicedef.bind('phys_interfaces')
        self.vifgs = self.servicedef.bind('vifgs')

    def get_jobs(self, force=False):

        if not self._job_objs or force:
            logger.debug("Getting info of capture jobs via resource "
                         "'jobs' link 'get'...")

            resp = self.jobs.execute('get')

            self._job_objs = [Job(data=item, servicedef=self.servicedef)
                              for item in resp.data['items']]

        return self._job_objs

    def create_job(self, config):
        full_config = {'config': config}

        logger.debug("Creating one capture job via resource "
                     "'jobs' link 'create' with data {}".format(full_config))
        resp = self.jobs.execute('create', _data=full_config)
        self.get_jobs(force=True)
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

    def get_vifgs(self):

        resp = self.vifgs.execute('get')

        return [VIFG(data=item, servicedef=self.servicedef)
                for item in resp.data['items']]


class Job(ResourceObject):
    """This class manages single packet capture job."""
    resource = 'job'

    def __repr__(self):
        return '<{0} {1} on VIFGs {2}>'.format(
            self.__class__.__name__,
            self.name,
            self.data.config.vifgs
        )

    @property
    def status(self):
        return self.data.state.status.state

    def stop(self):
        self.datarep.data['config']['enabled'] = False
        self.datarep.push()

    def delete(self):
        self.datarep.execute('delete')

    def start(self):
        self.datarep.data['config']['enabled'] = True
        try:
            self.datarep.push()
        except RvbdHTTPException as e:
            if e.error_text == 'NPM_JOB_RUNNING':
                msg = 'Job already started'
                logger.error(msg)
                print(msg)
            else:
                raise e

    def clear_packets(self):
        self.datarep.execute('clear_packets')

    def get_stats(self):
        return self.data.state.stats


class VIFG(ResourceObject):

    resource = 'vifg'

    def __repr__(self):
        return '<VIFG {0}/{1} enabled: {2}>'.format(
            self.data.id,
            self.data.config.name,
            self.data.config.enabled
        )
