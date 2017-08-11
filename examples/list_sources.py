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
            data.append([job.id, job.name,
                         job.data.config.mifg_id,
                         getattr(job.data.config, 'filter',
                                 dict(string=None))['string'],
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
