.. py:currentmodule:: steelscript.appresponse.core

SteelScript AppResponse Packets Report Tutorial
===============================================

This tutorial will show you how to run a packets report against
an AppResponse appliance using SteelScript for Python.
This tutorial assumes a basic understanding of Python.

The tutorial has been organized so you can follow it sequentially.
Throughout the example, you will be expected to fill in details
specific to your environment.  These will be called out using a dollar
sign ``$<name>`` -- for example ``$host`` indicates you should fill
in the host name or IP address of an AppResponse appliance.

Whenever you see ``>>>``, this indicates an interactive session using
the Python shell.  The command that you are expected to type follows
the ``>>>``.  The result of the command follows.  Any lines with a
``#`` are just comments to describe what is happening.  In many cases
the exact output will depend on your environment, so it may not match
precisely what you see in this tutorial.

AppResponse Object
------------------

As with any Python code, the first step is to import the module(s) to
be used. The SteelScript code for working with AppResponse
appliances resides in a module called
:py:mod:`steelscript.appresponse.core`.  The main class in this module is
:py:class:`AppResponse <steelscript.netshark.core.AppResponse>`.
This object represents a connection to an AppResponse appliance.

To start, start python from the shell or command line:

.. code-block:: bash

   $ python
   Python 2.7.13 (default, Apr  4 2017, 08:47:57)
   [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.38)] on darwin
   Type "help", "copyright", "credits" or "license" for more information.
   >>>

Once in the python shell, let's create an AppReponse object:

.. code-block:: python

   >>> from steelscript.appresponse.core import AppResponse
   >>> from steelscript.common import UserAuth

   >>> ar = AppResponse('$host', auth=UserAuth('$username', '$password'))

The first argument is the hostname or IP address of the AppResponse
appliance.  The second argument is a named parameter and identifies
the authentication method to use -- in this case, simple
username/password is used.

As soon as the AppResponse object is created, a connection is established
to the AppResponse appliance, and the authentication credentials are
validated.  If the username and password are not correct, you will
immediately see an exception.

The ``ar`` object is the basis for all communication with the AppResponse
appliance, whether that is running a report, updating host groups or
downloading a pcap file. Now lets take a look at the basic information
of the AppResponse appliance that we just connected to:

.. code-block:: python

   >>> info = ar.get_info()

   >>> info['model']
   u'VSCAN-2000'

   >>> info['sw_version']
   u'11.2.0 #13859'

   # Let's see the entire info structure
   >>> info
   {u'device_name': u'680-valloy1',
    u'hw_version': u'',
    u'mgmt_addresses': [u'10.33.158.77'],
    u'model': u'VSCAN-2000',
    u'serial': u'',
    u'sw_version': u'11.2.0 #13859'}


Packets Report
--------------

Let's create our first script. We're going to write a simple script that
runs a report against a packets capture job on our AppResponse
appliance.

This script will get packets from a running packets capture job. To start,
make sure the targeted AppResponse appliance has a running packets
capture job.

Now create a file called ``report.py`` and insert the following code:

.. code-block:: python

   import pprint

   from steelscript.appresponse.core.appresponse import AppResponse
   from steelscript.common import UserAuth
   from steelscript.appresponse.core.reports import DataDef, Report
   from steelscript.appresponse.core.types import Key, Value

   # Fill these in with appropriate values
   host = '$host'
   username = '$username'
   password = '$password'

   # Open a connection to the appliance and authenticate
   ar = AppResponse(host, auth=UserAuth(username, password))

   source = ar.get_capture_job_by_name('default_job')

   columns = [Key('start_time'), Value('sum_tcp.total_bytes'), Value('avg_frame.total_bytes')]

   granularity = '10'

   time_range = 'last 1 minute'

   data_def = DataDef(source=source, columns=columns, granularity='10', time_range=time_range)

   report = Report(ar)
   report.add(data_def)
   report.run()
   pprint.pprint(report.get_data())

Be sure to fill in appropriate values for ``$host``, ``$username`` and
``$password``. Run this script as follows and you should see something
like the following:

.. code-block:: bash

   $ python report.py
   [(u'1501610710', 4272341.0, 245.138),
    (u'1501610720', 4130029.0, 255.536),
    (u'1501610730', 4391768.0, 263.485),
    (u'1501610740', 4560534.0, 260.836),
    (u'1501610750', 4110080.0, 254.337),
    (u'1501610760', 2802668.0, 251.946)]

Let's take a closer look at what this script is doing. The first few
lines are simply importing a few libraries that we will be using:

.. code-block:: python

   import pprint

   from steelscript.appresponse.core.appresponse import AppResponse
   from steelscript.common import UserAuth
   from steelscript.appresponse.core.reports import DataDef, Report
   from steelscript.appresponse.core.types import Key, Value

Next, we create an AppResponse object that establishes our connection to
the target appliance:

.. code-block:: python

   # Open a connection to the appliance and authenticate
   ar = AppResponse(host, auth=UserAuth(username, password))

The next section describes how to create a data definition object.

.. code-block:: python

   source = ar.get_capture_job_by_name('default_job')

   columns = [Key('start_time'), Value('sum_tcp.total_bytes'), Value('avg_frame.total_bytes')]

   granularity = '10'

   time_range = 'last 1 minute'

   data_def = DataDef(source=source, columns=columns, granularity='10', time_range=time_range)

We first obtain a packet capture job object by using the name of the capture job.
To run a report against a pcap file source, the file object can be derived as below:

.. code-block:: python

   source = ar.get_file_by_id('$file_id')

Then we select the set of columns that we are interested in collecting. Note
that AppResponse supports numerous columns and any column can be either a key
column or a value column. Each row of data will be aggregated according to the
set of key columns selected. The value columns define the set of additional
data to collect per row. In this example, we are asking to collect total bytes
for tcp packets and average total packet length for each resolution bucket.

To help identify which columns are available, we could execute the helper command
as below.

.. code-block:: bash

   steel appresponse columns $hostname -u $usernmae -p $password


Setting granularity to ``10`` precision means the data source computes a
summary of the metrics it received based on intervals of ``10`` seconds.

The parameter ``time_range`` specifies the time range for which the data source computes
the metrics. Other valid formats include ``this minute``, ``previous hour`` and
``06/05/17 17:09:00 to 06/05/17 18:09:00``.

After creating the data definition object, then we are ready to run a report as below:

.. code-block:: python

   # Initialize a new report
   report = Report(ar)

   # Add one data definition object to the report
   report.add(data_def)

   # Run the report
   report.run()

   # Grab the data
   pprint.pprint(report.get_data())

Extending the Example
---------------------

As a last item to help get started with your own scripts, we will extend our example
with one helpful feature: table outputs.

Rather than show how to update your existing example script, we will post the new
script, then walk through key differences that add the feature.

Let us create a file ``table_report.py`` and insert the following code:

.. code-block:: python

   from steelscript.appresponse.core.appresponse import AppResponse
   from steelscript.common import UserAuth
   from steelscript.appresponse.core.reports import DataDef, Report
   from steelscript.appresponse.core.types import Key, Value

   # Import the Formatter class to output data in a table format
   from steelscript.common.datautils import Formatter

   # Fill these in with appropriate values
   host = '$host'
   username = '$username'
   password = '$password'

   # Open a connection to the appliance and authenticate
   ar = AppResponse(host, auth=UserAuth(username, password))

   source = ar.get_capture_job_by_name('default_job')

   columns = [Key('start_time'), Value('sum_tcp.total_bytes'), Value('avg_frame.total_bytes')]

   granularity = '10'

   time_range = 'last 1 minute'

   data_def = DataDef(source=source, columns=columns, granularity='10', time_range=time_range)

   report = Report(ar)
   report.add(data_def)
   report.run()

   # Get the header of the table
   header = report.get_legend()

   data = report.get_data()

   # Output the data in a table format
   Formatter.print_table(data, header)

Be sure to fill in appropriate values for ``$host``, ``$username`` and
``$password``. Run this script as follows and you should see report
result is rendered in a table format as the following:

.. code-block:: bash

   $ python table_report.py

    start_time    sum_tcp.total_bytes    avg_frame.total_bytes
    --------------------------------------------------------------
    1501681110    4286398.0              267.309
    1501681120    4825195.0              360.635
    1501681130    6252248.0              468.954
    1501681140    4741664.0              332.374
    1501681150    4386239.0              282.895
    1501681160    476495.0               292.533

As can be seen from the script, there are 3 differences.

First, we import the ``Formatter`` class as below:

.. code-block:: python

   from steelscript.common.datautils import Formatter

After the report finished running, we obtain the header of the
table, which is essentially a list of column names that match the
report result, shown as below:

.. code-block:: python

   header = report.get_legend()

At last, the ``Formatter`` class is used to render the report result in
a nice table format, shown as below:

.. code-block:: python

   Formatter.print_table(data, header)

