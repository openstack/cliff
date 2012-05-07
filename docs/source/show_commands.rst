===============
 Show Commands
===============

One of the most common patterns with command line programs is the need
to print properties of objects. cliff provides a base class for
commands of this type so that they only need to prepare the data, and
the user can choose from one of several output formatter plugins to
see the data in their preferred format.

ShowOne
=======

The :class:`cliff.show.ShowOne` base class API extends
:class:`Command` to add a :func:`get_data` method. Subclasses should
provide a :func:`get_data` implementation that returns a two member
tuple containing a tuple with the names of the columns in the dataset
and an iterable that contains the data values associated with those
names. See the description of :ref:`the file command in the demoapp
<demoapp-show>` for details.

Show Output Formatters
======================

cliff is delivered with output formatters for show
commands. :class:`ShowOne` adds a command line switch to let the user
specify the formatter they want, so you don't have to do any extra
work in your application.

html
----

The ``html`` formatter uses tablib_ to produce HTML output as a table.

::

    (.venv)$ cliffdemo file -f html setup.py
    <table>
    <thead>
    <tr><th>Field</th>
    <th>Value</th></tr>
    </thead>
    <tr><td>Name</td>
    <td>setup.py</td></tr>
    <tr><td>Size</td>
    <td>6373</td></tr>
    <tr><td>UID</td>
    <td>527</td></tr>
    <tr><td>GID</td>
    <td>501</td></tr>
    <tr><td>Modified Time</td>
    <td>1336353173.0</td></tr>
    </table>

json
----

The ``json`` formatter uses tablib_ to produce JSON output.

::

    (.venv)$ cliffdemo file -f json setup.py
    [{"Field": "Name", "Value": "setup.py"}, {"Field": "Size",
    "Value": 6373}, {"Field": "UID", "Value": 527}, {"Field": "GID",
    "Value": 501}, {"Field": "Modified Time", "Value": 1336353173.0}]

shell
-----

The ``shell`` formatter produces output that can be parsed directly by
a typical UNIX shell as variable assignments. This avoids extra
parsing overhead in shell scripts.

::

    (.venv)$ cliffdemo file -f shell setup.py
    name="setup.py"
    size="5916"
    uid="527"
    gid="501"
    modified_time="1335655655.0"

    (.venv)$ eval "$(cliffdemo file -f shell --prefix example_ setup.py)"
    (.venv)$ echo $example_size
    5916

table
-----

The ``table`` formatter uses PrettyTable_ to produce output
formatted for human consumption.

.. _PrettyTable: http://code.google.com/p/prettytable/

::

    (.venv)$ cliffdemo file setup.py
    +---------------+--------------+
    |     Field     |    Value     |
    +---------------+--------------+
    | Name          | setup.py     |
    | Size          | 5825         |
    | UID           | 502          |
    | GID           | 20           |
    | Modified Time | 1335569964.0 |
    +---------------+--------------+

yaml
----

The ``yaml`` formatter uses tablib_ to produce YAML output as a
sequence of mappings.

::

    (.venv)$ cliffdemo file -f yaml setup.py
    - {Field: Name, Value: setup.py}
    - {Field: Size, Value: 6373}
    - {Field: UID, Value: 527}
    - {Field: GID, Value: 501}
    - {Field: Modified Time, Value: 1336353173.0}

Creating Your Own Formatter
---------------------------

If the standard formatters do not meet your needs, you can bundle
another formatter with your program by subclassing from
:class:`cliff.formatters.base.ShowFormatter` and registering the
plugin in the ``cliff.formatter.show`` namespace.


.. _tablib: https://github.com/kennethreitz/tablib
