
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseTimeSeriesTable

report = Report.create("AppResponse UC Time Series")

report.add_section()

t = AppResponseTable.create('uc-base', source='aggregates')
t.add_column('start_time', 'Time', datatype='time', iskey=True,
             extractor='start_time')
t.add_column('media_type', 'Media Type ID', datatype='string',
             iskey=True, extractor='rtp.media_type')
t.add_column('media_type_name', 'Media Type Name', datatype='string',
             extractor='rtp.media_type_name')
t.add_column('packets', 'Number of RTP Packets', datatype='integer',
             extractor='sum_rtp.packets')
t.add_column('bytes', 'Number of RTP Packets',
             datatype='float', extractor='sum_rtp.traffic_bytes')

t1 = AppResponseTimeSeriesTable.create('uc-packets',
                                       tables={'base': t},
                                       pivot_column_label='Media Types',
                                       pivot_column_name='media_type_name',
                                       value_column_name='packets')

report.add_widget(c3.TimeSeriesWidget, t1, 'Number of Packets',
                  width=12)

t2 = AppResponseTimeSeriesTable.create('uc-bytes',
                                       tables={'base': t},
                                       pivot_column_label='Media Types',
                                       pivot_column_name='media_type_name',
                                       value_column_name='bytes')
report.add_widget(c3.TimeSeriesWidget, t2, 'Number of Bytes',
                  width=12)
