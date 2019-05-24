# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.appresponse.core.types import ServiceClass

logger = logging.getLogger(__name__)


class SystemTimeService(ServiceClass):
    """ This class provides an interface to manage classification
    service on an AppResponse appliance.
    """

    SERVICE_NAME = 'mgmt.time'

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.servicedef = None
        self.time_configuration = None
        self.ntp_servers = None
        self.ntp_status = None

    def _bind_resources(self):

        # Init service:
        self.servicedef = self.appresponse.find_service(self.SERVICE_NAME)

        # Init resources
        self.time_configuration = self.servicedef.bind('time_configuration')
        self.ntp_servers = self.servicedef.bind('ntp_servers')
        self.ntp_status = self.servicedef.bind('ntp_status')
