# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.appfwk.apps.report.modules.tables as tables
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable
from steelscript.appfwk.apps.datasource.modules.analysis import \
    FocusedAnalysisTable

report = Report.create("AppResponse Packets - Microburst and TCP Errors",
                       field_order=['endtime', 'duration',
                                    'appresponse_device',
                                    'appresponse_source',
                                    'entire_pcap', 'granularity'])

report.add_section()

# summary microbursts
p = AppResponseTable.create('MicroburstsTime',
                            duration='1 min', granularity='1s',
                            include_files=True)

p.add_column('time', label='Time', iskey=True, datatype='time',
             extractor='start_time', formatter='formatDateTimeMs')

p.add_column('max_microburst_1ms_bytes', label='uBurst 1ms',
             extractor='max_traffic.microburst_1ms_bytes', units='B')

p.add_column('max_microburst_10ms_bytes', label='uBurst 10ms',
             extractor='max_traffic.microburst_10ms_bytes', units='B')

p.add_column('max_microburst_100ms_bytes', label='uBurst 100ms',
             extractor='max_traffic.microburst_100ms_bytes', units='B')

report.add_widget(c3.TimeSeriesWidget, p,
                  'Microburst Timeseries (1s resolution)', width=6)
report.add_widget(tables.TableWidget, p,
                  'Microburst Bytes Summary', width=6)

# Detailed Microburst Template Table
# This uses finer grained microburst extractors

z = AppResponseTable.create('MicroburstsFocused')

z.add_column('time', label='Time', iskey=True, datatype='time',
             extractor='start_time', formatter='formatDateTimeMs')

z.add_column('max_microburst_1ms_bytes', label='uBurst 1ms',
             extractor='max_traffic.microburst_1ms_bytes', units='B')

z.add_column('max_microburst_10us_bytes', label='uBurst 10us',
             extractor='max_traffic.microburst_10us_bytes', units='B')

z.add_column('max_microburst_100us_bytes', label='uBurst 100us',
             extractor='max_traffic.microburst_100us_bytes', units='B')

# Local Max Microburst detail
a = FocusedAnalysisTable.create(name='max-focused-table-microburst',
                                max=True,
                                zoom_duration='1s',
                                zoom_resolution='1ms',
                                tables={'source': p},
                                related_tables={'template': z})
report.add_widget(c3.TimeSeriesWidget, a,
                  'Max Microburst Timeseries (1ms resolution)', width=6)
report.add_widget(tables.TableWidget, a,
                  'Max Microburst Bits Summary', width=6)

# TCP Errors Template Table
tcp = AppResponseTable.create('TCPErrors')

tcp.add_column('error_type', label='TCP Error Type', iskey=True,
               datatype='string',
               extractor='tcp.error_type', alias='tcp.error_type_name')
tcp.add_column('errors', label='TCP Error Count', datatype='integer',
               sortdesc=True, extractor='sum_tcp.errors')

# Local Min Microburst detail
a = FocusedAnalysisTable.create(name='max-focused-table-tcp',
                                max=True,
                                zoom_duration='1s',
                                zoom_resolution='1s',
                                tables={'source': p},
                                related_tables={'template': tcp})
report.add_widget(c3.BarWidget, a,
                  'TCP Errors @ Peak 1s Microburst', width=6, height=400)
report.add_widget(tables.TableWidget, a,
                  'TCP Errors Table @ Peak 1s Microburst', width=6, height=400)
