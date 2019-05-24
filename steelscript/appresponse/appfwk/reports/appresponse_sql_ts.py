
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseTimeSeriesTable

report = Report.create("AppResponse SQL TimeSeries")

report.add_section()

t = AppResponseTable.create('SQL-overall', source='sql_summaries')
t.add_column('start_time', 'Time', datatype='time', iskey=True,
             extractor='start_time')
t.add_column('db_process', 'Client Process Name', datatype='string',
             iskey=True,
             extractor='db.process_name')
t.add_column('sql_duration', 'Transaction Time',
             datatype='float',
             extractor='avg_sql.duration')
t.add_column('sql_packets', 'Average Packets',
             datatype='float',
             extractor='avg_sql.packets')

t1 = AppResponseTimeSeriesTable.create('sql-duration-ts',
                                       tables={'base': t},
                                       pivot_column_label='SQL Process Names',
                                       pivot_column_name='db_process',
                                       value_column_name='sql_duration')

report.add_widget(c3.TimeSeriesWidget, t1,
                  'Average Transaction Time (Seconds)',
                  width=12)

t2 = AppResponseTimeSeriesTable.create('sql-packets',
                                       tables={'base': t},
                                       pivot_column_label='SQL Process Names',
                                       pivot_column_name='db_process',
                                       value_column_name='sql_packets')

report.add_widget(c3.TimeSeriesWidget, t2, 'Average SQL Packets',
                  width=12)
