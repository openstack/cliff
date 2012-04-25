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
:class:`Command` to add a :func:`get_data` method. Subclasses should
provide a :func:`get_data` implementation that returns a two member
tuple containing a tuple with the names of the columns in the dataset
and an iterable that will yield the data to be output. See the
description of :ref:`the files command in the demoapp <demoapp-list>`
for details.

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

PrettyTable
-----------

The ``PrettyTable`` formatter uses PrettyTable_ to produce output
formatted for human consumption.

.. _PrettyTable: http://code.google.com/p/prettytable/

Creating Your Own Formatter
---------------------------

If the standard formatters do not meet your needs, you can bundle
another formatter with your program by subclassing from
:class:`cliff.formatters.base.ListFormatter` and registering the
plugin in the ``cliff.formatter.list`` namespace.

