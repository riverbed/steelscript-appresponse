
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

report = Report.create("AppResponse WTA Overall")

report.add_section()

# t1 is used to derive the overall metrics over the duration
t1 = AppResponseTable.create('wta-overall', source='aggregates',
                             sort_col_name='pages', ascending=False)
t1.add_column('page_family_id', 'Web Page Family ID',
              datatype='string', iskey=True,
              extractor='web.page.family.id')
t1.add_column('page_family_name', 'Web Page Family Name', datatype='string',
              extractor='web.page.family.name')
t1.add_column('pages', 'Number of Pages Viewed', datatype='integer',
              extractor='sum_web.pages')
t1.add_column('page_bps', 'Average Page Throughput (BPS)',
              datatype='float', extractor='avg_web.traffic_bytes_ps')

# t2 is used to derive the time series metrics values over the duration
t2 = AppResponseTable.create('wta-overall-ts', source='aggregates')
# Add this time key column is the main differentiator between t2 and t1
t2.copy_columns(t1)
t2.add_column('start_time', 'Time', datatype='time', iskey=True,
              extractor='start_time')

t3 = AppResponseTimeSeriesTable.create('wta-pages-ts',
                                       tables={'base': t2},
                                       pivot_column_name='page_family_name',
                                       value_column_name='pages',
                                       hide_pivot_field=True)

t4 = AppResponseTopNTimeSeriesTable.create(
    'wta-pages',
    tables={'overall': t1},
    related_tables={'ts': t3},
    pivot_column_name='page_family_name',
    value_column_name='pages',
    n=topn
)

report.add_widget(c3.TimeSeriesWidget, t4,
                  "Page Families/Top {} Pages Viewed".format(topn),
                  width=12)

t5 = AppResponseTimeSeriesTable.create('wta-page-bps-ts',
                                       tables={'base': t2},
                                       pivot_column_name='page_family_name',
                                       value_column_name='page_bps',
                                       hide_pivot_field=True)

t6 = AppResponseTopNTimeSeriesTable.create(
    'wta-page-bps',
    tables={'overall': t1},
    related_tables={'ts': t5},
    pivot_column_name='page_family_name',
    value_column_name='page_bps',
    n=topn
)

report.add_widget(c3.TimeSeriesWidget, t6,
                  "Apps/Top {} Page Throughput (BPS)".format(topn),
                  width=12)

t7 = AppResponseLinkTable.create('wta-link-overall',
                                 tables={'base': t1},
                                 pivot_column_name='page_family_name',
                                 ts_report_mod_name='appresponse_wta_ts')

report.add_widget(tables.TableWidget, t7, "WTA Overall",
                  width=12, height=0, searching=True)
