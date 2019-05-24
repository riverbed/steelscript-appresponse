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

report = Report.create("AppResponse Packets - DNS",
                       field_order=['endtime', 'duration',
                                    'appresponse_device',
                                    'appresponse_source',
                                    'entire_pcap', 'granularity'])

report.add_section()

# DNS Queries Over time
name = 'DNS Queries and Response Time Over Time'
p = AppResponseTable.create(name, include_files=True)

p.add_column('time', label='Time', iskey=True, datatype='time',
             extractor='start_time', formatter='formatDateTimeMs')
p.add_column('dns_count', label='DNS Query Count', datatype='integer',
             extractor='sum_dns.query.count')
p.add_column('dns_response_time', label='Avg DNS Response Time (ns)',
             units='ms', extractor='avg_dns.response_time')
report.add_widget(c3.TimeSeriesWidget, p, name, width=12,
                  altaxis=['dns_response_time'])

# DNS Response Code List for AR11
name = 'DNS Response Codes'
p = AppResponseTable.create(name)

p.add_column('dns_is_success', label='DNS Success', iskey=True,
             datatype='string',
             extractor='dns.is_success', alias='dns.is_success_name')
p.add_column('dns_total_queries', label='DNS Total Queries',
             datatype='integer', extractor='sum_dns.query.count',
             sortdesc=True)

report.add_widget(c3.PieWidget, p, name, width=6)

# DNS Query Type for AR11
name = 'DNS Query Type'
p = AppResponseTable.create(name)

p.add_column('dns_query_type', label='DNS Query Type', iskey=True,
             datatype='string',
             extractor='dns.query.type', alias='dns.query.type_name')
p.add_column('dns_total_queries', label='DNS Total Queries',
             datatype='integer', extractor='sum_dns.query.count',
             sortdesc=True)

report.add_widget(c3.PieWidget, p, name, width=6)


# DNS Request Details Table for AR11
name = 'Top 100 DNS Requests'
p = AppResponseTable.create(name, rows=100)

p.add_column('dns_query_name', label='DNS Request', iskey=True,
             datatype='string', extractor='dns.query.name')
p.add_column('dns_is_success', label='Query Result', iskey=True,
             datatype='string',
             extractor='dns.is_success', alias='dns.is_success_name')
p.add_column('dns_query_count', label='# Requests',
             datatype='integer', extractor='sum_dns.query.count',
             sortdesc=True)

report.add_widget(tables.TableWidget, p, name, width=12)
