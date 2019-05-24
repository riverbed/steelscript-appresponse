
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseTimeSeriesTable

report = Report.create("AppResponse DB Sessions TimeSeries")

report.add_section()

t = AppResponseTable.create('db-session-overall', source='dbsession_summaries')
t.add_column('start_time', 'Time', datatype='time', iskey=True,
             extractor='start_time')
t.add_column('db_instance', 'DB Instance', datatype='string', iskey=True,
             extractor='db.instance')
t.add_column('active_sessions', 'Concurrent Active DB Sessions',
             datatype='float',
             extractor='avg_db.active_sessions')
t.add_column('active_time', 'Total Duration of Active Sessions',
             datatype='float',
             extractor='sum_db.session_active_time')

t1 = AppResponseTimeSeriesTable.create('db-sessions',
                                       tables={'base': t},
                                       pivot_column_label='DB Instances',
                                       pivot_column_name='db_instance',
                                       value_column_name='active_sessions')

report.add_widget(c3.TimeSeriesWidget, t1, 'Concurrent Active DB Sessions',
                  width=12)

t2 = AppResponseTimeSeriesTable.create('db-time',
                                       tables={'base': t},
                                       pivot_column_label='DB Instance',
                                       pivot_column_name='db_instance',
                                       value_column_name='active_time')
report.add_widget(c3.TimeSeriesWidget, t2, 'Total Duration of Active Sessions',
                  width=12)
