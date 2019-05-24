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


class CertificateService(ServiceClass):
    """Interface to manage SSL certificates."""

    SERVICE_NAME = 'npm.https'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.certificate = None

    def _bind_resources(self):
        # Init service
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

        # Init resource
        self.certificate = self.servicedef.bind('certificate')

    def get_certificate(self):
        """Get SSL Certificate available on AppResponse appliance."""
        try:
            resp = self.certificate.execute('get')
            return Certificate(data=resp.data, datarep=resp)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('No certificate object found')

    def import_certificate(self, obj):
        """
        Import a Certificate on the AppResponse appliance.

        :param obj: Certificate object. { "pem": any, "passphrase": string }
        :return : Certificate object.
        """
        resp = self.certificate.execute('import', _data=obj)
        return Certificate(data=resp.data, datarep=resp)

    def generate_certificate(self, obj):
        """
        Generate a Certificate on the AppResponse appliance.

        :param obj: Distinguished name data object.
        {
            "common_name": string,
            "organization": string,
            "organizational_unit": string,
            "locality": string,
            "state": string,
            "country": string,
            "email": string
        }

        :return : Certificate object.
        """
        resp = self.certificate.execute('generate', _data=obj)
        return Certificate(data=resp.data, datarep=resp)


class Certificate(ResourceObject):

    resource = 'certificate'

    property_names = ['Subject', 'Fingerprint', 'Key', 'Issuer',
                      'Valid at', 'Expires at', 'PEM']

    def __str__(self):
        return '<Certificate {}/{}>'.format(self.issuer(),
                                            self.expires_at())

    def __repr__(self):
        return '<%s issuer: %s, expires at: %s>' % (self.__class__.__name__,
                                                    self.issuer(),
                                                    self.expires_at())

    def get_properties(self):
        return self.__dict__

    def get_property_values(self):
        return [
            self.subject(), self.fingerprint(),
            self.key(), self.issuer(),
            timeutils.string_to_datetime(self.valid_at()),
            timeutils.string_to_datetime(self.expires_at()),
            self.pem()
        ]

    def issuer(self):
        return self.data.get('issuer', None)

    def subject(self):
        return self.data.get('subject', None)

    def valid_at(self):
        return self.data.get('valid_at', None)

    def expires_at(self):
        return self.data.get('expires_at', None)

    def fingerprint(self):
        return self.data.get('fingerprint', None)

    def key(self):
        return self.data.get('key', None)

    def pem(self):
        return self.data.get('pem', None)
