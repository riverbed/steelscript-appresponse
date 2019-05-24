# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


class CommonService(object):

    def __init__(self, appresponse):
        self.appresponse = appresponse

        # Init service
        self.servicedef = self.appresponse.find_service('common')

        # Init resource
        self.services = self.servicedef.bind('services')
        self.info = self.servicedef.bind('info')

    def get_versions(self):
        versions_list = self.services.execute('get').data

        # Convert a list of service_id and versions into a dict
        # keyed by service_id
        versions = {}

        for service in versions_list:
            versions[service['id']] = service['versions']

        return versions

    def get_info(self):
        return self.info.execute('get').data
