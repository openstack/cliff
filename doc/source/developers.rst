================
 For Developers
================

If you would like to contribute to cliff directly, these instructions
should help you get started.  Bug reports, and feature requests are
all welcome through the `Launchpad project`_.

.. _Launchpad project: https://launchpad.net/python-cliff

Changes to cliff should be submitted for review via the Gerrit tool,
following the workflow documented at
http://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.

Bugs should be filed under the `Launchpad project`_.


.. note::

  Before contributing new features to clif core, please consider
  whether they should be implemented as an extension instead. The
  architecture is highly pluggable precisely to keep the core small.

Building Documentation
======================

The documentation for cliff is written in reStructuredText and
converted to HTML using Sphinx. The build itself is driven by make.
You will need the following packages in order to build the docs:

- Sphinx
- docutils

Once all of the tools are installed into a virtualenv using
pip, run ``make docs`` to generate the HTML version of the
documentation::

    $ make docs
    (cd docs && make clean html)
    sphinx-build -b html -d build/doctrees   source build/html
    Running Sphinx v1.1.3
    loading pickled environment... done
    building [html]: targets for 1 source files that are out of date
    updating environment: 1 added, 1 changed, 0 removed
    reading sources... [100%] index                                                 
    looking for now-outdated files... none found
    pickling environment... done
    done
    preparing documents... done
    writing output... [100%] index                                                  
    writing additional files... genindex search
    copying static files... done
    dumping search index... done
    dumping object inventory... done
    build succeeded, 2 warnings.

    Build finished. The HTML pages are in build/html.
    
The output version of the documentation ends up in
``./docs/build/html`` inside your sandbox.

Running Tests
=============

The test suite for clif uses tox_, which must be installed separately
(``pip install tox``).

To run the tests under Python 2.7 and 3.3 as well as PyPy, run ``tox``
from the top level directory of the git repository.

To run tests under a single version of Python, specify the appropriate
environment when running tox::

  $ tox -e py27

Add new tests by modifying an existing file or creating new script in
the ``tests`` directory.

.. _tox: http://codespeak.net/tox

.. _developer-templates:
