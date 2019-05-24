# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common import timeutils
from steelscript.appresponse.core.types import ServiceClass, ResourceObject
from steelscript.common.exceptions import RvbdHTTPException

logger = logging.getLogger(__name__)


class SystemUpdateService(ServiceClass):
    """Interface to manage system update"""

    SERVICE_NAME = 'npm.system_update'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.system_update = None

    def _bind_resources(self):
        # Init service
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

    def get_images(self):
        """Get Update images available on AppResponse appliance"""
        # Init resource
        self.system_update = self.servicedef.bind('images')
        resp = self.system_update.execute('get')
        ret = []
        for image in resp.data['items']:
            ret.append(Image(data=image, servicedef=self.servicedef))
        return ret

    def get_image_by_id(self, id_):
        """Get Update image with given id"""
        try:
            return next(j for j in self.get_images()
                        if j.id() == id_)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('No image found with id %s' % id_)

    def upload_image(self, path):
        """Upload an update image on AppResponse appliance.
        :param path: Provide a path to local image
        :return : Returns a response object.
        """
        try:
            # Init resource
            uri = self.servicedef.bind('images').uri + '/upload'
            conn = (self.appresponse
                        .service_manager
                        .connection_manager
                        .find(host=self.appresponse.host,
                              auth=self.appresponse.auth))
            with open(path, mode='rb') as fd:
                resp = conn.upload(uri, fd)
            fd.close()
            return resp
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to upload an update image.')

    def fetch_image(self, url):
        """Fetch an update image on AppResponse appliance.

        :param url: Provide a request body with the following structure:
            {
                "url": string
            }
        :return : Returns an image data object.
        """
        try:
            # Init resource
            self.system_update = self.servicedef.bind('images')
            data = dict(url=url)
            resp = self.system_update.execute('fetch', _data=data)
            return Image(data=resp.data, datarep=resp)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to fetch an update image.')

    def get_update(self):
        """Get an update object on AppResponse appliance."""
        try:
            # Init resource
            self.system_update = self.servicedef.bind('update')
            resp = self.system_update.execute('get')
            return Update(data=resp.data, datarep=resp)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('No update found')


class Image(ResourceObject):

    resource = 'image'

    property_names = ['ID', 'State', 'State Description',
                      'Version', 'Progress', 'Checksum']

    def __str__(self):
        return '<Image {}/{}>'.format(self.id(), self.state())

    def __repr__(self):
        return '<%s id: %s, state: %s>' % (self.__class__.__name__,
                                           self.id(), self.state())

    def get_properties(self):
        return self.__dict__

    def get_property_values(self):
        return [
            self.id(), self.state(), self.state_description(),
            self.version(), self.progress(), self.checksum()
        ]

    def id(self):
        return self.data.get('id', None)

    def state(self):
        return self.data.get('state', None)

    def state_description(self):
        return self.data.get('state_description', None)

    def version(self):
        return self.data.get('version', None)

    def progress(self):
        return self.data.get('progress', None)

    def checksum(self):
        return self.data.get('checksum', None)

    def delete(self):
        """Delete an update image"""
        return self.datarep.execute('delete')


class Update(ResourceObject):

    resource = 'update'

    property_names = ['State', 'State Description',
                      'Last State Time', 'Target Version',
                      'Update History']

    def __str__(self):
        return '<Update {}>'.format(self.state())

    def __repr__(self):
        return '<%s state: %s>' % (self.__class__.__name__,
                                   self.state())

    def get_properties(self):
        return self.__dict__

    def get_property_values(self):
        return [
            self.state(), self.state_description(),
            timeutils.string_to_datetime(self.last_state_time()),
            self.target_version(), self.get_history_details()
        ]

    def get_history_details(self):
        history = self.update_history()
        f_history = ""
        for i in range(len(history)):
            f_time = "\nTime: " + str(timeutils.string_to_datetime(
                history[i].time))
            f_version = "Version: " + history[i].version + "\n"
            f_history += f_time + " " + f_version
        return f_history

    def state(self):
        return self.data.get('state', None)

    def state_description(self):
        return self.data.get('state_description', None)

    def last_state_time(self):
        return self.data.get('last_state_time', None)

    def target_version(self):
        return self.data.get('target_version', None)

    def update_history(self):
        return self.data.get('update_history', None)

    def initialize(self):
        """Initialize the update process"""
        return self.datarep.execute('init')

    def start(self):
        """Start the update process"""
        return self.datarep.execute('start')

    def reset(self):
        """Uninitialize the update process"""
        return self.datarep.execute('reset')
