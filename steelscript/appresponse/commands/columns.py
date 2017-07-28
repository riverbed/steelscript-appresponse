#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
List all the key and value columns that the given AppResponse appliance
supports.
"""

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.datautils import Formatter


class Command(AppResponseApp):
    help = 'List available AppResponse Columns'

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.add_option('--truncate', default=False, action='store_true',
                          help="truncate description column, don't wrap")
        parser.add_option('-w', '--table-width', default=120,
                          help="max char width of table output, default: 120")

    def main(self):
        headers = ['ID', 'Description', 'Type']
        data = [(c['id'], c['description'], c['type'])
                for c in self.appresponse.reports.get_columns().values()]
        data.sort()
        Formatter.print_table(data,
                              headers,
                              padding=2,
                              max_width=int(self.options.table_width),
                              long_column=1,
                              wrap_columns=(not self.options.truncate))
