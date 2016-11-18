# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


class CommonService(object):

    def __init__(self, appresponse):
        service = appresponse.find_service('common')
        self.info = service.bind('info')
        self.ping = service.bind('ping')
        self.services = service.bind('services')
        self.auth_info = service.bind('auth_info')

    def get_versions(self):
        versions_list = self.services.execute('get').data

        # Convert a list of service_id and versions into a dict
        # keyed by service_id
        versions = {}

        for service in versions_list:
            versions[service['id']] = service['versions']

        return versions
