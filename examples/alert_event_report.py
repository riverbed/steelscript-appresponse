#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Show list of Alert Events and optionally detail of specific Alert.
"""
import optparse

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.appresponse.core.reports import DataDef, Report, SourceProxy
from steelscript.common.datautils import Formatter


class AlertEventApp(AppResponseApp):
    def add_options(self, parser):
        super(AlertEventApp, self).add_options(parser)

        group = optparse.OptionGroup(parser, 'Alert Options')

        group.add_option('--alert-detail',
                         dest='alert_detail',
                         default=None, action='store',
                         help='Display details of given Alert ID instead of '
                              'listing all Alert Events')
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, 'Time and Filter Options')
        group.add_option('--timerange', dest='timerange',
                         help='Time range to analyze, valid formats are: '
                              '"06/05/17 17:09:00 to 06/05/17 18:09:00" '
                              'or "17:09:00 to 18:09:00" '
                              'or "last 1 hour".')
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, 'Output Options')
        group.add_option('--csvfile', dest='csvfile', default=None,
                         help='CSV file to store report data')
        parser.add_option_group(group)

    def validate_args(self):
        super(AlertEventApp, self).validate_args()

        if self.options.timerange is None:
            self.parser.error('Time range must be provided.')

        if self.options.alert_detail:
            try:
                int(self.options.alert_detail)
            except ValueError:
                self.parser.error('alert-detail option must be an integer ID')

    def main(self):

        source = SourceProxy(name='alert_list')

        if self.options.alert_detail:
            # detail view
            column_names = [
                'alert.id',
                'alert.policy_id',
                'alert.policy_name',
                'alert.policy_eval_period',
                'alert.policy_type_name',
                'alert.policy_last_N',
                'alert.policy_last_M',
                'alert.severity_level',
                'alert.severity',
                'alert.start_time',
                'alert.end_time',
                'alert.duration',
                'alert.ongoing',
                'alert.low_violations_count',
                'alert.medium_violations_count',
                'alert.high_violations_count'
            ]
        else:
            # alert event listing view
            column_names = [
                'alert.id',
                'alert.policy_id',
                'alert.policy_name',
                'alert.policy_type_name',
                'alert.policy_type',
                'alert.severity_level',
                'alert.severity',
                'alert.start_time',
                'alert.end_time',
                'alert.duration',
                'alert.ongoing'
            ]

        columns = self.appresponse.get_column_objects('alert_list',
                                                      column_names)

        data_def = DataDef(source=source,
                           columns=columns,
                           granularity=60,
                           resolution=0,
                           time_range=self.options.timerange)

        if self.options.alert_detail:
            fltr = {'value': 'alert.id="{}"'.format(self.options.alert_detail)}
            data_def._filters.append(fltr)

        report = Report(self.appresponse)
        report.add(data_def)
        report.run()

        data = report.get_data()
        headers = [x.lstrip('alert.') for x in report.get_legend()]

        if not data:
            print('\nNo data found.\n')

        else:
            if self.options.csvfile:
                with open(self.options.csvfile, 'w') as f:
                    for line in Formatter.get_csv(data, headers):
                        f.write(line)
                        f.write('\n')
            else:
                Formatter.print_table(data, headers)


if __name__ == "__main__":
    app = AlertEventApp()
    app.run()
