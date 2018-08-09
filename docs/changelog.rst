Changelog and Upgrades in 2.0
=============================

Changelog
---------

Backwards incompatible release for AR 11.5.

This release adds support for the new Virtual Interface Groups introduced in 11.5

Upgrades
--------

This package will not be able to run reports against older versions of
AppResponse.  In order to communicate in a mixed environment, separate
SteelScript installations will be needed until the migrations are completed.

Reporting scripts should be largely unaffected as the MIFG to VIFG changes are
handled within the SDK.  Any specific references to MIFGs will need to be
updated to the new VIFG class instead.

Changelog and Upgrades in 1.3
=============================

Changelog
---------

 * Add support for topby columns and limit
 * Handle corrupted ServiceDef caches
 * Add get_instances method to retrieve all running reports
 * Add example clean_report_instances.py script

Upgrades
--------

None.

Changelog and Upgrades in 1.2
=============================

Changelog
---------

 * Add App Framework support for all data sources
 * Documentation updates
 * Better support for sources and columns caching
 * Bug fixes

 * Support filters for reports
 * Reports for non-packets sources
 * Add/update command scripts
 * Add general_reports.py script

Upgrades
--------

None.


Changelog and Upgrades in 1.1
=============================

Changelog
---------

Support New Data Sources
^^^^^^^^^^^^^^^^^^^^^^^^

The 1.1 release adds support for reporting against for all data sources, which
falls into groups such as **Application Stream Analysis**, **Web Transaction
Analysis**, **DB Analysis**, **UC Analysis**.


 - Add example script ``general_report.py`` to demonstrate how to create report
   scripts to run against general (non-packets) sources
 - Add command script ``sources.py`` to output the names of all sources
 - Update command script ``columns.py`` to output columns information based on
   given source name
 - Optimize caching data from AppResponse
 - Consolidate code to support reporting against both general sources and
   packets source in one module.

Upgrades
--------

If you have developed scripts or AppFwk reports using the previous steelscript.appresponse 1.0 library,
those need to be updated once steelscript.appresponse 1.1 is installed. The steps are as follows.

Add the following import statement in the module where DataDef object is created.

.. code-block:: python

   from steelscript.appresponse.core.reports import SourceProxy

Use a SourceProxy object when creating the DataDef object.

.. code-block:: python

   data_def = DataDef(source=SourceProxy(packets_source), ...)

where ``packets_source`` is a ``File`` object, a ``Job`` object or a ``Clip`` object.

