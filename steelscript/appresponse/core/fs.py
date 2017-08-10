# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common.datastructures import DictObject
from steelscript.appresponse.core.types import ServiceClass

logger = logging.getLogger(__name__)


class FileSystemService(ServiceClass):
    """This class provides an interface to manage directories and files on
    an AppResponse appliance.
    """

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.filesystem = None

    def _bind_resources(self):

        # Init service
        self.servicedef = self.appresponse.find_service('npm.filesystem')

        # Init resource
        self.filesystem = self.servicedef.bind('filesystem')

    def get_files(self):

        resp = self.filesystem.execute('get')

        ret = []

        for directory in resp.data['items']:
            if 'items' in directory['files']:
                for file in directory['files']['items']:
                    ret.append(File.create(data=file,
                                           servicedef=self.servicedef))
        return ret

    def get_file_by_id(self, id_):

        logger.debug("Get file object with id {}".format(id_))
        resp = self.servicedef.bind('file', id=id_)
        return File.create(data=resp.data, datarep=resp)


class File(DictObject):

    @classmethod
    def create(cls, data, servicedef=None, datarep=None):
        logger.debug('Creating File object with data {}'.format(data))
        obj = DictObject.create_from_dict(data)
        if not datarep:
            obj.datarep = servicedef.bind('file', id=obj.id)
        else:
            obj.datarep = datarep
        return File(obj)
