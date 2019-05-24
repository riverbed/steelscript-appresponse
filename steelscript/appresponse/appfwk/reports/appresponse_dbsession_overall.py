
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

report = Report.create("AppResponse DB Session Overall")

report.add_section()

# t1 is used to derive the overall metrics over the duration
t1 = AppResponseTable.create('db-session-overall',
                             source='dbsession_summaries')
t1.add_column('db_instance', 'DB Instance', datatype='string', iskey=True,
              extractor='db.instance')
t1.add_column('active_sessions', 'Concurrent Active DB Sessions',
              datatype='float',
              extractor='avg_db.active_sessions')
t1.add_column('active_time', 'Total Duration of Active Sessions',
              datatype='float',
              extractor='sum_db.session_active_time')

# t2 is used to derive the time series metrics values over the duration
t2 = AppResponseTable.create('db-session-overall-ts',
                             source='dbsession_summaries')
# Add this time key column is the main differentiator between t2 and t1
t2.copy_columns(t1)
t2.add_column('start_time', 'Time', datatype='time', iskey=True,
              extractor='start_time')

t3 = AppResponseTimeSeriesTable.create('db-active-session-ts',
                                       tables={'base': t2},
                                       pivot_column_name='db_instance',
                                       value_column_name='active_sessions',
                                       hide_pivot_field=True)

t4 = AppResponseTopNTimeSeriesTable.create('db-active-session',
                                           tables={'overall': t1},
                                           related_tables={'ts': t3},
                                           pivot_column_name='db_instance',
                                           value_column_name='active_sessions',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t4,
                  "DB Sessions/Top {} Active Sessions".format(topn),
                  width=12)

t5 = AppResponseTimeSeriesTable.create('db-active-time-ts',
                                       tables={'base': t2},
                                       pivot_column_name='db_instance',
                                       value_column_name='active_time',
                                       hide_pivot_field=True)

t6 = AppResponseTopNTimeSeriesTable.create('db-active-time',
                                           tables={'overall': t1},
                                           related_tables={'ts': t5},
                                           pivot_column_name='db_instance',
                                           value_column_name='active_time',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t6,
                  "DB Sessions/Top {} Active Time".format(topn),
                  width=12)

t7 = AppResponseLinkTable.create('db-session-link-overall',
                                 tables={'base': t1},
                                 pivot_column_name='db_instance',
                                 ts_report_mod_name='appresponse_dbsession_ts')

report.add_widget(tables.TableWidget, t7, "DB Session Overall",
                  width=12, height=0, searching=True)
