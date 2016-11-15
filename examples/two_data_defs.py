# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common.service import UserAuth
from steelscript.appresponse.core.appresponse import AppResponse
from steelscript.appresponse.core.types import Key, Value, TimeFilter
from steelscript.appresponse.core.reports import Report

hostname = '<hostname>'
auth = UserAuth(username='admin', password='admin')

arx = AppResponse(host=hostname, auth=auth)

report = Report(arx)

tf1 = TimeFilter.parse_range('last 10 seconds')
tf2 = TimeFilter.parse_range('last 20 seconds')

job = arx.get_capture_job_by_name('<Job Name>')

columns = [Key('start_time'), Value('sum_traffic.total_bytes')]


report.add(job, columns, '1', tf1)
report.add(job, columns, '1', tf2)

report.run()

data = report.get_data()

report.delete()
