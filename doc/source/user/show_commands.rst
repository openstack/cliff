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
:class:`Command` to allow :func:`take_action` to return data to be
formatted using a user-selectable formatter. Subclasses should provide
a :func:`take_action` implementation that returns a two member tuple
containing a tuple with the names of the columns in the dataset and an
iterable that contains the data values associated with those
names. See the description of :ref:`the file command in the demoapp
<demoapp-show>` for details.

Show Output Formatters
======================

cliff is delivered with output formatters for show
commands. :class:`ShowOne` adds a command line switch to let the user
specify the formatter they want, so you don't have to do any extra
work in your application.

table
-----

The ``table`` formatter uses PrettyTable_ to produce output
formatted for human consumption.  This is the default formatter.

.. _PrettyTable: https://pypi.org/project/prettytable

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

value
-----

The ``value`` formatter produces output that only contains the
value of the field or fields.

::

    (.venv)$ cliffdemo file -f value -c Size setup.py
    5916
    (.venv)$ SIZE="$(cliffdemo file -f value -c Size setup.py)"
    (.venv)$ echo $SIZE
    5916

yaml
----

The ``yaml`` formatter uses PyYAML_ to produce a YAML mapping where
the field name is the key.

.. _PyYAML: http://pyyaml.org/

::

    (.venv)$ cliffdemo file -f yaml setup.py
    Name: setup.py
    Size: 1807
    UID: 1000
    GID: 1000
    Modified Time: 1393531476.9587486

json
----

The ``json`` formatter produces a JSON object where the field name
is the key.

::

    (.venv)$ cliffdemo file -f json setup.py
    {
      "Modified Time": 1438726433.8055942, 
      "GID": 1000, 
      "UID": 1000, 
      "Name": "setup.py", 
      "Size": 1028
    }

Other Formatters
----------------

A formatter using tablib_ to produce HTML is available as part of
`cliff-tablib`_.

.. _cliff-tablib: https://github.com/dreamhost/cliff-tablib

Creating Your Own Formatter
---------------------------

If the standard formatters do not meet your needs, you can bundle
another formatter with your program by subclassing from
:class:`cliff.formatters.base.ShowFormatter` and registering the
plugin in the ``cliff.formatter.show`` namespace.


.. _tablib: https://github.com/kennethreitz/tablib
