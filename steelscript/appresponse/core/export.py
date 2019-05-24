# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

import time

from steelscript.appresponse.core.reports import SourceProxy
from steelscript.appresponse.core.types import ServiceClass
from steelscript.common.exceptions import RvbdHTTPException

logger = logging.getLogger(__name__)


class PacketExportService(ServiceClass):

    def __init__(self, appresponse):
        self.appresponse = appresponse
        self.exports = None

    def _bind_resources(self):

        self.servicedef = self.appresponse.find_service('npm.packet_export')

        self.exports = self.servicedef.bind('exports')

    def create(self, source, timefilter, filters):

        config = dict(path=SourceProxy(source).path,
                      start_time=str(timefilter.start),
                      end_time=str(timefilter.end),
                      filters=dict(items=filters))

        resp = self.exports.execute('create', _data=dict(config=config))

        return Export(self.appresponse, exp_id=resp.data['id'])


class Export(object):
    def __init__(self, appresponse, exp_id):
        self.appresponse = appresponse
        self.exp_id = exp_id
        self.datarep = appresponse.export.servicedef.bind('export', id=exp_id)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.delete()

    def download(self, filename, overwrite, retries=3, delay=5):
        """Download a created export.

        :param str filename: path to save downloaded file
        :param bool overwrite: true if existing file can be overwritten
        :param int retries: number of times to retry if export isn't ready
        :param int delay: time to sleep between retries

        TODO: [mzetea]: refactor this to proper recursion
        """
        try:
            self.appresponse.download(self.exp_id, filename, overwrite)
            return
        except RvbdHTTPException as e:
            # while we are waiting for the export to finish initializing,
            # retry the query checking the exception to make sure something
            # else didn't go wrong

            def not_initialized(exc):
                return ('state is not RUNNING: state UNINITIALIZED'
                        in exc.error_text)

            if not_initialized(e):
                while retries > 0:
                    logger.info('Export %s not ready, re-trying ...' %
                                self.exp_id)
                    time.sleep(delay)
                    try:
                        self.appresponse.download(self.exp_id,
                                                  filename, overwrite)
                        return
                    except RvbdHTTPException as inner_e:
                        # renamed the exception variable
                        # not to shadow the upper except
                        if not_initialized(inner_e):
                            retries = retries - 1
                            continue
                        else:
                            raise RvbdHTTPException(inner_e)
                # if we get here, the export still isn't ready
                raise RvbdHTTPException(e)
            else:
                raise RvbdHTTPException(e)

    def delete(self):
        try:
            self.datarep.execute('delete')
        except:
            pass
