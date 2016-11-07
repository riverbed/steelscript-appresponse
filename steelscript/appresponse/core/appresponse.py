import os
import yaml

from steelscript.appresponse.core.common import CommonService
from steelscript.common.service import UserAuth, Service
from reschema.servicedef import ServiceDefLoadHook, ServiceDef, ServiceDefManager
from steelscript.common._fs import SteelScriptDir
from sleepwalker.connection import ConnectionManager, ConnectionHook
from sleepwalker.service import ServiceManager

#SERVICE_ID = 'http://redocs.lab.nbttech.com:8000/docs/141/{name}/{version}/service.yml'
host = 'https://680-olaf88.lab.nbttech.com'

auth = UserAuth(username='admin', password='admin')

class ARXServiceDefLoader(ServiceDefLoadHook):
    """This class serves as the custom hook for service manager."""

    SERVICE_ID = '/api/{name}/{version}'

    def __init__(self, host, auth):

        self.connection = Service('ARX', host, auth).connection
        self.ss_dir = SteelScriptDir('AppResponse', 'files')

    def get_fnames(self, name, version):

        rel_fname = name + '-' + version + '.yml'
        abs_fname = os.path.join(self.ss_dir.basedir, rel_fname)

        return rel_fname, abs_fname

    def find_by_id(self, id_):

        _, name, version = id_.split('/')

        rel_fname, abs_fname = self.get_fnames(name, version)

        if self.ss_dir.isfile(rel_fname):
            return ServiceDef.create_from_file(abs_fname)

        resp = self.connection.request(method='GET', path=id_)

        # Write the yaml file
        with open(abs_fname, 'w+') as f:
            yaml.safe_dump(resp.json(), f)

        return ServiceDef.ServiceDef.create_from_file(abs_fname)

    def find_by_name(self, name, version, provider):

        assert(provider == 'riverbed')

        rel_fname, abs_fname = self.get_fnames(name, version)

        if self.ss_dir.isfile(rel_fname):
            # Found cache file
            return ServiceDef.create_from_file(abs_fname)

        service_id = self.SERVICE_ID.format(name=name, version=version)
        return self.find_by_id(service_id)


class ARXConnectionHook(ConnectionHook):

    def connect(self, host, auth):
        """Create a connection to the server"""
        svc = Service("ARX", host=host, auth=auth)
        return svc.conn


class ARXServiceManager(ServiceManager):

    def __init__(self, host, auth):

        svcdef_mgr = ServiceDef.ServiceDefManager()
        svcdef_mgr.add_load_hook(ARXServiceDefLoader())

        conn_mgr = ConnectionManager()
        conn_mgr.add_conn_hook(ARXServiceConnectionHook())

        super(ARXServiceManager, self).__init__(svcdef_mgr, conn_mgr)


class AppResponse():
    
    def __init__(self, host, auth, versions=None):

        self.host = host
        self.auth = auth
        self._versions = None
        self.req_versions = versions
        self._service_manager = None
        self._init_services()

    @property
    def service_manager(self):

        if self._service_manager is not None:
            return self._service_manager

        conn_mgr = ConnectionManager()
        conn_mgr.add_conn_hook(ARXConnectionHook())

        svcdef_mgr = ServiceDefManager()
        svcdef_mgr.add_load_hook(ARXServiceDefLoader(host, auth))

        self._service_manager = ServiceManager(servicedef_manager=svcdef_mgr,
                                               connnection_manager=conn_mgr)

        return self._service_manager

    def _init_services(self):
        self.common = CommonService(self)

        # 1st step try unauthenticated ping

        # 2nd step try authenticated call under common

        self.common = CommonService(self)
        #self.packets = PacketsService(self)
        #self.clips = get_service(name='npm.clips')
        #self.fs = get_service(name='npm.filesystem')
        #self.reports = ProbeReportService(host, auth, name, versions)
        #self.search = get_service(name='npm.search')

    def negoniate(self, versions):
        self.common.get_versions()

    @property
    def versions(self):
        if self._versions:
            return self._versions

        arx_versions = self.common.get_versions()

        self._versions = {}
        for svc, versions in arx_versions.iteritems():
            if svc in self.req_versions:
                self._versions[svc] = max(set(self.req_versions[svc]).\
                                          intersection(set(arx_versions[svc])))
            else:
                self._versions[svc] = max(versions)

        return self._versions

    def get_service(self, name):
        version = self.versions[name]
        return self.service_manager.find_by_name(name, version)

"""
    def create_report(self):
        return self.reports.create_report()

    def get_instance_status(self):
        return self.reports.get_instance_status()

    def create_job(self):
        self.packets.create_job()

    def get_jobs(self):
        return self.packets.get_jobs()

    def delete_jobs(self):
        return self.packets.delete_jobs()

    def start_job(self):
        self.packets.start_job()

    def get_job_status(self):
        self.packets.get_job_status()

# class DataDef(DictObject):
#
#     @classmethod
#     def create(reference, source_name, source_path, group_by, time, columns):
#         data_def = ...
#         return create_from_dict(data_def)
#

#class AppResponseService(Sleepwalker.Service):

    #@classmethod
    #def create(host, name, auth, version='1.0'):
    #    return svcmgr.find_by_name(host=host, name=name, version='1.0', auth=auth)


#    def execute(self, resource, link, data):
#        data_rep = self.bind(resource)
#        return data_rep.execute(link, data)

"""

