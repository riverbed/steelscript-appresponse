# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging
import threading

from django import forms

from steelscript.appfwk.apps.datasource.forms import \
    DurationField, IDChoiceField
from steelscript.appfwk.apps.datasource.models import TableField
from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appresponse.core.reports import SourceProxy


logger = logging.getLogger(__name__)
lock = threading.Lock()


def appresponse_source_choices(form, id_, field_kwargs, params):
    """ Query AppResponse for available capture jobs / files."""

    # most of these results will be cached by the underlying AR object

    ar_id = form.get_field_value('appresponse_device', id_)

    with lock:
        if ar_id == '':
            choices = [('', '<No AppResponse Device>')]

        else:
            ar = DeviceManager.get_device(ar_id)

            choices = []

            for job in ar.capture.get_jobs():
                if job.status == 'RUNNING':
                    choices.append((SourceProxy(job).path, job.name))

            for clip in ar.clips.get_clips():
                choices.append((SourceProxy(clip).path, clip.name))

            if params['include_files']:
                for f in ar.fs.get_files():
                    choices.append((SourceProxy(f).path, f.id))

            if params['include_msa_files_only']:
                choices = []
                for f in ar.fs.get_files(force=True):
                    if f.is_msa():
                        choices.append((SourceProxy(f).path, f.id))

    field_kwargs['label'] = 'Source'
    field_kwargs['choices'] = choices


def fields_add_granularity(obj, initial=None, source=None):

    if source == 'packets':
        granularities = ('0.001', '0.01', '0.1', '1', '10', '60', '600',
                         '3600', '86400')
    else:
        granularities = ('60', '600', '3600', '86400')

    field = TableField(keyword='granularity',
                       label='Granularity',
                       field_cls=DurationField,
                       field_kwargs={'choices': granularities},
                       initial=initial)
    field.save()
    obj.fields.add(field)


def fields_add_filterexpr(table, keyword='appresponse_steelfilter',
                          initial=None):
    field = TableField(keyword=keyword,
                       label='SteelFilter Expression',
                       help_text='Traffic expression using '
                                 'SteelFilter syntax, e.g. '
                                 'ip.addr == "10.0.0.1" or '
                                 'avg_traffic.total_ bytes_ps <= 10000',
                       initial=initial,
                       required=False)
    field.save()
    table.fields.add(field)


def fields_add_source_choices(table, func, keyword='appresponse_source',
                              label='Source', initial=None):
    TableField.create(
        keyword=keyword, label=label,
        obj=table,
        field_cls=IDChoiceField,
        field_kwargs={'widget_attrs': {'class': 'form-control'}},
        parent_keywords=['appresponse_device'],
        initial=initial,
        dynamic=True,
        pre_process_func=func
    )


def fields_add_entire_pcap(table):
    TableField.create(
        keyword='entire_pcap', obj=table,
        field_cls=forms.BooleanField,
        label='Entire File',
        help_text='Ignore start/end times '
                  'and run the report over the '
                  'whole timeframe of the selected '
                  'file.',
        initial=True,
        required=False
    )
