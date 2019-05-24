#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Host Group information on AppResponse appliance:

1. Show existng host groups
2. Update one host group
3. Add one host group
4. Create multiple host groups by uploading a file
5. Delete one host group
6. Clear all host groups
"""
import optparse


from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.datautils import Formatter
from steelscript.appresponse.core.classification import HostGroupConfig


class HostGroupApp(AppResponseApp):
    def add_options(self, parser):
        super(HostGroupApp, self).add_options(parser)

        group = optparse.OptionGroup(parser, "HostGroup Options")
        group.add_option('--file', dest='file', default=None,
                         help=('Path to the file with hostgroup info, '
                               'each line should have two columns '
                               'formated as:              '
                               '"<hostgroup_name> <subnet_1>,<subnet_2>,..."'))
        group.add_option('--name', dest='name', default=None,
                         help='Namme of host group to update or delete')
        group.add_option('--id', dest='id', default=None,
                         help='ID of the host group to update or delete')
        group.add_option('--hosts', dest='hosts', default=None,
                         help='List of hosts and host-ranges')
        group.add_option('--disabled', action='store_true', dest='disabled',
                         default=False, help='Whether host group should be '
                                             'disabled')
        group.add_option('--operation',
                         dest='operation', default=None,
                         help=('show: render configured hostgroups'
                               '                  '
                               'add: add one hostgroup'
                               '                              '
                               'update: update one hostgroup'
                               '                        '
                               'upload: upload a file with hostgroups'
                               '                '
                               'delete: delete one hostgroup'
                               '                         '
                               'clear: clear all hostgroups'
                               '                         '))
        parser.add_option_group(group)

    def validate_args(self):
        super(HostGroupApp, self).validate_args()

        if self.options.operation not in ['show', 'add', 'update',
                                          'delete', 'clear', 'upload']:
            self.parser.error("Operation should be set as one of "
                              "'show', 'add', 'update', 'upload', "
                              "'delete', 'clear'")

        if self.options.operation == 'upload' and not self.options.file:
            self.parser.error("File needs to be specified for 'upload' "
                              "operation")

        if self.options.operation == 'add' and \
                (not self.options.name or not self.options.hosts):
            self.parser.error("Hostgroup name and hosts are needed for "
                              "'add' operation")

        if self.options.operation == 'update' and \
                (not self.options.name and not self.options.id):

            self.parser.error("Hostgroup Name/ID is needed for 'update' "
                              "operation.")

        if self.options.operation == 'delete' and \
                (not self.options.name and not self.options.id):
            self.parser.error("Hostgroup name or ID is needed for 'delete' "
                              "operation.")

    def main(self):

        enabled = not self.options.disabled

        if self.options.operation == 'show':
            headers = ['id', 'name', 'active', 'definition']
            data = [[hg.id, hg.name, hg.data.enabled, hg.data.hosts]
                    for hg in self.appresponse.classification.get_hostgroups()
                    ]
            Formatter.print_table(data, headers)

        elif self.options.operation == 'add':

            hg = HostGroupConfig(name=self.options.name,
                                 hosts=self.options.hosts.split(','),
                                 enabled=enabled)
            ret = self.appresponse.classification.create_hostgroup(hg)
            print("Successfully created hostgroup '{}'".format(ret.data.name))

        elif self.options.operation == 'update':
            if self.options.id:
                hg = self.appresponse.classification.get_hostgroup_by_id(
                    self.options.id)
            else:
                hg = self.appresponse.classification.get_hostgroup_by_name(
                    self.options.name)

            hgc = HostGroupConfig(name=self.options.name or hg.data.name,
                                  hosts=(self.options.hosts.split(',')
                                         if self.options.hosts
                                         else hg.data.hosts),
                                  enabled=enabled)
            hg.update(hgc)
            print("Successfully updated hostgroup '{}'".format(hg.name))

        elif self.options.operation == 'upload':
            with open(self.options.file) as f:
                hgs = []
                for ln in f.readlines():
                    if not ln:
                        continue
                    name, hosts = ln.split()
                    hgs.append(HostGroupConfig(name=name,
                                               hosts=hosts.split(','),
                                               enabled=True))
                self.appresponse.classification.create_hostgroups(hgs)
                print("Successfully uploaded {} hostgroup definitions."
                      .format(len(hgs)))

        elif self.options.operation == 'delete':
            if self.options.id:
                hg = self.appresponse.classification.get_hostgroup_by_id(
                    self.options.id)
            else:
                hg = self.appresponse.classification.get_hostgroup_by_name(
                    self.options.name)

            hg.delete()
            print("Successfully deleted hostgroup with ID/name {}"
                  .format(self.options.id or self.options.name))

        elif self.options.operation == 'clear':  # clear all hostgroups
            self.appresponse.classification.bulk_delete()
            print("Successfully cleared all hostgroups")


if __name__ == "__main__":
    app = HostGroupApp()
    app.run()
