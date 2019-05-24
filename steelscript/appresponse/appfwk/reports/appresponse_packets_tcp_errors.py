# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.appfwk.apps.report.modules.tables as tables
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable

report = Report.create("AppResponse Packets - TCP Errors",
                       field_order=['endtime', 'duration',
                                    'appresponse_device',
                                    'appresponse_source',
                                    'entire_pcap', 'granularity'])

report.add_section()

# TCP Errors
p = AppResponseTable.create('TCPErrors',
                            duration='1 min', granularity='1s',
                            include_files=True)

p.add_column('error_type', label='TCP Error Type', iskey=True,
             datatype='string',
             extractor='tcp.error_type', alias='tcp.error_type_name')
p.add_column('errors', label='TCP Error Count', datatype='integer',
             sortdesc=True, extractor='sum_tcp.errors')

report.add_widget(c3.BarWidget, p, 'TCP Errors',
                  width=6, height=400)
report.add_widget(tables.TableWidget, p, 'TCP Errors Table',
                  width=6, height=400)
