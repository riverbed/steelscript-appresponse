
# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.appfwk.apps.report.modules.tables as tables
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable

report = Report.create("AppResponse General Report")

report.add_section()

p = AppResponseTable.create('network traffic', source='aggregates')
p.add_column('time', 'Time', datatype='time', iskey=True,
             extractor='start_time', )
p.add_column('network_traffic', 'Network Traffic', datatype='integer',
             extractor='sum_traffic.packets')
report.add_widget(c3.TimeSeriesWidget, p, "Network Traffic (Packets)", width=12)

"""
p = AppResponseTable.create('Traffic by TCP/UDP', include_files=True)
p.add_column('time', 'Time', datatype='time', iskey=True,
             extractor='start_time')
p.add_column('tcp_traffic', 'TCP Traffic', datatype='integer',
             extractor='sum_tcp.total_bytes')
p.add_column('udp_traffic', 'UDP Traffic', datatype='integer',
             extractor='sum_udp.total_bytes')
report.add_widget(c3.TimeSeriesWidget, p, "Traffic By Type (Bytes)", width=12)
"""
