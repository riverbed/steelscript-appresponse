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
            data.append([job.id, job.config.name,
                         job.config.mifg_id,
                         getattr(job.config, 'filter',
                                 dict(string=None))['string'],
                         job.state.status.state,
                         job.state.status.packet_start_time,
                         job.state.status.packet_end_time,
                         job.state.status.capture_size])
        self.console('Capture Jobs', data, headers)

        # Show clips

        headers = ['id', 'job_id', 'start_time', 'end_time', 'filters']
        data = []
        for clip in self.appresponse.clips.get_clips():
            data.append([clip.id, clip.config.job_id,
                         clip.config.start_time,
                         clip.config.end_time,
                         getattr(clip.config, 'filters',
                                 dict(items=None))['items']])
        self.console('Clips', data, headers)

        # Show files

        headers = ['type', 'id', 'link_type', 'format',
                   'size', 'created', 'modified']
        data = []
        for obj in self.appresponse.fs.get_files():
            data.append([obj.type, obj.id, obj.link_type,
                         obj.format, obj.size,
                         obj.created, obj.modified])
        self.console('Uploaded Files/PCAPs', data, headers)


if __name__ == '__main__':
    app = PacketCaptureApp()
    app.run()
