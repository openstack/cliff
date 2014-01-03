========================================================================
 cliff -- Command Line Interface Formulation Framework -- version 1.5.0
========================================================================

.. tags:: python cliff release DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Fix the arguments passed to commands when they are instantiated to
  pull out help. See https://github.com/dreamhost/cliff/issues/52 for
  details.
- Add bash command completion. (Contributed by Terry Howe)
- Use stevedore to load formatter plugins.
- Use pbr for packaging.

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

