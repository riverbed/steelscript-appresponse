Changelog and Upgrades in 1.1
=============================

Changelog
---------

Support New Data Sources
^^^^^^^^^^^^^^^^^^^^^^^^

steelscript.appresponse 1.0 only supports reporting against packets sources, such as capture jobs,
clips and Pcap files. The 1.1 release adds support for reporting for all the remaining data
sources, which falls into groups such as **Application Stream Analysis**, **Web Transaction Analysis**,
**DB Analysis**, **UC Analysis**.

Add Example Script
^^^^^^^^^^^^^^^^^^

Add one example script ``general_report.py`` to demonstrate how to create report scripts to run against
general (non-packets) sources.

Add Command Script to Output Sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add one command script ``sources.py`` to output the names of all sources.

Update Command Script
^^^^^^^^^^^^^^^^^^^^^

The command script ``columns.py`` is updated to output columns information based on given source name.

Optimization
^^^^^^^^^^^^

- Optimize caching data from AppResponse
- Consolidate code to support reporting against both general sources and packets source in one module.

Upgrade
-------

If you have developed scripts or AppFwk reports using the previous steelscript.appresponse 1.0 library,
those need to be updated once steelscript.appresponse 1.1 is installed. The steps are as follows.

Add the following import statement in the module where DataDef object is created.

.. code-block:: python

   from steelscript.appresponse.core.reports import SourceProxy

Use a SourceProxy object when creating the DataDef object.

.. code-block:: python

   data_def = DataDef(source=SourceProxy(packets_source), ...)

where ``packets_source`` is a ``File`` object, a ``Job`` object or a ``Clip`` object.

