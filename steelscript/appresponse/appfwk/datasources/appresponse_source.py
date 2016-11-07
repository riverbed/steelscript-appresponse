# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a data source for querying data.

There are three parts to defining a data source:

* Defining column options via a Column class
* Defining table options via a DatasourceTable
* Defining the query mechanism via a Query class

Note that you can define multiple Column and Table classes
in the same file. Each Table class needs to associate with a
Query class by specifying the _query_class attribute.

"""

import logging
import pandas

from steelscript.common.timeutils import \
    datetime_to_seconds, timedelta_total_seconds, parse_timedelta

from steelscript.appfwk.apps.datasource.models import \
    DatasourceTable, Column

from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisTable, AnalysisQuery

from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.datasource.forms import (fields_add_time_selection,
                                                      fields_add_resolution)
from steelscript.appfwk.apps.datasource.models import TableQueryBase

from steelscript.appresponse.core.appresponse import Appresponse

logger = logging.getLogger(__name__)


#
# Define a custom Column class
#
# This allows defintion of custom column options that may
# be set in reports.
#
# Use of this class is entirely optional, it may be deleted
# if there are no custom column options

class AppresponseColumn(Column):
    class Meta:
        proxy = True

    # COLUMN_OPTIONS is a dictionary of options that
    # are specific to columns for tables in this file.
    # the column options are available when the query is run.
    # The values are stored with the column definition at
    # table / column defintiion time.

    COLUMN_OPTIONS = { }


#
# Define a custom AppresponseTable
#
class AppresponseTable(DatasourceTable):

    class Meta:
        proxy = True

    # When a custom column is used, it must be linked
    _column_class = 'AppresponseColumn'

    # Name of the query class to extract data
    _query_class = 'AppresponseQuery'

    # TABLE_OPTIONS is a dictionary of options that are
    # specific to AppresponseQuery objects.  These will be overriden by
    # keyword arguments to the AppresponseTable.create() call in a report
    # file
    TABLE_OPTIONS = { }

    # FIELD_OPTIONS is a dictionary of default values for field
    # options.  These by be overriden by keyword arguments to the
    # AppresponseTable.create() call in a report file
    FIELD_OPTIONS = { }


    def post_process_table(self, field_options):
        #
        # Add criteria fields that are required by this table
        #
        pass


#
# The AppresponseQuery class must be defined with the __init__ and run
# method taking the defined arguments
#
class AppresponseQuery(TableQueryBase):

    def __init__(self, table, job):
        self.table = table
        self.job = job

        # Perform any additional query initialization here

    def run(self):
        # This method is called to actually execute the query
        # for the given table and job.  This is executed in a separate
        # thread and must not return until either the query completes
        # and data is available, or the query fails and returns an error.
        #
        # On success, this function should return either a list of lists
        # of data aligned to the set of non-synthetic columns associated
        # with this table or a pandas DataFrame with matching columns.
        # (synthetic columns are computed by automatically one the query
        # completes)
        #
        # On error, any errors that are not programmatic (like bad
        # criteria values) should be reported by calling
        # self.job.mark_error() with a user-friendly error message
        # indicating the cause of the failure.
        #
        # Any programmatic errors should be raised as exceptions.
        #
        # For long running queries self.job.mark_progress() should
        # be called to update the progress from 0 to 100 percent complete.

        # All user entered criteria is available directly from this object.
        # Values for any fields added to the table will appear as
        # attributes according to the field keyword.
        criteria = self.job.criteria

        # Perform the query of data here.  Save the result in self.data
        # The result must be either a list of lists (list of rows, each row
        # is a list of columns), or a Pandas DataFrame.
        self.data = None

        # If all went well, return True
        return True
