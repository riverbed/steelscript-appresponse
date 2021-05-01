#!/usr/bin/env python
'''
' Riverbed Community SteelScript
'
' delete_appresponse_clip.py
'
' Encoding: UTF8
' End of Line Sequence: LF
'
' Usage
'     python delete_appresponse_clip.py {appresponse-ip-address} {username} {password} {clip_id}
'
' Example
'     python delete_appresponse_clip.py 10.10.10.10 admin password "382b2f64-4dba-499b-aac9-b862f1c217ad0002"
'
'
' Copyright (c) 2021 Riverbed Technology, Inc.
'
' This software is licensed under the terms and conditions of the MIT License
' accompanying the software ("License").  This software is distributed "AS IS"
' as set forth in the License.
'''

import sys
from steelscript.common.service import Service, UserAuth

host = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
clip_id = sys.argv[4]

auth = UserAuth(username=username, password=password)

service = Service('AppResponse', host=host, auth=auth)

uri = '/api/npm.clips/1.0/clips/items/' + clip_id
print("Deleting clip id: "+clip_id)
