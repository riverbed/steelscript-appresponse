# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.common.app import Application
from steelscript.appresponse.core.appresponse import AppResponse


class AppResponseApp(Application):
    """Simple class to wrap common command line parsing"""
    def __init__(self, *args, **kwargs):
        super(AppResponseApp, self).__init__(*args, **kwargs)
        self.appresponse = None

    def add_positional_args(self):
        self.add_positional_arg('host', 'AppResponse hostname or IP address')

    def add_options(self, parser):
        super(AppResponseApp, self).add_options(parser)
        self.add_standard_options()

    def setup(self):
        super(AppResponseApp, self).setup()
        self.appresponse = AppResponse(self.options.host, auth=self.auth)
