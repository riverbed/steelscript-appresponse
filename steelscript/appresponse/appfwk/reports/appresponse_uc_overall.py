
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

report = Report.create("AppResponse UC Overall")

report.add_section()

# t1 is used to derive the overall metrics over the duration
t1 = AppResponseTable.create('uc-overall', source='aggregates')
t1.add_column('media_type', 'Media Type ID', datatype='string', iskey=True,
              extractor='rtp.media_type')
t1.add_column('media_type_name', 'Media Type Name', datatype='string',
              extractor='rtp.media_type_name')
t1.add_column('packets', 'Number of RTP Packets', datatype='integer',
              extractor='sum_rtp.packets')
t1.add_column('bytes', 'Number of RTP Bytes',
              datatype='integer', extractor='sum_rtp.traffic_bytes')

# t2 is used to derive the time series metrics values over the duration
t2 = AppResponseTable.create('uc-overall-ts', source='aggregates')
# Add this time key column is the main differentiator between t2 and t1
t2.copy_columns(t1)
t2.add_column('start_time', 'Time', datatype='time', iskey=True,
              extractor='start_time')

t3 = AppResponseTimeSeriesTable.create('uc-packets-ts',
                                       tables={'base': t2},
                                       pivot_column_name='media_type_name',
                                       value_column_name='packets',
                                       hide_pivot_field=True)

t4 = AppResponseTopNTimeSeriesTable.create('uc-packets',
                                           tables={'overall': t1},
                                           related_tables={'ts': t3},
                                           pivot_column_name='media_type_name',
                                           value_column_name='packets',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t4,
                  "RTP Packets/Top {} Media Type".format(topn),
                  width=12)

t5 = AppResponseTimeSeriesTable.create('uc-bytes-ts',
                                       tables={'base': t2},
                                       pivot_column_name='media_type_name',
                                       value_column_name='bytes',
                                       hide_pivot_field=True)

t6 = AppResponseTopNTimeSeriesTable.create('uc-bytes',
                                           tables={'overall': t1},
                                           related_tables={'ts': t5},
                                           pivot_column_name='media_type_name',
                                           value_column_name='bytes',
                                           n=topn)

report.add_widget(c3.TimeSeriesWidget, t6,
                  "RTP Bytes/Top {} Media Type".format(topn),
                  width=12)

t7 = AppResponseLinkTable.create('uc-link-overall',
                                 tables={'base': t1},
                                 pivot_column_name='media_type_name',
                                 ts_report_mod_name='appresponse_uc_ts')

report.add_widget(tables.TableWidget, t7, "UC Overall",
                  width=12, height=0, searching=True)
