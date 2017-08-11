#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Create a capture job.
"""

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.datautils import Formatter


class PacketCaptureApp(AppResponseApp):
    def add_options(self, parser):
        super(PacketCaptureApp, self).add_options(parser)

        parser.add_option('--jobname', dest='jobname', default=None,
                          help='job name')
        parser.add_option('--mifg-id', dest='mifg_id', default=None,
                          help='ID of the MIFG on which this job '
                               'is collecting packet data')
        parser.add_option('--filter', dest='filter', default='',
                          help='STEELFILTER/BPF filter of the packets '
                               'collected')
        parser.add_option('--filter-type', dest='filter_type', default='BPF',
                          help='STEELFILTER or BPF, default BPF')
        parser.add_option('--show-mifgs', action='store_true',
                          dest='show_mifgs', default=False,
                          help='Show list of MIFG on the device')
        parser.add_option('--show-jobs', action='store_true',
                          dest='show_jobs', default=False,
                          help='Show list of capture jobs on the device')

    def validate_args(self):
        super(PacketCaptureApp, self).validate_args()

        if self.options.show_jobs or self.options.show_mifgs:
            return

        if not self.options.jobname:
            self.parser.error("Job name needs to be provided.")

        if not self.options.mifg_id:
            self.parser.error("MIFG ID needs to be provided.")

    def main(self):

        if self.options.show_mifgs:
            headers = ['id', 'name', 'interfaces']
            data = []
            for mifg in self.appresponse.capture.get_mifgs():
                data.append([mifg.id, mifg.name,
                             mifg.data.config.interfaces])

            Formatter.print_table(data, headers)

        elif self.options.show_jobs:
            headers = ['id', 'name', 'mifg_id', 'filter', 'state',
                       'start', 'end', 'size']
            data = []
            for job in self.appresponse.capture.get_jobs():
                data.append([job.id, job.name,
                             job.data.config.mifg_id,
                             getattr(job.data.config, 'filter',
                                     dict(string=None))['string'],
                             job.status,
                             job.data.state.status.packet_start_time,
                             job.data.state.status.packet_end_time,
                             job.data.state.status.capture_size])
            Formatter.print_table(data, headers)

        else:
            config = dict(name=self.options.jobname,
                          mifg_id=int(self.options.mifg_id),
                          filter=dict(type=self.options.filter_type,
                                      string=self.options.filter))

            self.appresponse.capture.create_job(dict(config=config))
            print("Successfully created packet capture job {}"
                  .format(self.options.jobname))


if __name__ == '__main__':
    app = PacketCaptureApp()
    app.run()
