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


class SslKeyStoreService(ServiceClass):
    """Interface to manage SSL Keys."""

    SERVICE_NAME = 'npm.ssl_key_store'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.ssl_key_store = None

    # def __str__(self):
    #     # [mzetea] - where do the id() and name() come from? seem to be undefined. ResourceObject used below has
    #     # them defined as properties... Should this class implement the 2 or inherit the RersourceObject instead of the
    #     # ServiceClass?
    #     return '<SSL Key {}/{}>'.format(self.id(), self.name())

    def _bind_resources(self):
        # Init service
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

    def get_keys(self):
        """Get SSL Keys available on AppResponse appliance."""
        # Init resource
        self.ssl_key_store = self.servicedef.bind('keys')
        resp = self.ssl_key_store.execute('get')
        ret = []
        for ssl_key in resp.data['items']:
            ret.append(SslKey(data=ssl_key, servicedef=self.servicedef))
        return ret

    def get_key_by_id(self, id_):
        """Get SSL Key with given id"""
        try:
            self.ssl_key_store = self.servicedef.bind('key', id=id_)
            resp = self.ssl_key_store.execute('get')
            return SslKey(data=resp.data, datarep=resp)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('No SSL Key found with id %s' % id_)

    def get_key_by_name(self, name_):
        """Get SSL Key with given name"""
        try:
            self.ssl_key_store = self.servicedef.bind('key', name=name_)
            resp = self.ssl_key_store.execute('get')
            return SslKey(data=resp.data, datarep=resp)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('No SSL Key found with name %s' % name_)

    def import_key(self, obj):
        """Import a SSL Key on the AppResponse appliance.

        :param obj: an SSL Key data object.
            {
                "name": string,
                "key": string,
                "passphrase": string,
                "description": string
            }

        :return : an SSL Key Store object.
        """
        self.ssl_key_store = self.servicedef.bind('keys')
        resp = self.ssl_key_store.execute('import', _data=obj)
        return SslKey(data=resp.data, datarep=resp)


class SslKey(ResourceObject):

    resource = 'key'

    property_names = ['ID', 'Name', 'Description', 'Timestamp']

    def __str__(self):
        return '<SSL_Key {}/{}>'.format(self.id(), self.name())

    def __repr__(self):
        return '<%s id: %s, name: %s>' % (self.__class__.__name__,
                                          self.id(), self.name())

    def get_properties(self):
        return self.__dict__

    def get_property_values(self):
        return [
            self.id(), self.name(), self.description(),
            timeutils.string_to_datetime(self.timestamp())
        ]

    def id(self):
        #[mzetea] the parent class defines these as property...
        return self.data.get('id', None)

    def name(self):
        return self.data.get('name', None)

    def description(self):
        return self.data.get('description', None)

    def timestamp(self):
        return self.data.get('timestamp', None)

    def delete(self):
        """Delete an SSL Key"""
        return self.datarep.execute('delete')
