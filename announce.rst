========================================================================
 cliff -- Command Line Interface Formulation Framework -- version 1.3.3
========================================================================

.. tags:: python cliff release DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Restore compatibility with prettytable < 0.7.2 by forcing no
  output if there is no data (instead of printing an empty
  table). Contributed by Dirk Mueller.
- Update to allow cmd2 version 0.6.5.1. Contributed by Dirk Mueller.

Documentation
=============

`Documentation for cliff`_ is hosted on `readthedocs.org`_

.. _Documentation for cliff: http://readthedocs.org/docs/cliff/en/latest/

.. _readthedocs.org: http://readthedocs.org

Installation
============

Use pip::

  $ pip install cliff

See `the installation guide`_ for more details.

.. _the installation guide: http://cliff.readthedocs.org/en/latest/install.html

