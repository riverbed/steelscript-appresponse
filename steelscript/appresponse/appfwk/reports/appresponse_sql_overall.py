
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

report = Report.create("AppResponse SQL Overall")

report.add_section()

# t1 is used to derive the overall metrics over the duration
t1 = AppResponseTable.create('sql-overall', source='sql_summaries')
t1.add_column('db_process', 'Client Process Name', datatype='string',
              iskey=True, extractor='db.process_name')
t1.add_column('sql_duration', 'Average Transaction Time',
              datatype='float',
              extractor='avg_sql.duration')
t1.add_column('sql_packets', 'Average SQL Packets',
              datatype='float',
              extractor='avg_sql.packets')

# t2 is used to derive the time series metrics values over the duration
t2 = AppResponseTable.create('sql-overall-ts', source='sql_summaries')
# Add this time key column is the main differentiator between t2 and t1
t2.copy_columns(t1)
t2.add_column('start_time', 'Time', datatype='time', iskey=True,
              extractor='start_time')

t3 = AppResponseTimeSeriesTable.create('sql-duration-ts',
                                       tables={'base': t2},
                                       pivot_column_name='db_process',
                                       value_column_name='sql_duration',
                                       hide_pivot_field=True)

t4 = AppResponseTopNTimeSeriesTable.create('sql-duration',
                                           tables={'overall': t1},
                                           related_tables={'ts': t3},
                                           pivot_column_name='db_process',
                                           value_column_name='sql_duration',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t4,
                  "Top {} SQL Durations".format(topn),
                  width=12)

t5 = AppResponseTimeSeriesTable.create('sql-packets-ts',
                                       tables={'base': t2},
                                       pivot_column_name='db_process',
                                       value_column_name='sql_packets',
                                       hide_pivot_field=True)

t6 = AppResponseTopNTimeSeriesTable.create('sql-packets',
                                           tables={'overall': t1},
                                           related_tables={'ts': t5},
                                           pivot_column_name='db_process',
                                           value_column_name='sql_packets',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t6,
                  "Top {} SQL Packets".format(topn),
                  width=12)

t7 = AppResponseLinkTable.create('sql-link-overall',
                                 tables={'base': t1},
                                 pivot_column_name='db_process',
                                 ts_report_mod_name='appresponse_sql_ts')

report.add_widget(tables.TableWidget, t7, "SQL Overall",
                  width=12, height=0, searching=True)
