#!/usr/bin/env python

# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Upload a pcap file to AppResponse 11 appliance
"""

import os

from steelscript.appresponse.core.app import AppResponseApp


class UploadPcap(AppResponseApp):
    def add_options(self, parser):
        super(UploadPcap, self).add_options(parser)
        parser.add_option('--filepath',
                          help='path to pcap tracefile to upload')
        parser.add_option('--destname', default=None,
                          help='location to store on server, defaults to '
                               '<username>/<basename of filepath>')

    def validate_args(self):
        super(UploadPcap, self).validate_args()

        basedir = '/' + self.options.username

        if not self.options.destname:
            dst = os.path.join(basedir,
                               os.path.basename(self.options.filepath))
            self.options.destname = dst

    def main(self):
        print("Uploading {}".format(self.options.filepath))
        self.appresponse.upload(
            dest_path=self.options.destname,
            local_file=self.options.filepath
        )
        print("File '{}' successfully uploaded."
              .format(self.options.filepath))
        res = self.appresponse.fs.get_file_by_id(self.options.destname).data
        print("The properties are {}".format(res))


if __name__ == "__main__":
    app = UploadPcap()
    app.run()
