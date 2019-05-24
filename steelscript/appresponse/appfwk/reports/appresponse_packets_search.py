
# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables
from steelscript.appresponse.appfwk.datasources.appresponse import \
    AppResponseTable, AppResponseScannerTable

report = Report.create("AppResponse Packets - Search Capture Jobs",
                       hidden_fields=[
                           'appresponse_device',
                           'appresponse_source',
                           'entire_pcap',
                           'granularity'
                       ],
                       field_order=['endtime', 'duration'])

report.add_section()

# Create base table
base = AppResponseTable.create(name='ar_bytes', include_filter=True)
base.add_column('total_bytes', label='Bytes', iskey=False,
                extractor='sum_traffic.total_bytes')

# Make
table = AppResponseScannerTable.create(name='ars', basetable=base)
table.add_column('name', "Name", datatype='string')
table.add_column('host', "Host", datatype='string')
table.add_column('capture_job', "Capture Job", datatype='string')
table.add_column('bytes', "Bytes")

report.add_widget(tables.TableWidget, table, "AppResponse Capture Jobs Found",
                  width=12, height=0)
