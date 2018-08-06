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
        parser.add_option('--vifg', dest='vifgs', default=None,
                          help='ID of the VIFG on which this job '
                               'is collecting packet data')
        parser.add_option('--filter', dest='filter', default='',
                          help='STEELFILTER/BPF filter of the packets '
                               'collected')
        parser.add_option('--filter-type', dest='filter_type', default='BPF',
                          help='STEELFILTER or BPF, default BPF')
        parser.add_option('--show-vifgs', action='store_true',
                          dest='show_vifgs', default=False,
                          help='Show list of VIFG on the device')
        parser.add_option('--show-jobs', action='store_true',
                          dest='show_jobs', default=False,
                          help='Show list of capture jobs on the device')

    def validate_args(self):
        super(PacketCaptureApp, self).validate_args()

        if self.options.show_jobs or self.options.show_vifgs:
            return

        if not self.options.jobname:
            self.parser.error("Job name needs to be provided.")

        if not self.options.vifgs:
            self.parser.error("VIFG ID needs to be provided.")

    def main(self):

        if self.options.show_vifgs:
            headers = ['id', 'name', 'filter', 'members']
            data = []
            for vifg in self.appresponse.capture.get_vifgs():
                f = vifg.data.config.filter
                fltr = f if f['value'] else 'None'

                data.append([vifg.id, vifg.name,
                             fltr,
                             vifg.data.config.members])

            Formatter.print_table(data, headers)

        elif self.options.show_jobs:
            headers = ['id', 'name', 'vifgs', 'filter', 'state',
                       'start', 'end', 'size']
            data = []
            for job in self.appresponse.capture.get_jobs():
                data.append([job.id, job.name,
                             job.data.config.vifgs,
                             getattr(job.data.config, 'filter',
                                     dict(string=None))['string'],
                             job.status,
                             job.data.state.status.packet_start_time,
                             job.data.state.status.packet_end_time,
                             job.data.state.status.capture_size])
            Formatter.print_table(data, headers)

        else:
            vifgs = [int(v) for v in self.options.vifgs.split(',')]

            config = dict(name=self.options.jobname,
                          enabled=True,
                          vifgs=vifgs)

            if self.options.filter:
                fltr = dict(type=self.options.filter_type,
                            string=self.options.filter)
                config['filter'] = fltr

            self.appresponse.capture.create_job(config)
            print("Successfully created packet capture job {}"
                  .format(self.options.jobname))


if __name__ == '__main__':
    app = PacketCaptureApp()
    app.run()
