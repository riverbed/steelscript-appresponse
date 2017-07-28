#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Show available packet sources.
"""

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.datautils import Formatter


class PacketCaptureApp(AppResponseApp):

    def console(self, source_type, data, headers):
        print('')
        print(source_type)
        print('-' * len(source_type))

        Formatter.print_table(data, headers)

    def main(self):

        # Show capture jobs
        headers = ['id', 'name', 'mifg_id', 'filter', 'state',
                   'start_time', 'end_time', 'size']
        data = []
        for job in self.appresponse.capture.get_jobs():
            data.append([job.prop.id, job.prop.config.name,
                         job.prop.config.mifg_id,
                         getattr(job.prop.config, 'filter',
                                 dict(string=None))['string'],
                         job.prop.state.status.state,
                         job.prop.state.status.packet_start_time,
                         job.prop.state.status.packet_end_time,
                         job.prop.state.status.capture_size])
        self.console('Capture Jobs', data, headers)

        # Show clips

        headers = ['id', 'job_id', 'start_time', 'end_time', 'filters']
        data = []
        for clip in self.appresponse.clips.get_clips():
            data.append([clip.prop.id, clip.prop.config.job_id,
                         clip.prop.config.start_time,
                         clip.prop.config.end_time,
                         getattr(clip.prop.config, 'filters',
                                 dict(items=None))['items']])
        self.console('Clips', data, headers)

        # Show files

        headers = ['type', 'id', 'link_type', 'format',
                   'size', 'created', 'modified']
        data = []
        for obj in self.appresponse.fs.get_files():
            data.append([obj.prop.type, obj.prop.id, obj.prop.link_type,
                         obj.prop.format, obj.prop.size,
                         obj.prop.created, obj.prop.modified])
        self.console('Uploaded Files/PCAPs', data, headers)


if __name__ == '__main__':
    app = PacketCaptureApp()
    app.run()
