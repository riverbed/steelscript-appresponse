#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import print_function

"""
Run a report against sources of 'packets' (capture job, clips, files) on an
AppResponse 11 appliance.
"""
import time
import datetime
import optparse

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.appresponse.core.types import Key, Value, TrafficFilter
from steelscript.appresponse.core.reports import DataDef, SourceProxy
from steelscript.common.datautils import Formatter


class LiveReportApp(AppResponseApp):
    def add_options(self, parser):
        super(LiveReportApp, self).add_options(parser)

        group = optparse.OptionGroup(parser, "Source Options")

        group.add_option('--sourcename',
                         dest='sourcename', default='packets',
                         help='Name of source to run report against, '
                              'can be either "packets" or "aggregates". '
                              'Defaults to "packets"')
        group.add_option('--sourceid',
                         dest='sourceid', default=None,
                         help='If sourcename is "packets", '
                              'ID of the source to run report against, in the '
                              'form of <type>/<id>, e.g. "interfaces/mon0", or '
                              '"jobs/default_job".')
        group.add_option('--keycolumns',
                         dest='keycolumns',
                         default=None,
                         help='List of key column names separated by comma')
        group.add_option('--valuecolumns', dest='valuecolumns',
                         default=None,
                         help='List of value column names separated by comma'
                         )
        group.add_option('--interval', dest='interval',
                         default=1,
                         help='Delay in seconds between data requests, '
                              'defaults to 1 sec'
                         )
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, "Time and Filter Options")
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
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, "Output Options")
        group.add_option('--csvfile', dest='csvfile', default=None,
                         help='CSV file to store report data')
        parser.add_option_group(group)

    def validate_args(self):
        super(LiveReportApp, self).validate_args()

        try:
            self.delay = int(self.options.interval)
        except:
            self.parser.error('Invalid interval time: %s'
                              % self.options.interval)

        if self.options.sourcename == 'packets':
            if self.options.sourceid is None:
                print('No source defined, '
                      'choosing first MIFG or VIFG available.')

            if (self.options.sourceid and
                    '/' not in self.options.sourceid):
                self.parser.error('Invalid sourceid: {}.  Must be of the form'
                                  '<type>/<id>')

        elif self.options.sourcename == 'aggregates':
            print('Setting granularity to 60s for aggregates data source.')
            self.options.granularity = 60

            if self.delay == 1:
                # override default of 1 to 60 for aggregates
                print('Setting interval to 60s for aggregates data source.')
                self.delay = 60

            if self.delay % 60 != 0:
                self.parser.error('Invalid interval for aggregates data source: {}. '
                                  'Must be multiple of 60s.'.format(self.delay))
        else:
            self.parser.error('Invalid sourcename: {}. '
                              'Must be either "packets" or "aggregates"')

        if (self.options.keycolumns is None and
                self.options.valuecolumns is None):
            print('Choosing default set of columns: ')

            if self.options.sourcename == 'packets':
                self.options.keycolumns = ','.join([
                    'frame.timestamp',
                    'src_ip.addr',
                    'dst_ip.addr'
                ])
                self.options.valuecolumns = ','.join([
                    'sum_traffic.total_bytes',
                    'sum_traffic.packets',
                    'sum_ip.total_packets_psg'
                ])
            elif self.options.sourcename == 'aggregates':
                self.options.keycolumns = ','.join([
                    'app.id',
                ])
                self.options.valuecolumns = ','.join([
                    'app.name',
                    'sum_traffic.total_bytes'
                ])

            print('--keycolumns={} --valuecolumns={}'
                  .format(self.options.keycolumns,
                          self.options.valuecolumns))

    def main(self):

        if self.options.sourcename == 'packets':
            if self.options.sourceid is None:
                try:
                    source = self.appresponse.capture.get_mifgs()[0]
                except:
                    source = self.appresponse.capture.get_vifgs()[0]
            else:
                source = SourceProxy(name='packets',
                                     path=self.options.sourceid)
        else:
            source = SourceProxy(name='aggregates')

        columns = []
        headers = []

        for col in self.options.keycolumns.split(','):
            columns.append(Key(col))
            headers.append(col)

        for col in self.options.valuecolumns.split(','):
            columns.append(Value(col))
            headers.append(col)

        data_def = DataDef(source=source,
                           columns=columns,
                           granularity=self.options.granularity,
                           resolution=self.options.resolution,
                           live=True)

        if self.options.filterexpr:
            data_def.add_filter(TrafficFilter(type_='steelfilter',
                                              value=self.options.filterexpr))

        print('Running report, press Ctrl-C to exit.')
        print('')

        report = self.appresponse.create_report(data_def)
        time.sleep(1)

        try:

            while 1:
                banner = '{} {}'.format(datetime.datetime.now(), '--' * 20)
                print(banner)

                try:
                    data = report.get_data()['data']
                except KeyError:
                    # something went wrong, print error and exit
                    print('Error accessing data:')
                    print(report.get_data())
                    raise KeyboardInterrupt

                headers = report.get_legend()

                if self.options.csvfile:
                    with open(self.options.csvfile, 'a') as f:
                        f.write(banner)
                        f.write('\n')
                        for line in Formatter.get_csv(data, headers):
                            f.write(line)
                            f.write('\n')
                else:
                    Formatter.print_table(data, headers)

                time.sleep(self.delay)

        except KeyboardInterrupt:
            print('Exiting ...')
            report.delete()


if __name__ == "__main__":
    app = LiveReportApp()
    app.run()
