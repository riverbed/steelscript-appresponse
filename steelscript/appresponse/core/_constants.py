# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os

from collections import OrderedDict


# Using OrderedDict to ensure the ordering in GUI and CLI
# Mapping from group name to group title
report_groups = OrderedDict([
    ('packets', 'Packets'),
    ('asa', 'Application Stream Analysis'),
    ('wta', 'Web Transaction Analysis'),
    ('db', 'DB Analysis'),
    ('uc', 'UC Analysis')])

# Mapping from group title to group sources
# AR11_ADVANCED_FEATURES is a shell variable telling
# whether advanced sources should be exposed or not.

if os.environ.get('AR11_ADVANCED_FEATURES', 'False').lower() == 'true':
    report_sources = OrderedDict([
        ('packets', ['packets']),
        ('asa', ['aggregates', 'flow_tcp']),
        ('wta', ['aggregates', 'wtapages', 'wtapageobjects']),
        ('db',  ['dbsession_summaries', 'sql_summaries',
                 'sqlsessions', 'sqlqueries']),
        ('uc', ['aggregates', 'voip_rtp_channels', 'voip_calls'])])

else:
    report_sources = OrderedDict([
        ('packets', ['packets']),
        ('asa', ['aggregates']),
        ('wta', ['aggregates']),
        ('db', ['dbsession_summaries', 'sql_summaries']),
        ('uc', ['aggregates'])
    ])


# EXPERIMENT is a shell variable dictating whether to include
# sources from 'system' and 'other' group

if os.environ.get('AR11_EXPERIMENTAL_FEATURES', 'False').lower() == 'true':
    exp_groups = OrderedDict([
        ('system', 'System Metrics'),
        ('other', 'Other')])

    report_groups.update(exp_groups)

    exp_sources = OrderedDict([
        ('system', [
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
                   'system_metrics.tds']),
        ('other', ['alert_list']),
    ])

    report_sources.update(exp_sources)

report_source_to_groups = OrderedDict()
for group, sources in report_sources.iteritems():
    for source in sources:
        if source in report_source_to_groups:
            report_source_to_groups[source].append(report_groups[group])
        else:
            report_source_to_groups[source] = [report_groups[group]]
