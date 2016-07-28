==============
 Installation
==============

Python Versions
===============

cliff is being developed under Python 2.7 and tested with Python 3.2.

Dependencies
============

cliff depends on distribute_, the updated replacement for
setuptools. If you have an older version of setuptools installed, `you
may have trouble installing cliff`_ until you upgrade or set up a
virtualenv_ using distribute instead (by using ``--use-distribute``).

.. _distribute: http://pypi.python.org/pypi/distribute

.. _you may have trouble installing cliff: https://bitbucket.org/tarek/distribute/issue/91/install-glitch-when-using-pip-virtualenv

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

.. _install-basic:

Basic Installation
==================

cliff should be installed into the same site-packages area where the
application and extensions are installed (either a virtualenv or the
global site-packages). You may need administrative privileges to do
that.  The easiest way to install it is using pip_::

  $ pip install cliff

or::

  $ sudo pip install cliff

.. _pip: http://pypi.python.org/pypi/pip

Source Code
===========

The source is hosted on github: http://git.openstack.org/cgit/openstack/cliff

Reporting Bugs
==============

Please report bugs through the github project:
https://bugs.launchpad.net/python-cliff
