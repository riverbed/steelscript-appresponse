# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import copy
import logging
import datetime
import functools

import pandas

from steelscript.appfwk.apps.datasource.models import \
    DatasourceTable, TableQueryBase, Column, TableField

from steelscript.appfwk.apps.datasource.forms import \
    fields_add_time_selection
from steelscript.appfwk.apps.devices.models import Device

from steelscript.appfwk.apps.jobs import QueryComplete, QueryContinue

from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.libs.fields import Function
from steelscript.appresponse.appfwk.fields import \
    appresponse_source_choices, fields_add_granularity, \
    fields_add_filterexpr, fields_add_source_choices, fields_add_entire_pcap
from steelscript.appresponse.core.reports import \
    SourceProxy, DataDef, Report
from steelscript.appresponse.core.types import Key, Value, \
    AppResponseException, TrafficFilter
from steelscript.common.timeutils import datetime_to_seconds
from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisTable, AnalysisQuery
from steelscript.appfwk.apps.datasource.models import Table
from steelscript.appfwk.apps.jobs.models import Job
from functools import reduce

logger = logging.getLogger(__name__)

APP_LABEL = 'steelscript.appresponse.appfwk'


class AppResponseColumn(Column):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    # Notes:
    # 'extractor' defines the underlying column name for the Data Def

    # 'alias' indicates for a given key column, what the more descriptive
    # string alias column would be for it.  This actually results in the
    # query making a request for both columns, then overwriting the 'extractor'
    # column results with the 'alias' column results before handing back the
    # results.

    COLUMN_OPTIONS = {'extractor': None,
                      'alias': None}


class AppResponseTable(DatasourceTable):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    _column_class = 'AppResponseColumn'
    _query_class = 'AppResponseQuery'

    TABLE_OPTIONS = {'source': 'packets',
                     'include_files': False,
                     'include_msa_files_only': False,
                     'include_filter': False,
                     'show_entire_pcap': True,
                     'sort_col_name': None,
                     'ascending': False}

    FIELD_OPTIONS = {'duration': '15m',
                     'granularity': '1m'}

    def post_process_table(self, field_options):
        # Add a time selection field

        fields_add_device_selection(self, keyword='appresponse_device',
                                    label='AppResponse', module='appresponse',
                                    enabled=True)

        if self.options.source == 'packets':
            func = Function(appresponse_source_choices, self.options)
            fields_add_source_choices(self, func)

            if self.options.show_entire_pcap:
                fields_add_entire_pcap(self)

        if self.options.include_filter:
            fields_add_filterexpr(self)

        fields_add_granularity(self, initial=field_options['granularity'],
                               source=self.options.source)

        fields_add_time_selection(self, show_end=True,
                                  initial_duration=field_options['duration'])


class AppResponseQuery(TableQueryBase):

    def run(self):
        criteria = self.job.criteria

        ar = DeviceManager.get_device(criteria.appresponse_device)

        if self.table.options.source == 'packets':

            source_name = criteria.appresponse_source

            if source_name.startswith(SourceProxy.JOB_PREFIX):
                job_id = source_name.lstrip(SourceProxy.JOB_PREFIX)
                source = SourceProxy(ar.capture.get_job_by_id(job_id))
            else:
                file_id = source_name.lstrip(SourceProxy.FILE_PREFIX)
                source = SourceProxy(ar.fs.get_file_by_id(file_id))

        else:
            source = SourceProxy(name=self.table.options.source)

        col_extractors = []
        col_names = {}
        aliases = {}

        for col in self.table.get_columns(synthetic=False):
            col_names[col.options.extractor] = col.name

            if col.iskey:
                col_extractors.append(Key(col.options.extractor))
            else:
                col_extractors.append(Value(col.options.extractor))

            if col.options.alias:
                aliases[col.options.extractor] = col.options.alias
                col_extractors.append(Value(col.options.alias))

        # If the data source is of file type and entire PCAP
        # is set True, then set start end times to None

        if (self.table.options.source == 'packets' and
                source.path.startswith(SourceProxy.FILE_PREFIX) and
                criteria.entire_pcap):
            start = None
            end = None
        else:
            start = datetime_to_seconds(criteria.starttime)
            end = datetime_to_seconds(criteria.endtime)

        granularity = criteria.granularity.total_seconds()

        resolution = None

        # temp fix for https://bugzilla.nbttech.com/show_bug.cgi?id=305478
        # if we aren't asking for a timeseries, make sure the data gets
        # aggregated by making resolution greater than the report duration
        if (self.table.options.source == 'packets' and
                'start_time' not in col_names.keys() and
                'end_time' not in col_names.keys()):
            resolution = end - start + granularity

        data_def = DataDef(
            source=source,
            columns=col_extractors,
            granularity=granularity,
            resolution=resolution,
            start=start,
            end=end)

        if hasattr(criteria, 'appresponse_steelfilter'):
            logger.debug('calculating steelfilter expression ...')
            filterexpr = self.job.combine_filterexprs(
                exprs=criteria.appresponse_steelfilter
            )
            if filterexpr:
                logger.debug('applying steelfilter expression: %s'
                             % filterexpr)
                data_def.add_filter(TrafficFilter(type_='steelfilter',
                                                  value=filterexpr))

        report = Report(ar)
        report.add(data_def)
        report.run()

        df = report.get_dataframe()

        report.delete()

        if aliases:
            # overwrite columns with their alias values, then drop 'em
            for k, v in aliases.items():
                df[k] = df[v]
                df.drop(v, 1, inplace=True)

        df.columns = map(lambda x: col_names[x], df.columns)

        def to_int(x):
            return x if str(x).isdigit() else None

        def to_float(x):
            return x if str(x).replace('.', '', 1).isdigit() else None

        # Numerical columns can be returned as '#N/D' when not available
        # Thus convert them to None to help sorting
        for col in self.table.get_columns(synthetic=False):
            if col.datatype == Column.DATATYPE_FLOAT:
                df[col.name] = df[col.name].apply(lambda x: to_float(x))
            elif col.datatype == Column.DATATYPE_INTEGER:
                df[col.name] = df[col.name].apply(lambda x: to_int(x))
            elif col.datatype == Column.DATATYPE_TIME:
                if granularity < 1:
                    # The fractional epoch time values are in string
                    # Thus needs to be converted to float
                    df[col.name] = df[col.name].apply(float)

        if self.table.options.sort_col_name:
            df.sort(columns=self.table.options.sort_col_name,
                    ascending=self.table.options.ascending,
                    inplace=True)
        return QueryComplete(df)


class AppResponseTimeSeriesTable(AnalysisTable):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    _query_class = 'AppResponseTimeSeriesQuery'

    TABLE_OPTIONS = {'pivot_column_label': None,
                     'pivot_column_name': None,
                     'value_column_name': None,
                     'hide_pivot_field': False}

    def post_process_table(self, field_options):

        super(AppResponseTimeSeriesTable, self).\
            post_process_table(field_options)

        TableField.create(keyword='pivot_column_names',
                          required=not self.options.hide_pivot_field,
                          hidden=self.options.hide_pivot_field,
                          label=self.options.pivot_column_label, obj=self,
                          help_text='Name of Interested Columns '
                                    '(separated by ",")')

        self.add_column('time', 'time', datatype='time', iskey=True)


class AppResponseTimeSeriesQuery(AnalysisQuery):

    def analyze(self, jobs):
        # Based on input pivot column names, i.e. CIFS, RTP, Facebook
        # using dataframe keyed by Application ID, and start time
        # derive dataframe keyed by start_time, with each row as
        # a dictionary keyed by input pivot values

        df = jobs['base'].data()
        # First clear all the dynamic columns that were associated with
        # the table last time the report is run
        # do not delete the time column
        for col in self.table.get_columns():
            if col.name == 'time':
                continue
            col.delete()

        base_table = Table.from_ref(self.table.options.tables.base)

        time_col_name = None
        for col in base_table.get_columns():
            if col.datatype == Column.DATATYPE_TIME and col.iskey:
                time_col_name = col.name
                break

        if not time_col_name:
            raise AppResponseException("No key 'time' column defined "
                                       "in base table")

        pivot_column = self.table.options.pivot_column_name

        sub_dfs = []
        for pivot in self.job.criteria.pivot_column_names.split(','):
            # Add pivot column to the table
            pivot = pivot.strip()
            AppResponseColumn.create(self.table, pivot, pivot)

            # Add pivot column to the data frame
            sub_df = df[df[pivot_column] == pivot]

            # extract time column and value column
            sub_df = sub_df[[time_col_name,
                             self.table.options.value_column_name]]
            # Rename columns to 'time' and the pivot column name
            sub_df.rename(
                columns={time_col_name: 'time',
                         self.table.options.value_column_name: pivot},
                inplace=True
            )

            sub_dfs.append(sub_df)

        df_final = reduce(
            lambda df1, df2: pandas.merge(df1, df2, on='time', how='outer'),
            sub_dfs
        )

        return QueryComplete(df_final)


class AppResponseTopNTimeSeriesTable(AnalysisTable):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    _query_class = 'AppResponseTopNTimeSeriesQuery'

    TABLE_OPTIONS = {'n': 10,
                     'value_column_name': None,
                     'pivot_column_name': None}

    def post_process_table(self, field_options):

        # Use criteria as the overall table uses
        # to avoid showing pivot column names field
        super(AppResponseTopNTimeSeriesTable, self).\
            post_process_table(field_options)

        # Adding key column
        self.copy_columns(self.options.related_tables.ts)


class AppResponseTopNTimeSeriesQuery(AnalysisQuery):

    def analyze(self, jobs):

        df = jobs['overall'].data()

        # First clear all the dynamic columns that were associated with
        # the table last time the report is run
        # do not delete the time column
        for col in self.table.get_columns():
            if col.name == 'time':
                continue
            col.delete()

        # Get the top N values of the value column
        val_col = self.table.options.value_column_name
        pivot_col = self.table.options.pivot_column_name
        n = self.table.options.n

        pivots = list(df.sort_values(val_col, ascending=False)
                      .head(n)[pivot_col])

        for pivot in pivots:
            # Add pivot column to the table
            AppResponseColumn.create(self.table, pivot, pivot)

        # Create an AppResponseTimeSeries Job
        self.job.criteria.pivot_column_names = ','.join(pivots)
        ts_table_ref = self.table.options.related_tables['ts']
        table = Table.from_ref(ts_table_ref)

        job = Job.create(table=table,
                         criteria=self.job.criteria,
                         update_progress=False,
                         parent=self.job)

        return QueryContinue(self.collect, jobs={'ts': job})

    def collect(self, jobs):
        df = jobs['ts'].data()
        return QueryComplete(df)


class AppResponseLinkTable(AnalysisTable):
    """This analysis table derive the hyperlink columns using the base
    table value columns.
    """
    class Meta:
        proxy = True
        app_label = APP_LABEL

    _query_class = 'AppResponseLinkQuery'

    TABLE_OPTIONS = {'pivot_column_name': None,
                     'ts_report_mod_name': None}

    def post_process_table(self, field_options):
        self.copy_columns(self.options.tables.base)


class AppResponseLinkQuery(AnalysisQuery):

    def analyze(self, jobs):

        df = jobs['base'].data()

        criteria = self.job.criteria

        devid = criteria.appresponse_device
        duration = criteria.duration.seconds
        endtime = datetime_to_seconds(criteria.endtime)
        granularity = criteria.granularity.seconds

        def make_report_link(mod, v):
            s = ('<a href="/report/appresponse/{}/?'
                 'duration={}&appresponse_device={}&endtime={}&'
                 'pivot_column_names={}&granularity={}&auto_run=true" '
                 'target="_blank">{}</a>'
                 .format(mod, duration, devid, endtime, v,
                         granularity, v))
            return s

        make_report_link_with_mod = functools.partial(
            make_report_link, self.table.options.ts_report_mod_name)

        pivot_col = self.table.options.pivot_column_name
        df[pivot_col] = df[pivot_col].map(make_report_link_with_mod)

        return QueryComplete(df)


class AppResponseScannerTable(AnalysisTable):
    class Meta:
        proxy = True
        app_label = APP_LABEL

    _query_class = 'AppResponseScannerQuery'

    @classmethod
    def create(cls, name, basetable, **kwargs):
        kwargs['related_tables'] = {'basetable': basetable}
        return super(AppResponseScannerTable, cls).create(name, **kwargs)


class AppResponseScannerQuery(AnalysisQuery):
    def analyze(self, jobs):
        criteria = self.job.criteria

        ar_query_table = Table.from_ref(
            self.table.options.related_tables['basetable']
        )

        depjobs = {}

        # For every (ar, job), we spin off a new job to grab the data, then
        # merge everything into one dataframe at the end.
        for s in Device.objects.filter(module='appresponse', enabled=True):
            ar = DeviceManager.get_device(s.id)

            for job in ar.capture.get_jobs():
                # Start with criteria from the primary table -- this gives us
                # endtime, duration and filterexpr.
                bytes_criteria = copy.copy(criteria)
                bytes_criteria.appresponse_device = s.id
                bytes_criteria.appresponse_source = 'jobs/' + job.id
                bytes_criteria.granularity = datetime.timedelta(0, 1)

                newjob = Job.create(table=ar_query_table,
                                    criteria=bytes_criteria)

                depjobs[newjob.id] = newjob

        return QueryContinue(self.collect, depjobs)

    def collect(self, jobs=None):

        out = []
        for jid, job in jobs.items():
            ardata = job.data()
            if ardata is not None:
                total_bytes = ardata['total_bytes'].sum()
                if total_bytes:
                    s = Device.objects.get(id=job.criteria.appresponse_device)
                    out.append([s.name,
                                s.host,
                                job.criteria.appresponse_source,
                                total_bytes])

        if not out:
            out.append([
                'No capture jobs found', '--', '--', ''
            ])

        columns = ['name', 'host', 'capture_job', 'bytes']
        df = pandas.DataFrame(out, columns=columns)
        return QueryComplete(df)
