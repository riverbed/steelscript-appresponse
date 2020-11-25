#!/usr/bin/env python
'''
' Riverbed Community SteelScript
'
' print_hostgroups-formatted.py
'
' Usage
'     python print_hostgroups-formatted.py appresponse-ip-address -u admin -p password
'
' Example
'     python print_hostgroups-formatted.py 10.10.10.9 -u admin -p password
'
' Copyright (c) 2020 Riverbed Technology, Inc.
'
' This software is licensed under the terms and conditions of the MIT License
' accompanying the software ("License").  This software is distributed "AS IS"
' as set forth in the License.
'''

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.datautils import Formatter
class HostGroupApp(AppResponseApp):
    def main(self):
        headers = ['id', 'name', 'active', 'definition']
        data = [[hg.id, hg.name, hg.data.enabled, hg.data.hosts]
                for hg in self.appresponse.classification.get_hostgroups() if hasattr(hg.data,'hosts')
                ]
        Formatter.print_table(data, headers)


app = HostGroupApp()
app.run()