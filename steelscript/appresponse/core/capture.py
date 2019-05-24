# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.appresponse.core.types import ServiceClass, \
    AppResponseException, ResourceObject
from steelscript.common.api_helpers import APIVersion
from steelscript.common.datastructures import DictObject
from steelscript.common.exceptions import RvbdHTTPException

logger = logging.getLogger(__name__)


def CaptureJobService(appresponse):
    """Factory to determine appropriate CaptureJob class"""

    version = APIVersion(appresponse.versions['npm.packet_capture'])
    if version < APIVersion('2.0'):
        return PacketCapture10(appresponse)
    else:
        return PacketCapture20(appresponse)


class CaptureServiceBase(ServiceClass):
    """This class manages packet capture jobs."""

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.jobs = None
        self.settings = None
        self.interfaces = None
        self._job_objs = None
        self._interface_objs = None

    def _bind_resources(self):

        # init service
        self.servicedef = self.appresponse.find_service('npm.packet_capture')

        # init resources
        self.jobs = self.servicedef.bind('jobs')
        self.settings = self.servicedef.bind('settings')
        self.interfaces = self.servicedef.bind('phys_interfaces')

    def get_interfaces(self, force=False):

        if not self._interface_objs or force:
            logger.debug("Getting interfaces via resource "
                         "'phys_interfaces' link 'get'...")

            resp = self.interfaces.execute('get')

            self._interface_objs = [Interface(data=item,
                                              servicedef=self.servicedef)
                                    for item in resp.data['items']]

        return self._interface_objs

    def get_jobs(self, force=False):

        if not self._job_objs or force:
            logger.debug("Getting capture jobs via resource "
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
            return next((j for j in self.get_jobs() if j.id == id_))
        except StopIteration:
            raise AppResponseException(
                "No capture job found with ID '{}'".format(id_))

    def get_job_by_name(self, name):

        try:
            logger.debug("Obtaining Job object with name '{}'".format(name))
            return next((j for j in self.get_jobs() if j.name == name))
        except StopIteration:
            raise AppResponseException(
                "No capture job found with name '{}'".format(name))


class PacketCapture10(CaptureServiceBase):

    def __init__(self, appresponse):
        super(PacketCapture10, self).__init__(appresponse)
        self.mifgs = None

    def _bind_resources(self):
        super(PacketCapture10, self)._bind_resources()
        self.mifgs = self.servicedef.bind('mifgs')

    def get_mifgs(self):
        resp = self.mifgs.execute('get')

        return [MIFG(data=item, servicedef=self.servicedef)
                for item in resp.data['items']]


class PacketCapture20(CaptureServiceBase):
    def __init__(self, appresponse):
        super(PacketCapture20, self).__init__(appresponse)
        self.vifgs = None

    def _bind_resources(self):
        super(PacketCapture20, self)._bind_resources()
        self.vifgs = self.servicedef.bind('vifgs')

    def get_vifgs(self):
        resp = self.vifgs.execute('get')

        return [VIFG(data=item, servicedef=self.servicedef)
                for item in resp.data['items']]


class Interface(ResourceObject):
    """This class manages single packet capture job."""
    resource = 'phys_interface'

    def __init__(self, data, servicedef=None, datarep=None):
        # Override super class to use name instead of id
        logger.debug('Initialized {} object with data {}'
                     .format(self.__class__.__name__, data))
        self.data = DictObject.create_from_dict(data)
        if not datarep:
            self.datarep = servicedef.bind(self.resource,
                                           name=self.data.name)
        else:
            self.datarep = datarep

    def __repr__(self):
        return '<Interface {}/{}>'.format(self.name, self.status)

    @property
    def name(self):
        return self.data.name

    @property
    def status(self):
        return self.data.state.status

    @property
    def stats(self):
        """Show packets seen and dropped"""
        return self.data.state.stats


class Job(ResourceObject):
    """This class manages single packet capture job."""
    resource = 'job'

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self._version = self.datarep.service.servicedef.version

    def __repr__(self):
        if self._version == '1.0':
            return '<{0} {1} on MIFG {2}>'.format(
                self.__class__.__name__,
                self.name,
                self.data.config.mifg_id
            )
        else:
            return '<{0} {1} on VIFGs {2}>'.format(
                self.__class__.__name__,
                self.name,
                self.data.config.vifgs
            )

    @property
    def status(self):
        return self.data.state.status.state

    def stop(self):
        if self._version == '1.0':
            self.datarep.execute('stop')
        else:
            self.datarep.data['config']['enabled'] = False
            self.datarep.push()

    def delete(self):
        self.datarep.execute('delete')

    def start(self):
        try:
            if self._version == '1.0':
                self.datarep.execute('start')
            else:
                self.datarep.data['config']['enabled'] = True
                self.datarep.push()
        except RvbdHTTPException as e:
            if e.error_text in ('NPM_JOB_RUNNING',
                                'NPM_JOB_ALREADY_RUNNING'):
                msg = 'Job already started'
                logger.error(msg)
                print(msg)
            else:
                raise e

    def clear_packets(self):
        self.datarep.execute('clear_packets')

    def get_stats(self):
        if self._version == '1.0':
            return self.datarep.execute('get_stats').data
        else:
            return self.data.state.stats


class MIFG(ResourceObject):

    resource = 'mifg'

    def __repr__(self):
        return '<MIFG {0}/{1}>'.format(self.data.id, self.data.config.name)


class VIFG(ResourceObject):

    resource = 'vifg'

    def __repr__(self):
        return '<VIFG {0}/{1} enabled: {2}>'.format(
            self.data.id,
            self.data.config.name,
            self.data.config.enabled
        )
