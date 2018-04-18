#!/usr/bin/env python

# Copyright (c) 2018 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Cleanup Report Instances
"""

import sys

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.commands.steel import prompt_yn
from steelscript.common.datautils import Formatter


class CleanReports(AppResponseApp):
    def add_options(self, parser):
        super(CleanReports, self).add_options(parser)

        parser.add_option('--force',
                          help='Delete all reports without prompting',
                          default=False)

    def validate_args(self):
        super(CleanReports, self).validate_args()

    def main(self):

        instances = self.appresponse.reports.get_instances()

        if instances:
            header = ['id', 'user_agent', 'owner', 'name', 'completed?',
                      'is_live?']
            data = []
            for i in instances:
                data.append(
                    (i.data['id'], i.data['user_agent'],
                     i.data['access_rights']['owner'], i.data['info']['name'],
                     i.is_complete(), i.data['live'])
                )
            Formatter.print_table(data, header)

            if not self.options.force:
                if not prompt_yn('\nDelete all these report instances?',
                                 default_yes=False):
                    print('Okay, exiting.')
                    sys.exit(0)

            for instance in instances:
                instance.delete()

            print('Deleted.')
        else:
            print('No report instances found.')


if __name__ == '__main__':
    app = CleanReports()
    app.run()
