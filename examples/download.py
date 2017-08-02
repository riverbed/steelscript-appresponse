#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Download a pcap file from one packet source.
"""
import optparse

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.appresponse.core.types import TimeFilter


class DownloadApp(AppResponseApp):

    def add_options(self, parser):
        super(DownloadApp, self).add_options(parser)

        group = optparse.OptionGroup(parser, "Source Options")
        group.add_option('--source-file', dest='source_file', default=None,
                         help='source file path to export')
        group.add_option('--jobname', dest='jobname', default=None,
                         help='job name to export')
        group.add_option('--jobid', dest='jobid', default=None,
                         help='job ID to export')
        group.add_option('--clipid', dest='clipid', default=None,
                         help='clip ID to export')
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, "Time and Filter Options")
        group.add_option('--starttime', dest='start_time', default=None,
                         help='start time for export (timestamp format)')
        group.add_option('--endtime', dest='end_time', default=None,
                         help='end time for export (timestamp format)')
        group.add_option('--timerange', dest='timerange', default=None,
                         help='Time range to analyze '
                              '(defaults to "last 1 hour") '
                              'other valid formats are: '
                              '"4/21/13 4:00 to 4/21/13 5:00" '
                              'or "16:00:00 to 21:00:04.546"')
        group.add_option('--filter', dest='filters', action='append',
                         default=[],
                         help='filter to apply to export, can be repeated as '
                              'many times as desired. Each filter should be '
                              'formed as "<id>,<type>,<value>", where '
                              '<type> should be one of "BPF", "STEELFILTER", '
                              '"WIRESHARK", i.e.           "f1,BPF,port 80".')
        parser.add_option_group(group)

        group = optparse.OptionGroup(parser, "Output Options")
        group.add_option('--dest-file', dest='dest_file', default=None,
                         help='destination file path to export')
        group.add_option('--overwrite', dest='overwrite', action='store_true',
                         help='Overwrite the local file if it exists')
        parser.add_option_group(group)

    def validate_args(self):
        """Ensure one packet source is provided."""
        super(DownloadApp, self).validate_args()

        if ((self.options.source_file is not None) +
                (self.options.jobname is not None) +
                (self.options.jobid is not None) +
                (self.options.clipid is not None) != 1):
            self.parser.error("Select one of --source-file, --jobname, "
                              "--jobid, --clipid")

    def main(self):

        if self.options.jobname:
            source = self.appresponse.capture.get_job_by_name(
                self.options.jobname)
        elif self.options.jobid:
            source = self.appresponse.capture.get_job_by_id(
                self.options.jobid)
        elif self.options.source_file:
            source = self.appresponse.fs.get_file_by_id(
                self.options.source_file)
        else:
            source = self.appresponse.clips.get_clip_by_id(
                self.options.clipid)

        filename = self.options.dest_file
        if not filename:
            filename = '{}_export.pcap'.format(
                self.options.jobname or self.options.jobid or
                self.options.source_file or self.options.clipid
            )

        if self.options.timerange:
            timefilter = TimeFilter(time_range=self.options.timerange)
        elif self.options.start_time and self.options.end_time:
            timefilter = TimeFilter(start=self.options.start_time,
                                    end=self.options.end_time)
        else:
            self.parser.error("Select either --timerange or --start and "
                              "--end times")

        filters = [dict(zip(['id', 'type', 'value'], f.split(',')))
                   for f in self.options.filters]

        with self.appresponse.create_export(source, timefilter, filters) as e:
            print('Downloading to file {}'.format(filename))
            e.download(filename, overwrite=self.options.overwrite)
            print('Finished downloading to file {}'.format(filename))


if __name__ == '__main__':
    DownloadApp().run()
