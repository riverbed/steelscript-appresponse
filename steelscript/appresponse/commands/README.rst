Commands
========

This directory defines custom commands via the 'steel' script.
In order to enable this functionality, uncomment a few lines
in the setup.py script.  Search for 'steel.commands'.

Once enabled, any file with a .py extension that defines a class
named Command will automatically become available as subcommands
of the 'steel appresponse' command.

For example, the file 'subcommand.py' in this directory would
be executed by running 'steel appresponse subcommand'.

Any number of commands can be defined.  In addition, further
subcommands of a command can be added for more complex functionality.
See the documenation for details.
