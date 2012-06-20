======================================================================
 cliff -- Command Line Interface Formulation Framework -- version 0.7
======================================================================

.. tags:: python cliff release DreamHost

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

What's New In This Release?
===========================

- Add trailing newlines after output from tablib-based formatters
  (JSON, YAML, and HTML). Contributed by Matt Joyce.
- Some PEP-8 fixes.
- Refactor the API in ``Command`` to add ``take_action()``
  and make ``run()`` a concrete method. Existing users should only
  need to rename ``run()`` to ``take_action()`` since the function
  signatures have not changed.
- In ``Lister`` and ``ShowOne`` use ``take_action()`` instead of
  ``get_data()``.

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

