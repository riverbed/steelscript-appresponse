
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.appfwk.apps.report.modules.tables as tables
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseTimeSeriesTable, \
    AppResponseTopNTimeSeriesTable, AppResponseLinkTable

topn = 10

report = Report.create("AppResponse ASA Overall")

report.add_section()

# t1 is used to derive the overall metrics over the duration
t1 = AppResponseTable.create('applications-overall', source='aggregates')
t1.add_column('app_id', 'App ID', datatype='string', iskey=True,
              extractor='app.id')
t1.add_column('app_name', 'App Name', datatype='string',
              extractor='app.name')
t1.add_column('total_bytes', 'Average Bytes per Second', datatype='float',
              extractor='avg_traffic.total_bytes_ps')
t1.add_column('srv_response_time', 'Average Server Response Time (seconds)',
              datatype='float', extractor='avg_tcp.srv_response_time')
t1.add_column('usr_response_time', 'Average User Response Time (seconds)',
              datatype='float', extractor='avg_tcp.user_response_time')

# t2 is used to derive the time series metrics values over the duration
t2 = AppResponseTable.create('applications-overall-ts', source='aggregates')
# Add this time key column is the main differentiator between t2 and t1
t2.copy_columns(t1)
t2.add_column('start_time', 'Time', datatype='time', iskey=True,
              extractor='start_time')

t3 = AppResponseTimeSeriesTable.create('app-throughput-ts',
                                       tables={'base': t2},
                                       pivot_column_name='app_name',
                                       value_column_name='total_bytes',
                                       hide_pivot_field=True)

t4 = AppResponseTopNTimeSeriesTable.create('app-throughput',
                                           tables={'overall': t1},
                                           related_tables={'ts': t3},
                                           pivot_column_name='app_name',
                                           value_column_name='total_bytes',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t4,
                  "Apps/Top {} Throughput".format(topn),
                  width=12)

t5 = AppResponseTimeSeriesTable.create('app-srv-resp-ts',
                                       tables={'base': t2},
                                       pivot_column_name='app_name',
                                       value_column_name='srv_response_time',
                                       hide_pivot_field=True)

t6 = AppResponseTopNTimeSeriesTable.create(
    'app-srv-resp',
    tables={'overall': t1},
    related_tables={'ts': t5},
    pivot_column_name='app_name',
    value_column_name='srv_response_time',
    n=topn
)

report.add_widget(c3.TimeSeriesWidget, t6,
                  "Apps/Top {} Server Response Time".format(topn),
                  width=12)

t7 = AppResponseTimeSeriesTable.create('app-usr-resp-ts',
                                       tables={'base': t2},
                                       pivot_column_name='app_name',
                                       value_column_name='usr_response_time',
                                       hide_pivot_field=True)

t8 = AppResponseTopNTimeSeriesTable.create(
    'app-usr-resp',
    tables={'overall': t1},
    related_tables={'ts': t7},
    pivot_column_name='app_name',
    value_column_name='usr_response_time',
    n=topn
)

report.add_widget(c3.TimeSeriesWidget, t8,
                  "Apps/Top {} User Response Time".format(topn),
                  width=12)

t9 = AppResponseLinkTable.create('app-link-overall',
                                 tables={'base': t1},
                                 pivot_column_name='app_name',
                                 ts_report_mod_name='appresponse_asa_ts')

report.add_widget(tables.TableWidget, t9, "Throughput & Response Time",
                  width=12, height=0, searching=True)
