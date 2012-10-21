======================================================================
 cliff -- Command Line Interface Formulation Framework -- version 1.3
======================================================================

.. tags:: python cliff release DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Allow user to pass ``argparse_kwargs`` argument to the
  ``build_option_parser`` method. This argument can contain extra
  keyword arguments which are passed to the ``ArgumentParser`` constructor.
  (contributed by Tomaz Muraus)
- Document the dependency on using distribute.

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

