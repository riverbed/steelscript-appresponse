# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import yaml
import logging

from steelscript.appresponse.core import CommonService, ReportService, \
    CaptureJobService, ClipService, ClassificationService, SystemTimeService, \
    FileSystemService, PacketExportService
from steelscript.common.service import Service
from reschema.servicedef import ServiceDefLoadHook, ServiceDef,\
    ServiceDefManager
from steelscript.common._fs import SteelScriptDir
from sleepwalker.connection import ConnectionManager, ConnectionHook
from sleepwalker.service import ServiceManager
from steelscript.appresponse.core.types import InstanceDescriptorMixin

logger = logging.getLogger(__name__)


COMMON_SERVICE_VERSION = '1.0'


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

        # This call would call get on resource 'services' to get versions
        # which is redundant. But since it is only one time during
        # initialization, it is benign.
        svc = Service("AppResponse", host=host, auth=auth)
        return svc.conn


class AppResponse(InstanceDescriptorMixin):
    """Main interface to interact with a AppResponse appliance."""

    def __init__(self, host, auth, port=443, versions=None):
        """Initialize an AppResponse object.

        :param str host: name or IP address of the AppResponse appliance.

        :param auth: defines the authentication method and credentials
            to use to access the AppResponse. It should be an instance of
            :py:class:`UserAuth<steelscript.common.service.UserAuth>` or
            :py:class:`OAuth<steelscript.common.service.OAuth>`

        :param port: integer, port number to connect to appliance

        :param dict versions: service versions to use, keyed by the service
            name, value is a list of version strings that are required by the
            external application. If unspecified, this will use the latest
            version of each service supported by both this implementation and
            the AppResponse appliance.
        """

        self.host = host
        if port != 443:
            self.host = '{0}:{1}'.format(self.host, port)
        self.auth = auth
        self._versions = None
        self.req_versions = versions
        self._service_manager = None
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
        self.reports = ReportService(self)
        self.classification = ClassificationService(self)
        self.mgmt_time = SystemTimeService(self)
        self.fs = FileSystemService(self)
        self.export = PacketExportService(self)
        # At this point, all services have used negotiated versions
        # Except common which is using 1.0 to get supported versions
        # Now reinitialize common service with negotiated versions
        if self.versions['common'] != COMMON_SERVICE_VERSION:
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
                vers = set(self.req_versions[svc]).intersection(set(versions))
                if not vers:
                    raise KeyError(
                        "No support of service '%s' of version '%s'."
                        % (svc, ', '.join(self.req_versions[svc])))
                self._versions[svc] = max(vers)
            else:
                self._versions[svc] = max(versions)

        return self._versions

    def find_service(self, name):
        """Return a ServiceDef for a given service name."""
        if not self._versions and name == 'common':
            # Initializing appresponse, use hard coded common service version
            version = COMMON_SERVICE_VERSION
        else:
            version = self.versions[name]
        return self.service_manager.find_by_name(
            host=self.host, auth=self.auth, name=name, version=version)

    def get_info(self):
        """Get the basic info of the device."""
        return self.common.get_info()

    def get_capture_job_by_name(self, name):
        """Find a capture job by name."""
        return self.capture.get_job_by_name(name)

    def get_capture_jobs(self):
        """Get a list of all existing capture jobs."""
        return self.capture.get_jobs()

    def create_report(self, data_def_request):
        """Helper method to initiate an AppResponse report.

        :param DataDef data_def_request: Single DataDef object defining
            the report criteria.
        """
        return self.reports.create_report(data_def_request)

    def upload(self, dest_path, local_file):
        """ Upload a local file to the AppResponse 11 device.

        :param dest_path: path where local file will be stored
            at AppResponse device
        :param local_file: path to local file to be uploaded
        :return: location information if resource has been created,
            otherwise the response body (if any).
        """

        dest_dir, filename = dest_path.rsplit('/', 1)

        headers = {'Content-Disposition': filename,
                   'Content-Type': 'application/octet-stream'}

        if dest_dir[0] == '/':
            dest_dir = dest_dir[1:]

        conn = self.service_manager.connection_manager.\
            find(host=self.host, auth=self.auth)

        uri = '{}/fs/{}'.format(self.fs.servicedef.servicepath, dest_dir)

        with open(local_file) as f:
            logger.debug("Uploading file {}".format(local_file))
            resp = conn.upload(uri, f, extra_headers=headers)
            logger.debug("File {} successfully uploaded.".format(local_file))

            return resp

    def create_export(self, source, timefilter, filters):
        return self.export.create(source, timefilter, filters)

    def download(self, id_, dest_path, overwrite):

        conn = self.service_manager.connection_manager.\
            find(host=self.host, auth=self.auth)
        uri = '{}/packets/items/{}'.\
            format(self.export.servicedef.servicepath, id_)
        return conn.download(uri, dest_path, overwrite=overwrite)

    def get_file_by_id(self, id_):
        return self.fs.get_file_by_id(id_)
