#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Run a report against sources of 'packets' (capture job, clips, files) on an
AppResponse 11 appliance.
"""
import optparse

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.appresponse.core.types import Key, Value, TrafficFilter
from steelscript.appresponse.core.reports import DataDef, Report, SourceProxy
from steelscript.common.datautils import Formatter


class GeneralReportApp(AppResponseApp):
    def add_options(self, parser):
        super(GeneralReportApp, self).add_options(parser)

        group = optparse.OptionGroup(parser, "Source Options")

        group.add_option('--showsources',
                         dest='showsources',
                         default=False, action='store_true',
                         help='Display the set of source names')
        group.add_option('--sourcename',
                         dest='sourcename', default=None,
                         help='Name of source to run report against, '
                              'i.e. aggregates, flow_tcp, etc.')
        group.add_option('--keycolumns',
                         dest='keycolumns',
                         default=None,
                         help='List of key column names separated by comma')
        group.add_option('--valuecolumns', dest='valuecolumns',
                         default=None,
                         help='List of value column names separated by comma'
                         )
        group.add_option('--topbycolumns', dest='topbycolumns',
                         default=None,
                         help='List of column names to be topped by seperated by commas'
                         )
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, "Time and Filter Options")
        group.add_option('--timerange', dest='timerange',
                         help='Time range to analyze, valid formats are: '
                              '"06/05/17 17:09:00 to 06/05/17 18:09:00" '
                              'or "17:09:00 to 18:09:00" '
                              'or "last 1 hour".')
        group.add_option('--granularity', dest='granularity',
                         help='The amount of time in seconds for which the '
                              'data source computes a summary of the '
                              'metrics it received.')
        group.add_option('--resolution', dest='resolution',
                         help='Additional granularity in seconds to tell the '
                              'data source to aggregate further.')
        group.add_option('--filterexpr', dest='filterexpr',
                         help="steelfilter traffic filter expression. "
                              "bpf and wireshark filters are not supported "
                              "for non-packets sources.")
        group.add_option('--limit', dest='limit',
                         help='The limit on the number of records to return.')
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, "Output Options")
        group.add_option('--csvfile', dest='csvfile', default=None,
                         help='CSV file to store report data')
        parser.add_option_group(group)

    def validate_args(self):
        super(GeneralReportApp, self).validate_args()

        if self.options.showsources:
            return

        if self.options.sourcename is None:
            self.parser.error("Source name must be provided.")

        if self.options.valuecolumns is None:
            self.parser.error("Value column names must be provided.")

        if self.options.timerange is None:
            self.parser.error("Time range must be provided.")

    def main(self):

        if self.options.showsources:
            svcdef = self.appresponse.find_service('npm.reports')
            dr = svcdef.bind('source_names')
            source_names = dr.execute('get').data
            print('\n'.join(source_names))
            return

        source = SourceProxy(name=self.options.sourcename)

        columns = []
        headers = []
        if self.options.keycolumns:
            for col in self.options.keycolumns.split(','):
                columns.append(Key(col))
                headers.append(col)

        for col in self.options.valuecolumns.split(','):
            columns.append(Value(col))
            headers.append(col)

        topbycolumns = []
        
        if self.options.topbycolumns:
            for col in self.options.topbycolumns.split(','):
                topbycolumns.append(Key(col))

        data_def = DataDef(source=source,
                           columns=columns,
                           granularity=self.options.granularity,
                           resolution=self.options.resolution,
                           time_range=self.options.timerange,
                           limit=self.options.limit,
                           topbycolumns=topbycolumns)

        if self.options.filterexpr:
            data_def.add_filter(TrafficFilter(type_='steelfilter',
                                              value=self.options.filterexpr))

        report = Report(self.appresponse)
        report.add(data_def)
        report.run()

        data = report.get_data()
        headers = report.get_legend()

        report.delete()

        if self.options.csvfile:
            with open(self.options.csvfile, 'w') as f:
                for line in Formatter.get_csv(data, headers):
                    f.write(line)
                    f.write('\n')
        else:
            Formatter.print_csv(data, headers)


if __name__ == "__main__":
    app = GeneralReportApp()
    app.run()
    