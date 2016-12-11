# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common.service import UserAuth
from steelscript.appresponse.core.appresponse import AppResponse
from steelscript.appresponse.core.types import Key, Value, TimeFilter
from steelscript.appresponse.core.reports import DataDef, Report

hostname = '<hostname>'
auth = UserAuth(username='admin', password='admin')

arx = AppResponse(host=hostname, auth=auth)

report = Report(arx)

job = arx.get_capture_job_by_name('<Job Name>')

columns = [Key('start_time'), Value('sum_traffic.total_bytes')]

data_def1 = DataDef(job=job, duration='10 seconds', start=<epoch_seconds>,
                    granularity='1', columns=columns)

data_def2 = DataDef(job=job, duration='20 seconds', start=<epoch_seconds>,
                    granularity='1', columns=columns)

report.add(data_def1)
report.add(data_def2)

report.run()

data = report.get_data()

report.delete()
