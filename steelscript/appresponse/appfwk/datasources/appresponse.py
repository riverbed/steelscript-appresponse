# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from django import forms

from steelscript.appfwk.apps.datasource.models import \
    DatasourceTable, TableQueryBase, Column, TableField

from steelscript.appfwk.apps.datasource.forms import \
    fields_add_time_selection, DurationField

from steelscript.appfwk.apps.jobs import QueryComplete

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.libs.fields import Function
from steelscript.appfwk.apps.datasource.forms import IDChoiceField
from steelscript.appresponse.core.reports import \
    SourceProxy, DataDef, Report
from steelscript.appresponse.core.types import Key, Value
from steelscript.common.timeutils import datetime_to_seconds
from steelscript.appresponse.core.fs import File

logger = logging.getLogger(__name__)

APP_LABEL = 'steelscript.appresponse.appfwk'


class AppResponseColumn(Column):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    COLUMN_OPTIONS = {'extractor': None}


def appresponse_source_choices(form, id_, field_kwargs, params):
    """ Query AppResponse for available capture jobs / files."""

    ar_id = form.get_field_value('appresponse_device', id_)
    if ar_id == '':
        choices = [('', '<No AppResponse Device>')]
    else:
        ar = DeviceManager.get_device(ar_id)

        choices = []

        for job in ar.capture.get_jobs():
            if job.status == 'RUNNING':
                choices.append((SourceProxy(job).path, job.name))

        if params['include_files']:
            for f in ar.fs.get_files():
                choices.append((SourceProxy(f).path, f.id))

    field_kwargs['label'] = 'Source'
    field_kwargs['choices'] = choices


def fields_add_granularity(obj, initial=None, granularities=None):

    if granularities is None:
        granularities = ('1s', '10s', '1m', '10m', '1h')

    field = TableField(keyword='granularity',
                       label='Granularity',
                       field_cls=DurationField,
                       field_kwargs={'choices': granularities},
                       initial=initial)
    field.save()
    obj.fields.add(field)


class AppResponseTable(DatasourceTable):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    _column_class = 'AppResponseColumn'
    _query_class = 'AppResponseQuery'

    TABLE_OPTIONS = {'include_files': False,
                     'show_entire_pcap': True}

    FIELD_OPTIONS = {'duration': '1m',
                     'granularity': '1s'}

    def post_process_table(self, field_options):
        # Add a time selection field

        fields_add_device_selection(self, keyword='appresponse_device',
                                    label='AppResponse', module='appresponse',
                                    enabled=True)

        func = Function(appresponse_source_choices,
                        self.options)

        TableField.create(
            keyword='appresponse_source', label='Source',
            obj=self,
            field_cls=IDChoiceField,
            field_kwargs={'widget_attrs': {'class': 'form-control'}},
            parent_keywords=['appresponse_device'],
            dynamic=True,
            pre_process_func=func
        )

        fields_add_time_selection(self, show_end=True,
                                  initial_duration=field_options['duration'])

        fields_add_granularity(self, initial=field_options['granularity'])

        if self.options.show_entire_pcap:
            TableField.create(keyword='entire_pcap', obj=self,
                              field_cls=forms.BooleanField,
                              label='Entire PCAP',
                              initial=True,
                              required=False)


class AppResponseQuery(TableQueryBase):

    def run(self):
        criteria = self.job.criteria

        ar = DeviceManager.get_device(criteria.appresponse_device)

        source_path = criteria.appresponse_source

        if source_path.startswith(SourceProxy.JOB_PREFIX):
            job_id = source_path.lstrip(SourceProxy.JOB_PREFIX)
            source = ar.capture.get_job_by_id(job_id)
        else:
            file_id = source_path.lstrip(SourceProxy.FILE_PREFIX)
            source = ar.fs.get_file_by_id(file_id)

        col_extractors, col_names = [], {}

        for col in self.table.get_columns(synthetic=False):
            col_names[col.options.extractor] = col.name

            if col.iskey:
                col_extractors.append(Key(col.options.extractor))
            else:
                col_extractors.append(Value(col.options.extractor))

        # If the data source is of file type and entire PCAP
        # is set True, then set start end times to None

        if isinstance(source, File) and criteria.entire_pcap:
            start = None
            end = None
        else:
            start = datetime_to_seconds(criteria.starttime)
            end = datetime_to_seconds(criteria.endtime)

        data_def = DataDef(source=SourceProxy(source),
                           columns=col_extractors,
                           granularity=criteria.granularity.total_seconds(),
                           start=start,
                           end=end)

        report = Report(ar)
        report.add(data_def)
        report.run()

        df = report.get_dataframe()
        df.columns = map(lambda x: col_names[x], df.columns)
        return QueryComplete(df)
