# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import pkg_resources

from django.apps import AppConfig

from steelscript.appfwk.apps.plugins import Plugin as AppsPlugin


class AppResponsePlugin(AppsPlugin):
    title = 'SteelScript AppResponse'
    description = 'Python modules to interact AppResponse via REST API'
    version = pkg_resources.get_distribution('steelscript.appresponse').version
    author = 'Riverbed Technology'

    enabled = True
    can_disable = True

    devices = ['devices']
    datasources = ['datasources']
    reports = ['reports']


class SteelScriptAppConfig(AppConfig):
    name = 'steelscript.appresponse.appfwk'
    # label cannot have '.' in it
    label = 'steelscript_appresponse'
    verbose_name = 'SteelScript AppResponse'
