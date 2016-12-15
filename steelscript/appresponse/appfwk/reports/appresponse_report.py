# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a single report of multiple tables and widgets.

The typical structure is as follows:

    report = Report.create('Appresponse Report')
    report.add_section()

    table = SomeTable.create(name, table_options...)
    table.add_column(name, column_options...)
    table.add_column(name, column_options...)
    table.add_column(name, column_options...)

    report.add_widget(yui3.TimeSeriesWidget, table, name, width=12)

See the documeantion or sample plugin for more details
"""
#
# import steelscript.appfwk.apps.datasource.modules.analysis as analysis
# from steelscript.appfwk.apps.report.models import Report
# from steelscript.appfwk.apps.datasource.models import Column, TableField
# import steelscript.appfwk.apps.report.modules.yui3 as yui3
#
# # Import the datasource module for this plugin (if needed)
# import steelscript.appresponse.appfwk.datasources.appresponse_source as appresponse
