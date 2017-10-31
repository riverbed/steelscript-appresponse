# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.appresponse.core.reports import SourceProxy
from steelscript.appresponse.core.types import ServiceClass

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
                      start_time=timefilter.start,
                      end_time=timefilter.end,
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

    def download(self, filename, overwrite):
        self.appresponse.download(self.exp_id, filename, overwrite)

    def delete(self):
        try:
            self.datarep.execute('delete')
        except:
            pass
