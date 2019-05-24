# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging
import os

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
        self._file_objs = None

    def _bind_resources(self):

        # Init service
        self.servicedef = self.appresponse.find_service('npm.filesystem')

        # Init resource
        self.filesystem = self.servicedef.bind('filesystem')

    def get_files(self, force=False):
        """Get all files on filesystem across all directories."""

        if not self._file_objs or force:
            resp = self.filesystem.execute('get')

            def find_files(data, files=None):
                """Recursive function which traverses directories."""
                if files is None:
                    files = []

                if list(data.keys()) == ['items']:
                    data = data['items']

                for element in data:
                    # [mzetea] - rather than searching in a list
                    # (log(n)) we can try dict access O(1)
                    # dirs = element.get('dirs')
                    # if dirs is not None: find_files(dirs, files=files)
                    # same goes below unless it's not a dict we expect...
                    if 'dirs' in element and element['dirs']:
                        find_files(element['dirs'], files=files)

                    if 'files' in element and element['files']:
                        filelist = [File(data=f, servicedef=self.servicedef)
                                    for f in element['files']['items']]
                        files.extend(filelist)
                return files

            self._file_objs = find_files(resp.data)

        return self._file_objs

    def get_file_by_id(self, id_):

        logger.debug("Get file object with id {}".format(id_))
        resp = self.servicedef.bind('file', id=id_)
        return File(data=resp.data, datarep=resp)

    def create_dir(self, fullpath):
        """Create directory on device at `fullpath`"""
        # too hard to figure out how to do this with sleepwalker natively
        # just hit the endpoint with custom headers directly

        # The API requires the directory name and the directory
        # parent dir as two separated parameters
        src_dir, dir_name = os.path.split(fullpath)

        # Remove leading and trailing white space from the new resource name
        dir_name = dir_name.strip()

        if (src_dir is not None and dir_name is not None and
                len(src_dir) > 0 and len(dir_name) > 0):

            headers = {
                'Content-Disposition': dir_name,
                'Content-Type': 'application/x-shark-directory'
            }
            self.servicedef.connection.request(
                'POST',
                '/api/npm.filesystem/1.0/fs/{}'.format(src_dir),
                body=None, extra_headers=headers
            )

            return self.get_file_by_id(fullpath)


class File(ResourceObject):

    resource = 'file'

    def __str__(self):
        return '<File {}:{}>'.format(self.type, self.path)

    def __repr__(self):
        return '<File {}:{}>'.format(self.type, self.path)

    @property
    def type(self):
        return self.data.type

    @property
    def path(self):
        return self.data.id

    def is_msa(self):
        return self.type == 'MULTISEGMENT_FILE'

    def delete(self):
        self.datarep.delete()
