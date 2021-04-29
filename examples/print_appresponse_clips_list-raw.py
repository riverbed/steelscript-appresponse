#!/usr/bin/env python
'''
' Riverbed Community SteelScript
'
' print_appresponse_clips_list-raw.py`
'
' Encoding: UTF8
' End of Line Sequence: LF
'
' Usage
'     python print_appresponse_clips_list-raw.py {appresponse-ip-address} {username} {password}
'
' Example
'     python print_appresponse_clips_list-raw.py 10.10.10.10 admin password
'
'     output example: 
{
    "items": [
        {
            "status": {
                "estimated_size": 0,
                "modification_time": "0",
                "packets_dropped": 0,
                "locked": false,
                "packets_written": 0,
                "creation_time": "1613657410.054126000"
            },
            "index_stats": {
                "items": [
                    {
                        "start_time": "1613656786",
                        "version": "2",
                        "end_time": "1613657386"
                    }
                ]
            },
            "config": {
                "start_time": "1613656786",
                "end_time": "1613657386",
                "job_id": "382b2f64-4dba-499b-aac9-b862f1c217ad"
            },
            "id": "382b2f64-4dba-499b-aac9-b862f1c217ad0002"
        },
        ...
    ]
}
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

auth = UserAuth(username=username, password=password)

service = Service('AppResponse', host=host, auth=auth)

uri = '/api/npm.clips/1.0/clips'
result = service.conn.json_request('GET', uri)
print(result)
