Example Script Walkthroughs
===========================

The SteelScript AppResponse package includes several example scripts to help
get started quickly with common operations and useful code to customize
for specific situations.  This guide will provide a summary of the scripts along
with some example command-lines and the associated output.

These example scripts can be found in your SteelScript workspace, see
:ref:`steel_mkworkspace` for a guide on how to create a new workspace in your
environment.  Alternatively, they can be found inside the `GitHub repository
<https://github.com/riverbed/steelscript-appresponse/tree/master/examples>`_.

Conventions and Common Arguments
--------------------------------

Throughout this discussion we will be showing the results of ``--help`` options
for each of the scripts where they vary from the core set.  All of the scripts
take the same core set of options and arguments as follows:

.. code-block:: none

    Usage: <SCRIPT_NAME> <HOST> [options] ...

    Required Arguments:
      HOST        AppResponse hostname or IP address

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit

      Logging Parameters:
        --loglevel=LOGLEVEL
                            log level: debug, warn, info, critical, error
        --logfile=LOGFILE   log file, use '-' for stdout

      Connection Parameters:
        -P PORT, --port=PORT
                            connect on this port
        -u USERNAME, --username=USERNAME
                            username to connect with
        -p PASSWORD, --password=PASSWORD
                            password to connect with
        --oauth=OAUTH       OAuth Access Code, in place of username/password
        -A API_VERSION, --api_version=API_VERSION
                            api version to use unconditionally

      REST Logging:
        --rest-debug=REST_DEBUG
                            Log REST info (1=hdrs, 2=body)
        --rest-body-lines=REST_BODY_LINES
                            Number of request/response body lines to log

This example output has no specific options to the script.  To execute this
script, use the following syntax::

    $ <SCRIPT_NAME> ar11.example.com -u admin -p admin

That typically provides the bare minimum options for execution: the hostname,
and username/password combination.

Also, we will be showing example output which in some cases may extend past the
size of the formatting box, be sure to try scrolling to the right when needed
to see the full command-line arguments or console output.

.. _list_sources_example:

``list_sources.py``
-------------------

This script takes no extra arguments, and will just cycle through Capture Jobs,
Clips, and Files printing out the results.

Example output::

    $ python list_sources.py ar11.example.com -u admin -p admin

    Capture Jobs
    ------------

    id                                      name           mifg_id    filter     state      start_time              end_time                size
    -------------------------------------------------------------------------------------------------------------------------------------------------------
    524abdd0-b620-4ec8-9fa0-d3e2d0376f42    test1          1000       port 80    STOPPED    0.000000000             0.000000000             0
    82fc88b2-ae6a-44c7-bf6e-1ee262700ab9    port81         1000       port 81    STOPPED    0.000000000             0.000000000             0
    94e116fa-11ca-40b7-9926-0f6825b4fcf2    test5          1000                  STOPPED    0.000000000             0.000000000             0
    a9db07eb-b330-4fad-a025-7ae9e02b7f69    port80         1000       port 80    STOPPED    0.000000000             0.000000000             0
    fc8ae608-31a3-4990-b0bf-373e908f6954    default_job    1000       None       RUNNING    1501182870.000000000    1501272580.000000000    16048877139

    Clips
    -----

    id                                          job_id                                  start_time    end_time      filters
    ---------------------------------------------------------------------------------------------------------------------------
    fc8ae608-31a3-4990-b0bf-373e908f69540000    fc8ae608-31a3-4990-b0bf-373e908f6954    1501165048    1501165348    None

    Uploaded Files/PCAPs
    --------------------

    type         id                           link_type    format     size       created       modified
    ---------------------------------------------------------------------------------------------------------
    PCAP_FILE    /admin/port80_export.pcap    EN10MB       PCAP_US    7518727    1501166729    1501166729


.. _create_capture_job_example:

``create_capture_job.py``
-------------------------

This script provides a means to query existing jobs and MIFGs, and also a simple
mechanisim to create a new capture job with an associated filter expression.

There are a few unique options to this script, which are fairly self
explanatory:

.. code-block:: none

    --jobname=JOBNAME     job name
    --mifg-id=MIFG_ID     ID of the MIFG on which this job is collecting packet
                          data
    --filter=FILTER       STEELFILTER/BPF filter of the packets collected
    --filter-type=FILTER_TYPE
                          STEELFILTER or BPF, default BPF
    --show-mifgs          Show list of MIFG on the device
    --show-jobs           Show list of capture jobs on the device

Using the ``--show-jobs`` command will output the same table as seen in
:ref:`list_sources_example`, and using the ``--show-mifgs`` will show the
interface groups available::

    $ python create_capture_job.py ar11.example.com -u admin -p admin --show-mifgs

    id      name            interfaces
    --------------------------------------
    1000    default_mifg    ['mon0']

Creating a capture job requires just a desired job name, the MIFG, and an optional filter
expression:

.. code-block:: none

    $ python create_capture_job.py ar11.example.com -u admin -p admin --jobname newtest1 --filter "port 80" --mifg-id 1000
    Successfully created packet capture job newtest1

Running the ``--show-jobs`` option will now show the newly created capture job.

.. _upload_pcap_example:

``upload_pcap.py``
------------------

As the name implies, this script will take a PCAP file on the local system
and upload it to the remote AppResponse appliance.  The two extra options
available are::

    --filepath=FILEPATH   path to pcap tracefile to upload
    --destname=DESTNAME   location to store on server, defaults to
                        <username>/<basename of filepath>

Only the ``--filepath`` option is required.

Example output:

.. code-block:: none

    $ python upload_pcap.py ar11.example.com -u admin -p admin --filepath http.pcap
    Uploading http.pcap
    File 'http.pcap' successfully uploaded.
    The properties are {'created': '1501273621', 'format': 'PCAP_US',
    'access_rights': {'owner': 'admin'}, 'modified': '1501273621',
    'type': 'PCAP_FILE', 'id': '/admin/http.pcap', 'link_type': 'EN10MB', 'size': 1601}

.. _download_example:

``download.py``
---------------

This script provides a means to download packets into a local PCAP file from
a variety of sources on AppResponse.  Several options provide
fine control over just what gets downloaded:

.. code-block:: none

    Source Options:
      --source-file=SOURCE_FILE
                          source file path to export
      --jobname=JOBNAME   job name to export
      --jobid=JOBID       job ID to export
      --clipid=CLIPID     clip ID to export

    Time and Filter Options:
      --starttime=START_TIME
                          start time for export (timestamp format)
      --endtime=END_TIME  end time for export (timestamp format)
      --timerange=TIMERANGE
                          Time range to analyze (defaults to "last 1 hour")
                          other valid formats are: "4/21/13 4:00 to 4/21/13
                          5:00" or "16:00:00 to 21:00:04.546"
      --filter=FILTERS    filter to apply to export, can be repeated as many
                          times as desired. Each filter should be formed as
                          "<id>,<type>,<value>", where <type> should be one of
                          "BPF", "STEELFILTER", "WIRESHARK", i.e.
                          "f1,BPF,port 80".

    Output Options:
      --dest-file=DEST_FILE
                          destination file path to export
      --overwrite         Overwrite the local file if it exists

Choose one of the `Source Options`, a time filter, and add an optional
filter expression.  To download a PCAP file, for example the same one
we just uploaded using our :ref:`upload_pcap_example`, we need to
specify the file path on the appliance, a destination, and use
a special time filter of start:0 end:0 to make sure we get
the whole PCAP rather than a slice:

.. code-block:: none

    $ python download.py ar11.example.com -u admin -p admin --source-file "/admin/http.pcap" --starttime=0 --endtime=0 --dest-file=http_output.pcap
    Downloading to file http_output.pcap
    Finished downloading to file http_output.pcap
    $ ls -l
    ...
    -rw-r--r--@ 1 root  staff      1601 May 10 09:06 http.pcap
    -rw-r--r--  1 root  staff      1601 Jul 28 17:04 http_output.pcap
    ...

To download packets from a capture job, we use slightly different options.

.. code-block:: none

    $ python download.py ar11.example.com -u admin -p admin --jobname default_job --timerange "last 3 seconds" --overwrite
    Downloading to file default_job_export.pcap
    Finished downloading to file default_job_export.pcap


.. _packets_report_example:

``packets_report.py``
---------------------

This example provides a quick means to generate a report against a given
packets source on AppResponse.  The sources could be a file, clip, or running
capture job, and the query can take the form of virtually any combination of
key and value columns.

The availble options for this script:

.. code-block:: none

    Source Options:
      --sourcetype=SOURCETYPE
                          Type of data source to run report against, i.e. file,
                          clip or job
      --sourceid=SOURCEID
                          ID of the source to run report against
      --keycolumns=KEYCOLUMNS
                          List of key column names separated by comma
      --valuecolumns=VALUECOLUMNS
                          List of value column names separated by comma

    Time and Filter Options:
      --timerange=TIMERANGE
                          Time range to analyze, valid formats are: "06/05/17
                          17:09:00 to 06/05/17 18:09:00" or "17:09:00 to
                          18:09:00" or "last 1 hour".
      --granularity=GRANULARITY
                          The amount of time in seconds for which the data
                          source computes a summary of the metrics it received.
      --resolution=RESOLUTION
                          Additional granularity in seconds to tell the data
                          source to aggregate further.

    Output Options:
      --csvfile=CSVFILE   CSV file to store report data

The critical items in this report are the ``--keycolumns`` and
``--valuecolumns`` options.  Together they will define how the format of the
resulting data will look.  Virtually any combination of available fields can be
used either as a key or a value.  Choosing the Key columns will define how each
of the rows are grouped and ensure they will be unique -- think of them as Key
columns to a SQL table.  The Value columns will be any value that matches up
with the Keys.

A simple packets report using `src_ip` and `dest_ip` as the keys, and bytes and packets as
the values:

.. code-block:: none

    $ python packets_report.py ar11.example.com -u admin -p admin --sourcetype=job \
    --sourceid=default_job --keycolumns=src_ip.addr,dst_ip.addr \
    --valuecolumns=sum_traffic.total_bytes,sum_traffic.packets --timerange='last 10 seconds' --granularity=1 \
    --filterexpr 'tcp.port==80'

    src_ip.addr,dst_ip.addr,sum_traffic.total_bytes,sum_traffic.packets
    3ffe::300:ff:fe00:62,3ffe::200:ff:fe00:2,888,12
    192.70.163.102,192.70.0.4,2056,14
    10.33.122.39,10.5.39.140,66,1
    3ffe::200:ff:fe00:2,3ffe::300:ff:fe00:62,9602,7
    10.64.101.226,10.64.101.2,57675,79
    10.64.101.2,10.64.101.226,69775,86
    107.178.255.114,10.33.122.39,611,4
    192.70.163.103,192.70.0.4,1403,11
    10.33.122.39,107.178.255.114,310,4
    10.64.101.225,10.8.117.12,96690,134
    10.8.117.12,10.64.101.225,31662,65
    bad:dad:cafe::1eb9:a44b,bad:dad:cafe::2ec3:ae55,8432,58
    34.197.206.192,10.33.124.26,60,1
    192.70.0.3,192.70.84.228,27765,21
    10.33.124.26,34.197.206.192,60,1
    10.64.101.225,10.8.117.10,132,2

    .... snipped ....

 For a complete listing of the available columns to choose, see the output
 of the builtin command ``steel appresponse columns``.


.. _general_report_example:

``general_report.py``
---------------------

This example provides a quick means to generate a report against a given non-packets
source on AppResponse. The source could be any one of the supported sources except
``packets``, and the query can take the form of virtually any combination of key and value
columns that are supported by the selected source.

The availble options for this script:

.. code-block:: none

  Source Options:
    --showsources       Display the set of source names
    --sourcename=SOURCENAME
                        Name of source to run report against, i.e. aggregates,
                        flow_tcp, etc.
    --keycolumns=KEYCOLUMNS
                        List of key column names separated by comma
    --valuecolumns=VALUECOLUMNS
                        List of value column names separated by comma

  Time and Filter Options:
    --timerange=TIMERANGE
                        Time range to analyze, valid formats are: "06/05/17
                        17:09:00 to 06/05/17 18:09:00" or "17:09:00 to
                        18:09:00" or "last 1 hour".
    --granularity=GRANULARITY
                        The amount of time in seconds for which the data
                        source computes a summary of the metrics it received.
    --resolution=RESOLUTION
                        Additional granularity in seconds to tell the data
                        source to aggregate further.
    --filtertype=FILTERTYPE
                        Traffic filter type, needs to be one of 'steelfilter',
                        'wireshark', 'bpf', defaults to 'steelfilter'
    --filterexpr=FILTEREXPR
                        Traffic filter expression

  Output Options:
    --csvfile=CSVFILE   CSV file to store report data

A simple general repor that uses ``start_time`` as the key column, ``sum_tcp.payload_bytes``
and ``sum_tcp.payload_packets`` as value columns, against the ``flow_tcp`` source:

.. code-block:: none

   $ python general_report.py ar11.example.com -u admin -p admin --sourcename flow_tcp
     --keycolumns start_time --valuecolumns sum_tcp.payload_bytes,sum_tcp.payload_packets
     --timerange 'last 1 min' --filterexpr 'cli_tcp.port==80'

    start_time,sum_tcp.payload_bytes,sum_tcp.payload_packets
    1509590160,23181326,41931

For a complete list of available source names to choose from, see the ouput of the built-in
command `steel appresponse sources <file:///Users/wguo/ws/steelscript/docs/_build/html/appresponse/tutorial.html#creating-an-appresponse-object>`_.

.. _update_host_groups_example:

``update_host_groups.py``
-------------------------

This script provides a simple interface to the Host Group functionality
within appresponse.  It will display, update, or create new hostgroups
as needed.

The custom options are:

.. code-block:: none

    HostGroup Options:
      --file=FILE         Path to the file with hostgroup info, each line should
                          have three columns formated as:
                          "<hostgroup_name>
                          <subnet_1>,<subnet_2>,...,<subnet_n>"
      --name=NAME         Namme of host group to update or delete
      --id=ID             ID of the host group to update or delete
      --hosts=HOSTS       List of hosts and host-ranges
      --disabled          Whether host group should be disabled
      --operation=OPERATION
                          show: render configured hostgroups
                          add: add one hostgroup
                          update: update one hostgroup
                          upload: upload a file with hostgroups
                          delete: delete one hostgroup
                          clear: clear all hostgroups

The ``--operation`` option controls the primary action of the script,
which can be one of the several values shown in the help screen. Using
the operation `show`, we can see all of the configured Host Groups:

.. code-block:: none

    > python update_host_groups.py ar11.example.com -u admin -p admin --operation show

    id    name     active    definition
    -------------------------------------------------------------------------
    14    test5    True      ['4.4.4.4-4.4.4.4']
    15    test7    True      ['3.3.0.0-3.3.255.255', '4.2.2.0-4.2.2.255']

In order to add new groups, we can either use the options to create them one by
one, or we can use a specially formatted file to upload them all at once.  Take
the following file named ``hostgroup_upload.csv``, for example:

.. code-block:: none

    CZ-Prague-HG 10.143.58.64/26,10.143.58.63/23
    MX-SantaFe-HG 10.194.32.0/23
    KR-Seoul-HG 10.170.55.0/24
    ID-Surabaya-HG 10.234.9.0/24


Now, let's upload this to the server:

.. code-block:: none

    > python update_host_groups.py ar11.example.com -u admin -p admin --operation upload --file hostgroup_upload.csv
    Successfully uploaded 4 hostgroup definitions.

And if we re-run our `show` operation, we will see our groups in the listing:

.. code-block:: none

    > python update_host_groups.py ar11.example.com -u admin -p admin --operation show

    id    name     active    definition
    -------------------------------------------------------------------------
    14    test5             True      ['4.4.4.4-4.4.4.4']
    15    test7             True      ['3.3.0.0-3.3.255.255', '4.2.2.0-4.2.2.255']
    16    CZ-Prague-HG      True      ['10.143.58.0-10.143.59.255', '10.143.58.64-10.143.58.127']
    17    MX-SantaFe-HG     True      ['10.194.32.0-10.194.33.255']
    18    KR-Seoul-HG       True      ['10.170.55.0-10.170.55.255']
    19    ID-Surabaya-HG    True      ['10.234.9.0-10.234.9.255']
