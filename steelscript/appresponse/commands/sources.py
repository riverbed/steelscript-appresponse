#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
List all the sources that the given AppResponse appliance supports.
"""

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.datautils import Formatter
from steelscript.appresponse.core._constants import report_groups, \
    report_source_names, report_sources


class Command(AppResponseApp):
    help = 'List available AppResponse Sources'

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.add_option('--group', default=None,
                          help="Name of group that sources belong to, "
                               "needs to be one of the following: "
                               "'packets', 'asa', 'wta', 'db', 'uc',"
                               "'system' and 'other'. If not provided, "
                               "all sources will be shown. "
                               "The mapping of each name is as below."
                               "                                           "
                               "--------------------------------------------- "
                               "packets: Packets                      "
                               "                       "
                               "asa: Application Stream Analysis"
                               "                      "
                               "wta: Web Transaction Analysis"
                               "                           "
                               "db: DB Analysis"
                               "                                         "
                               "uc: UC Analysis"
                               "                                     "
                               "system: System Metrics"
                               "                                     "
                               "other: Other Sources "
                               "--------------------------------------------- "
                          )
        parser.add_option('--truncate', default=False, action='store_true',
                          help="truncate description column, don't wrap")
        parser.add_option('-w', '--table-width', default=120,
                          help="max char width of table output, default: 120")

    def validate_args(self):
        super(Command, self).validate_args()

        if self.options.group:
            if self.options.group not in report_groups.keys():
                self.parser.error("group needs to one of {}."
                                  .format(', '.join(report_groups.keys())))

    def main(self):
        headers = ['Name', 'Filters Supported on Metric Columns',
                   'Granularities in Seconds']

        if self.options.group:
            group_title = report_groups[self.options.group]
            source_names = report_sources[group_title]
        else:
            source_names = report_source_names

        data = []
        for name in source_names:
            s = self.appresponse.reports.sources[name]

            data.append([s['name'], str(s['filters_on_metrics']),
                         ', '.join(s['granularities'])
                         if s['granularities'] else '---'])

        Formatter.print_table(data,
                              headers,
                              padding=2,
                              max_width=int(self.options.table_width),
                              long_column=1,
                              wrap_columns=(not self.options.truncate))
