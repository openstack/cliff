===============
 List Commands
===============

One of the most common patterns with command line programs is the need
to print lists of data. cliff provides a base class for commands of
this type so that they only need to prepare the data, and the user can
choose from one of several output formatter plugins to see the list of
data in their preferred format.

Lister
======

The :class:`cliff.lister.Lister` base class API extends
:class:`Command` to allow :func:`take_action` to return data to be
formatted using a user-selectable formatter. Subclasses should provide
a :func:`take_action` implementation that returns a two member tuple
containing a tuple with the names of the columns in the dataset and an
iterable that will yield the data to be output. See the description of
:ref:`the files command in the demoapp <demoapp-list>` for details.

List Output Formatters
======================

cliff is delivered with two output formatters for list
commands. :class:`Lister` adds a command line switch to let the user
specify the formatter they want, so you don't have to do any extra
work in your application.

csv
---

The ``csv`` formatter produces a comma-separated-values document as
output. CSV data can be imported into a database or spreadsheet for
further manipulation.

::
    
    (.venv)$ cliffdemo files -f csv
    "Name","Size"
    "build",136
    "cliffdemo.log",2690
    "Makefile",5569
    "source",408

table
-----

The ``table`` formatter uses PrettyTable_ to produce output formatted
for human consumption.

.. _PrettyTable: https://pypi.org/project/prettytable/

::
    
    (.venv)$ cliffdemo files
    +---------------+------+
    |      Name     | Size |
    +---------------+------+
    | build         |  136 |
    | cliffdemo.log | 2546 |
    | Makefile      | 5569 |
    | source        |  408 |
    +---------------+------+

value
-----

The ``value`` formatter produces a space separated output with no headers.

::
    
    (.venv)$ cliffdemo files -f value
    build 136
    cliffdemo.log 2690
    Makefile 5569
    source 408

This format can be very convenient when you want to pipe the output to
a script.

::
    
    (.venv)$ cliffdemo files -f value | while read NAME SIZE
    do
      echo $NAME is $SIZE bytes
    done
    build is 136 bytes
    cliffdemo.log is 2690 bytes
    Makefile is 5569 bytes
    source is 408 bytes

yaml
----

The ``yaml`` formatter uses PyYAML_ to produce a YAML sequence of
mappings.

.. _PyYAML: http://pyyaml.org/

::

    (.venv)$ cliffdemo files -f yaml
    - Name: dist
      Size: 4096
    - Name: cliffdemo.egg-info
      Size: 4096
    - Name: README.rst
      Size: 960
    - Name: setup.py
      Size: 1807
    - Name: build
      Size: 4096
    - Name: cliffdemo
      Size: 4096

json
----

The ``json`` formatter produces an array of objects in indented JSON
format.

::

    (.venv)$ cliffdemo files -f json
    [
      {
        "Name": "source", 
        "Size": 4096
      }, 
      {
        "Name": "Makefile", 
        "Size": 5569
      }, 
      {
        "Name": "build", 
        "Size": 4096
      }
    ]

Other Formatters
----------------

A formatter using tablib_ to produce HTML is available as part of
`cliff-tablib`_.

.. _cliff-tablib: https://github.com/dreamhost/cliff-tablib

Creating Your Own Formatter
---------------------------

If the standard formatters do not meet your needs, you can bundle
another formatter with your program by subclassing from
:class:`cliff.formatters.base.ListFormatter` and registering the
plugin in the ``cliff.formatter.list`` namespace.


.. _tablib: https://github.com/kennethreitz/tablib
