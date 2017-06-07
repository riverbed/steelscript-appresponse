#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Ran a report against sources of 'packets' (capture job, clips, files) on an
AppResponse 11 appliance.
"""

import pandas

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.appresponse.core.types import Key, Value
from steelscript.appresponse.core.reports import DataDef, Report


class PacketsReportApp(AppResponseApp):
    def add_options(self, parser):
        super(PacketsReportApp, self).add_options(parser)
        parser.add_option('--sourcetype',
                          dest='sourcetype', default=None,
                          help='Type of data source to run report against, '
                               'i.e. file, clip or job')
        parser.add_option('--sourceid',
                          dest='sourceid', default=None,
                          help='ID of the source to run report against')
        parser.add_option('--keycolumns',
                          dest='keycolumns',
                          default=None,
                          help='List of key column names separated by comma')
        parser.add_option('--valuecolumns', dest='valuecolumns',
                          default=None,
                          help='List of value column names separated by comma'
                          )
        parser.add_option('--duration', dest='duration',
                          help='Time range to analyze, valid formats are: '
                               '"06/05/17 17:09:00 to 06/05/17 18:09:00" '
                               'or "17:09:00 to 18:09:00" '
                               'or "last 1 hour".' )
        parser.add_option('--granularity', dest='granularity',
                          help='The amount of time in seconds for which the '
                               'data source computes a summary of the '
                               'metrics it received.')
        parser.add_option('--resolution', dest='resolution',
                          help='Additional granularity in seconds to tell the '
                               'data source to aggregate further.')
        parser.add_option('--csvfile', dest='csvfile', default=None,
                          help='CSV file to store report data')

    def validate_args(self):
        super(PacketsReportApp, self).validate_args()

        if self.options.sourcetype not in ['file', 'clip', 'job']:
            self.parser.error("Source type should be set as "
                              "one of 'file', 'clip', 'job'")

        if self.options.sourceid is None:
            self.parser.error("Name of the source must be provided")

        if self.options.keycolumns is None:
            self.parser.error("Key column names must be provided")

        if self.options.valuecolumns is None:
            self.parser.error("Value column names must be provided")

        if self.options.duration is None and \
                self.options.sourcetype == 'job':
            self.parser.error("Duration must be provided for source type job")

    def main(self):
        if self.options.sourcetype == 'file':
            source = self.appresponse.fs.get_file_by_id(self.options.sourceid)
        elif self.options.sourcetype == 'job':
            source = self.appresponse.capture.\
                get_job_by_name(self.options.sourceid)
        else:
            source = self.appresponse.clips.\
                get_clip_by_id(self.options.sourceid)

        columns = []
        for col in self.options.keycolumns.split(','):
            columns.append(Key(col))

        for col in self.options.valuecolumns.split(','):
            columns.append(Value(col))

        data_def = DataDef(source=source, columns=columns,
                           granularity=self.options.granularity,
                           resolution=self.options.resolution,
                           duration=self.options.duration)

        report = Report(self.appresponse)
        report.add(data_def)
        report.run()

        df = pandas.DataFrame(report.get_data(0)[0])

        if self.options.csvfile:
            df.to_csv(self.options.csvfile)
        else:
            print(df.to_string())


if __name__ == "__main__":
    app = PacketsReportApp()
    app.run()
