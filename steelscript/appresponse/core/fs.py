# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.appresponse.core.types import ServiceClass, ResourceObject

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
                    ret.append(File(data=file,
                                    servicedef=self.servicedef))
        return ret

    def get_file_by_id(self, id_):

        logger.debug("Get file object with id {}".format(id_))
        resp = self.servicedef.bind('file', id=id_)
        return File(data=resp.data, datarep=resp)


class File(ResourceObject):

    resource = 'file'
