==================
 For Contributors
==================

If you would like to contribute to cliff directly, these instructions
should help you get started.  Bug reports, and feature requests are
all welcome through the `Storyboard project`_.

.. _Storyboard project: https://storyboard.openstack.org/#!/project/openstack/cliff

Changes to cliff should be submitted for review via the Gerrit tool,
following the workflow documented at
https://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.

Bugs should be filed under the `Storyboard project`_.

.. note::

  Before contributing new features to clif core, please consider
  whether they should be implemented as an extension instead. The
  architecture is highly pluggable precisely to keep the core small.

Running Tests
=============

The test suite for cliff uses tox_, which must be installed separately
(``pip install tox``).

To run the standard set of tests, run ``tox`` from the top level directory of
the git repository.

To run a single environment, specify it using the ``-e`` parameter. For
example::

  $ tox -e pep8

Add new tests by modifying an existing file or creating new script in
the ``tests`` directory.

.. _tox: https://tox.readthedocs.io/

Building Documentation
======================

The documentation for cliff is written in reStructuredText and
converted to HTML using Sphinx. Like tests, the documentation can be built
using ``tox``::

  $ tox -e docs

The output version of the documentation ends up in ``./docs/build/html``.

.. _developer-templates:
