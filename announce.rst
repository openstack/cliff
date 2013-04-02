========================================================================
 cliff -- Command Line Interface Formulation Framework -- version 1.3.2
========================================================================

.. tags:: python cliff release DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Add ``convert_underscores`` parameter to ``CommandManager``
  ``__init__`` method to allow underscores to be used in command
  names. This optional argument is defaulted to True to maintain
  current behavior.  (contributed by Joe Server)
- Use flake8_ for style checking.
- Relax version requirement for PrettyTable dependency to allow point
  releases of 0.7.

.. _flake8: https://pypi.python.org/pypi/flake8

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

