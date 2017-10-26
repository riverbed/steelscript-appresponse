# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

# Define report groups to ensure the ordering in GUI
report_groups = ['Packets',
                 'Application Stream Analysis',
                 'Web Transaction Analysis',
                 'DB Analysis',
                 'UC Analysis',
                 'System Metrics',
                 'Other']


report_sources = {
    'Packets': ['packets'],
    'Application Stream Analysis': ['aggregates', 'flow_tcp'],
    "Web Transaction Analysis": ['aggregates', 'wtapages', 'wtapageobjects'],
    "DB Analysis": ['dbsession_summaries', 'sql_summaries',
                    'sqlsessions', 'sqlqueries'],
    'UC Analysis': ['aggregates', 'voip_rtp_channels', 'voip_calls'],
    'System Metrics': [
               'system_metrics.mipmaps',
               'system_metrics.cpu',
               'system_metrics.chassis',
               'system_metrics.capture_job',
               'system_metrics.diskio',
               'system_metrics.dbperf',
               'system_metrics.npqueuedump',
               'system_metrics.connections',
               'system_metrics.threads',
               'system_metrics.capture',
               'system_metrics.capture_interface',
               'system_metrics.stitcher',
               'system_metrics.vmstat',
               'system_metrics.filters',
               'system_metrics.probe',
               'system_metrics.processes',
               'system_metrics.loggers',
               'system_metrics.profiler_export',
               'system_metrics.capture_slabpool',
               'system_metrics.report_manager',
               'system_metrics.mysqladmin',
               'system_metrics.swap',
               'system_metrics.disk',
               'system_metrics.memory',
               'system_metrics.tds'],
    'Other': ['tdstest', 'alert_list'],
}

# Consolidate source names into one list
report_source_names = set([])

for sources in report_sources.values():
    report_source_names = report_source_names.union(set(tuple(sources)))

report_source_names = list(report_source_names)
