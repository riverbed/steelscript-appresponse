

class CommonService(object):

    def __init__(self, arx):
        service = arx.get_service('common')
        self.info = service.bind('info')
        self.ping = service.bind('ping')
        self.services = service.bind('services')
        self.auth_info = service.bind('auth_info')
        self.token = service.bind('token')
        self.session_auth = service.bind('session_auth')

    def get_versions(self):
        versions_list = self.services.execute('get').data

        # Convert a list of service_id and versions into a dict
        # keyed by service_id
        versions = {}

        for service in versions_list:
            versions[service['id']] = service['versions']

        return versions


