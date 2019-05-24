
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.yui3 as yui3

from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseTimeSeriesTable

report = Report.create("AppResponse WTA Time Series")

report.add_section()

t = AppResponseTable.create('wta-base', source='aggregates')
t.add_column('start_time', 'Time', datatype='time', iskey=True,
             extractor='start_time')
t.add_column('page_family_id', 'Web Page Family ID', datatype='string',
             iskey=True, extractor='web.page.family.id')
t.add_column('page_family_name', 'Web Page Family Name', datatype='string',
             extractor='web.page.family.name')
t.add_column('pages', 'Number of Pages Viewed', datatype='integer',
             extractor='sum_web.pages')
t.add_column('page_bps', 'Average Page Throughput (BPS)',
             datatype='float', extractor='avg_web.traffic_bytes_ps')

t1 = AppResponseTimeSeriesTable.create('web-pages',
                                       tables={'base': t},
                                       pivot_column_label='App Names',
                                       pivot_column_name='page_family_name',
                                       value_column_name='pages')

report.add_widget(yui3.TimeSeriesWidget, t1, 'Number of Pages',
                  width=12)

t2 = AppResponseTimeSeriesTable.create('web-page-bps',
                                       tables={'base': t},
                                       pivot_column_name='page_family_name',
                                       value_column_name='page_bps')
report.add_widget(yui3.TimeSeriesWidget, t2, 'Average Page Throughput',
                  width=12)
