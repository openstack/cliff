======================================================================
 cliff -- Command Line Interface Formulation Framework -- version 0.2
======================================================================

.. tags: python, cliff, release, DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Incorporate changes from dtroyer to replace use of optparse in App
  with argparse.
- Added "help" subcommand to replace ``--help`` option handling in
  subcommands.

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

.. _the installation guide: http://cliff.readthedocs.org/en/latest/install.html>

