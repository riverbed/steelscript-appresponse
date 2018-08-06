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
        parser.add_option('--source', default='packets',
                          help="name of source to which the columns belong")

    def main(self):
        headers = ['ID', 'Description', 'Type', 'Metric', 'Key/Value']
        cols = self.appresponse.reports.sources[self.options.source]['columns']

        data = []
        for c in cols.values():
            v = 'Key' if 'grouped_by' in c and c['grouped_by'] else 'Value'
            metric = c['metric'] if 'metric' in c else '---'
            data.append((c['id'], c['description'], c['type'],
                         metric, v))

        data.sort()
        Formatter.print_table(data,
                              headers,
                              padding=2,
                              max_width=int(self.options.table_width),
                              long_column=1,
                              wrap_columns=(not self.options.truncate))
