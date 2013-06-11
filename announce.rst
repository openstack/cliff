======================================================================
 cliff -- Command Line Interface Formulation Framework -- version 1.4
======================================================================

.. tags:: python cliff release DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Store a reference to the InteractiveApp on the App while in
  interactive mode to allow commands to update the interactive
  state. (Contributed by Tomaz Muraus)
- Remove reliance on distribute, now that it has merged with
  setuptools 0.7. Providing an explicit dependency on setuptools
  breaks updates in some cases, so just fail if it isn't there.

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

