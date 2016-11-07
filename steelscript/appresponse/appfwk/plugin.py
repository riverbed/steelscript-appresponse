# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import pkg_resources

from django.apps import AppConfig

from steelscript.appfwk.apps.plugins import Plugin as AppsPlugin


class Plugin(AppsPlugin):
    title = 'SteelScript AppResponse'
    description = 'Python modules to interact AppResponse via REST API'
    version = pkg_resources.get_distribution('steelscript.appresponse').version
    author = 'Riverbed'

    enabled = True
    can_disable = True

    devices = ['devices']
    datasources = ['datasources']
    reports = ['reports']

    # List javascript/css files required by this plugin to work.
    # If a file is local to this plugin, it should be in /static/<path>.
    # Remote content can also be listed by fully qualified URL
    #
    # Example:
    #    js = ['/static/js/__plugin__.js',
    #          'http://some.website.com/cool.js']
    #    css = ['/static/css/__plugin__.css',
    #          'http://some.website.com/cool.css']
    #
    js = []
    cs = []


class SteelScriptAppConfig(AppConfig):
    name = 'steelscript.appresponse.appfwk'
    # label cannot have '.' in it
    label = 'steelscript_appresponse'
    verbose_name = 'SteelScript AppResponse'
