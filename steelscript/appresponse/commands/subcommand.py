# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""This file defines a single Command"""

from optparse import OptionParser, OptionGroup
from steelscript.commands.steel import BaseCommand


class Command(BaseCommand):
    # Provide a one line help message
    help = 'Simple command'

    def add_options(self, parser):
        # Add OptionParser style options for your command
        # See https://docs.python.org/2/library/optparse.html

        # parser.add_option(
        #     '-b', '--beta', default=10,
        #     help='Show more detailed Python installation information')

        # You can also create option groups to provide
        # more organization for long commands
        #
        # group = OptionGroup(parser, 'Special options'
        # group.add_option(....)  -- just like add_option above
        # group.add_option(....)
        # parser.add_option_group(group)

    def main(self):
        # Main execution.  Options are available via self.options
        # print('Running with beta: {beta}'.format(beta=self.options.beta))
