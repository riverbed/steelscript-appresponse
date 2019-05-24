
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseTimeSeriesTable

report = Report.create("AppResponse ASA Time Series")

report.add_section()

t = AppResponseTable.create('timeseries-base', source='aggregates')
t.add_column('start_time', 'Time', datatype='time', iskey=True,
             extractor='start_time')
t.add_column('app_id', 'App ID', datatype='string', iskey=True,
             extractor='app.id')
t.add_column('app_name', 'App Name', datatype='string',
             extractor='app.name')
t.add_column('srv_response_time', 'Average Server Response Time (seconds)',
             datatype='float', extractor='avg_tcp.srv_response_time')
t.add_column('usr_response_time', 'Average User Response Time (seconds)',
             datatype='float', extractor='avg_tcp.user_response_time')
t.add_column('total_bytes', 'Average Bytes per Second', datatype='float',
             extractor='avg_traffic.total_bytes_ps')

t1 = AppResponseTimeSeriesTable.create('application-srv-response-time',
                                       tables={'base': t},
                                       pivot_column_label='App Names',
                                       pivot_column_name='app_name',
                                       value_column_name='srv_response_time')

report.add_widget(c3.TimeSeriesWidget, t1, 'Server Response Time',
                  width=12)

t2 = AppResponseTimeSeriesTable.create('application-user-resp-time',
                                       tables={'base': t},
                                       pivot_column_name='app_name',
                                       value_column_name='usr_response_time')
report.add_widget(c3.TimeSeriesWidget, t2, 'Server Response Time',
                  width=12)

t3 = AppResponseTimeSeriesTable.create('application-throughput',
                                       tables={'base': t},
                                       pivot_column_name='app_name',
                                       value_column_name='total_bytes')
report.add_widget(c3.TimeSeriesWidget, t3, 'Average Throughput (BPS)',
                  width=12)
