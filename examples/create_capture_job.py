#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Create a capture job.
"""
from collections import namedtuple

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.api_helpers import APIVersion
from steelscript.common.datautils import Formatter


IFG = namedtuple('IFG', 'type get_id get_items')


class PacketCaptureApp(AppResponseApp):
    def add_options(self, parser):
        super(PacketCaptureApp, self).add_options(parser)

        parser.add_option('--jobname', dest='jobname', default=None,
                          help='job name')
        parser.add_option('--ifg', dest='ifgs', default=None,
                          help='ID of the MIFG/VIFG on which this job '
                               'is collecting packet data')
        parser.add_option('--filter', dest='filter', default='',
                          help='STEELFILTER/BPF filter of the packets '
                               'collected')
        parser.add_option('--filter-type', dest='filter_type', default='BPF',
                          help='STEELFILTER or BPF, default BPF')
        parser.add_option('--show-ifgs', action='store_true',
                          dest='show_ifgs', default=False,
                          help='Show list of MIFG/VIFG on the device')
        parser.add_option('--show-jobs', action='store_true',
                          dest='show_jobs', default=False,
                          help='Show list of capture jobs on the device')

    def validate_args(self):
        super(PacketCaptureApp, self).validate_args()

        if self.options.show_jobs or self.options.show_ifgs:
            return

        if not self.options.jobname:
            self.parser.error("Job name needs to be provided.")

        if not self.options.ifgs:
            self.parser.error("IFG ID needs to be provided.")

    def main(self):

        version = APIVersion(self.appresponse.versions['npm.packet_capture'])
        if version < APIVersion('2.0'):
            ifg = IFG('mifg_id',
                      lambda job: job.data.config.mifg_id,
                      self.appresponse.capture.get_mifgs)
        else:
            ifg = IFG('vifgs',
                      lambda job: job.data.config.vifgs,
                      self.appresponse.capture.get_vifgs)

        if self.options.show_ifgs:
            headers = ['id', 'name', 'filter', 'members']
            data = []
            for xifg in ifg.get_items():
                if 'filter' in xifg.data.config:
                    f = xifg.data.config.filter
                else:
                    f = {'value': None}

                fltr = f if f['value'] else 'None'

                if 'members' in xifg.data.config:
                    members = xifg.data.config.members
                else:
                    members = xifg.data.config.interfaces

                data.append([xifg.id, xifg.name,
                             fltr,
                             members])

            Formatter.print_table(data, headers)

        elif self.options.show_jobs:
            headers = ['id', 'name', ifg.type, 'filter', 'state',
                       'start', 'end', 'size']
            data = []
            for job in self.appresponse.capture.get_jobs():
                data.append([job.id, job.name,
                             ifg.get_id(job),
                             getattr(job.data.config, 'filter',
                                     dict(string=None))['string'],
                             job.status,
                             job.data.state.status.packet_start_time,
                             job.data.state.status.packet_end_time,
                             job.data.state.status.capture_size])
            Formatter.print_table(data, headers)

        else:

            if version < APIVersion('2.0'):
                config = dict(name=self.options.jobname,
                              mifg_id=int(self.options.ifgs))
            else:
                ifgs = [int(v) for v in self.options.ifgs.split(',')]
                config = dict(name=self.options.jobname,
                              enabled=True,
                              vifgs=ifgs)

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
