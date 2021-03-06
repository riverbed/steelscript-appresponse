#!/usr/bin/env python
'''
' Riverbed Community SteelScript
'
' .py
'
' Encoding: UTF8
' End of Line Sequence: LF
'
' Copyright (c) 2021 Riverbed Technology, Inc.
'
' This software is licensed under the terms and conditions of the MIT License
' accompanying the software ("License").  This software is distributed "AS IS"
' as set forth in the License.
'''

"""
Show available packet sources.
"""
from collections import namedtuple

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.api_helpers import APIVersion
from steelscript.common.datautils import Formatter


IFG = namedtuple('IFG', 'type get_id get_items')


class PacketCaptureApp(AppResponseApp):

    def console(self, source_type, data, headers):
        print('')
        print(source_type)
        print('-' * len(source_type))

        if data:
            Formatter.print_table(data, headers)
        else:
            print('None.')

    def main(self):

        # handle new packet capture version
        version = APIVersion(self.appresponse.versions['npm.packet_capture'])
        if version < APIVersion('2.0'):
            ifg = IFG('mifg_id',
                      lambda job: job.data.config.mifg_id,
                      self.appresponse.capture.get_mifgs)
        else:
            ifg = IFG('vifgs',
                      lambda job: job.data.config.vifgs,
                      self.appresponse.capture.get_vifgs)

        # Show Interfaces and VIFGs (skip if MIFG appliance)
        if ifg.type == 'vifgs':
            # Show interfaces
            headers = ['name', 'description', 'status', 'bytes_total',
                       'packets_dropped', 'packets_total']
            data = []
            for iface in self.appresponse.capture.get_interfaces():
                data.append([
                    iface.name,
                    iface.data.config.description,
                    iface.status,
                    iface.stats.bytes_total.total,
                    iface.stats.packets_dropped.total,
                    iface.stats.packets_total.total,
                ])
            self.console('Interfaces', data, headers)

            headers = ['id', 'name', 'enabled', 'filter', 'bytes_received',
                       'packets_duped', 'packets_received']
            data = []
            for vifg in self.appresponse.capture.get_vifgs():
                data.append([
                    vifg.data.id,
                    vifg.data.config.name,
                    vifg.data.config.enabled,
                    vifg.data.config.filter,
                    vifg.data.state.stats.bytes_received.total,
                    vifg.data.state.stats.packets_duped.total,
                    vifg.data.state.stats.packets_received.total,
                ])
            self.console('VIFGs', data, headers)

        # Show capture jobs
        headers = ['id', 'name', ifg.type, 'filter', 'state',
                   'start_time', 'end_time', 'size']
        data = []
        for job in self.appresponse.capture.get_jobs():
            data.append([job.id, job.name,
                         ifg.get_id(job),
                         getattr(job.data.config, 'filter', None),
                         job.data.state.status.state,
                         job.data.state.status.packet_start_time,
                         job.data.state.status.packet_end_time,
                         job.data.state.status.capture_size])
        self.console('Capture Jobs', data, headers)

        # Show clips

        headers = ['id', 'job_id', 'start_time', 'end_time', 'filters']
        data = []
        for clip in self.appresponse.clips.get_clips():
            data.append([clip.id, clip.data.config.job_id,
                         clip.data.config.start_time,
                         clip.data.config.end_time,
                         getattr(clip.data.config, 'filters',
                                 dict(items=None))['items']])
        self.console('Clips', data, headers)

        # Show files

        headers = ['type', 'id', 'link_type', 'format',
                   'size', 'created', 'modified']
        data = []
        for obj in self.appresponse.fs.get_files():
            data.append([obj.data.type, obj.id, obj.data.link_type,
                         obj.data.format, obj.data.size,
                         obj.data.created, obj.data.modified])
        self.console('Uploaded Files/PCAPs', data, headers)


if __name__ == '__main__':
    app = PacketCaptureApp()
    app.run()
