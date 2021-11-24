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
from steelscript.common.service import UserAuth
from steelscript.common import Service
from steelscript.common.exceptions import RvbdHTTPException

host = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
clip_id = sys.argv[4]
uri= '/api/npm.clips/1.0/clips/items/'

ar11 = Service("appresponse", host, auth=UserAuth(username, password))

path = uri + clip_id

try:
    result = ar11.conn.request('DELETE', path)
    if result.status_code == 204:
        print("Successfully deleted clip ID: "+clip_id)
except RvbdHTTPException as e:
    if e.status == 404:
        message = "Clip ID file does not exist!"
    else:
        message = "Error retrieving information on '{}'".format(path)
    print(message)