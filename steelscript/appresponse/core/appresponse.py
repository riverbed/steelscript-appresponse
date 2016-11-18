# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import yaml
import logging

from steelscript.appresponse.core import CommonService, ProbeReportService, \
    CaptureJobService, ClipService
from steelscript.common.service import Service
from reschema.servicedef import ServiceDefLoadHook, ServiceDef,\
    ServiceDefManager
from steelscript.common._fs import SteelScriptDir
from sleepwalker.connection import ConnectionManager, ConnectionHook
from sleepwalker.service import ServiceManager

logger = logging.getLogger(__name__)

class AppResponseServiceDefLoader(ServiceDefLoadHook):
    """This class serves as the custom hook for service definition manager
    for AppResponse devices.
    """

    SERVICE_ID = '/api/{name}/{version}'

    def __init__(self, connection):
        """Initialize AppResponse object.

        :param connection: Connection object to the AppResponse appliance.
            should be an instance of
            :py:class:`Connection<steelscript.common.connection.Connection`
        """
        self.connection = connection
        self.ss_dir = SteelScriptDir('AppResponse', 'files')

    def get_fnames(self, name, version):
        """Return both the base filename and absolute file name of the
        Service Def file.

        :param str name: name of the service
        :param str version: version string

        :return: base file name and absolute file name
        """
        rel_fname = name + '-' + version + '.yml'
        abs_fname = os.path.join(self.ss_dir.basedir, rel_fname)

        return rel_fname, abs_fname

    def find_by_id(self, id_):
        """Return ServiceDef object of the given service.

        :param str id_: uri of the service definition
        """
        _, name, version = id_.rsplit('/', 2)

        rel_fname, abs_fname = self.get_fnames(name, version)

        if self.ss_dir.isfile(rel_fname):
            return ServiceDef.create_from_file(abs_fname)

        resp = self.connection.request(method='GET', path=id_)

        # Write the yaml file
        with open(abs_fname, 'w+') as f:
            yaml.safe_dump(resp.json(), f)

        return ServiceDef.create_from_file(abs_fname)

    def find_by_name(self, name, version, provider):
        """Return ServiceDef object of the given service and version."""

        assert(provider == 'riverbed')

        rel_fname, abs_fname = self.get_fnames(name, version)

        if self.ss_dir.isfile(rel_fname):
            # Found cache file
            return ServiceDef.create_from_file(abs_fname)

        service_id = self.SERVICE_ID.format(name=name, version=version)
        return self.find_by_id(service_id)


class AppResponseConnectionHook(ConnectionHook):

    def connect(self, host, auth):
        """Create a connection to the server"""
        svc = Service("AppResponse", host=host, auth=auth)
        return svc.conn


class AppResponse(object):
    """The AppResponse class is the main interface to interact with a
    AppResponse appliance. Primarity this provides an interface to
    reporting. """

    def __init__(self, host, auth, versions=None):
        """Initialize an AppResponse object.

        :param str host: name or IP address of the AppResponse appliance.

        :param auth: defines the authentication method and credentials
            to use to access the AppResponse. It should be an instance of
            :py:class:`UserAuth<steelscript.common.service.UserAuth>` or
            :py:class:`OAuth<steelscript.common.service.OAuth>`


        :param dict versions: service versions to use, keyed by the service
        name, value is a list of version strings that are required by the
        external application. If unspecified, this will use the latest
        version of each service supported by both this implementation and
        the AppResponse appliance.
        """

        self.host = host
        self.auth = auth
        self._versions = None
        self.req_versions = versions
        self._service_manager = None
        self.common_service_version = '1.0'
        self._init_services()
        logger.info("Initialized AppResponse object with %s" % self.host)

    @property
    def service_manager(self):
        """Initialize the service manager instance if it does not exist."""

        if self._service_manager is not None:
            return self._service_manager

        conn_mgr = ConnectionManager()
        conn_mgr.add_conn_hook(AppResponseConnectionHook())

        appl_conn = conn_mgr.find(host=self.host, auth=self.auth)

        svcdef_mgr = ServiceDefManager()
        svcdef_mgr.add_load_hook(AppResponseServiceDefLoader(appl_conn))

        self._service_manager = ServiceManager(servicedef_manager=svcdef_mgr,
                                               connection_manager=conn_mgr)

        return self._service_manager

    def _init_services(self):
        self.common = CommonService(self)
        self.capture = CaptureJobService(self)
        self.clips = ClipService(self)
        self.reports = ProbeReportService(self)

        # At this point, all services have used negotiated versions
        # Except common which is using 1.0 to get supported versions
        # Now reinitialize common service with negotiated versions
        self.common = CommonService(self)

    @property
    def versions(self):
        """Determine version strings for each required service."""
        if self._versions:
            return self._versions

        ar_versions = self.common.get_versions()

        self._versions = {}
        for svc, versions in ar_versions.iteritems():
            if self.req_versions and svc in self.req_versions:
                self._versions[svc] = max(set(self.req_versions[svc]).
                                          intersection(set(ar_versions[svc])))
            else:
                self._versions[svc] = max(versions)

        return self._versions

    def find_service(self, name):
        if not self._versions and name == 'common':
            # Initializing appresponse, use hard coded common service version
            version = self.common_service_version
        else:
            version = self.versions[name]
        return self.service_manager.find_by_name(
            host=self.host, auth=self.auth, name=name, version=version)

    def get_column_names(self):
        return self.reports.get_column_names()

    def get_capture_job_by_name(self, name):
        return self.capture.get_job_by_name(name)

    def get_capture_jobs(self):
        return self.capture.get_jobs()

    def create_report(self, data_def_request):
        return self.reports.create_report(data_def_request)

