====================
 Sphinx Integration
====================

Usage
=====

cliff supports integration with Sphinx by way of a `Sphinx directives`__.

Preparation
-----------

Before using the :rst:dir:`autoprogram-cliff` directive you must add
`'cliff.sphinxext'` extension module to a list of `extensions` in `conf.py`:

.. code-block:: python

   extensions = ['cliff.sphinxext']

Directive
---------

.. rst:directive:: .. autoprogram-cliff:: <namespace> or <app class>

   Automatically document an instance of :py:class:`cliff.command.Command`
   or :py:class:`cliff.app.App`
   including a description, usage summary, and overview of all options.

   .. important::

      There are two modes in this directive: **command** mode and **app**
      mode. The directive takes one required argument and the mode is
      determined based on the argument specified.

   The **command** mode documents various information of a specified instance of
   :py:class:`cliff.command.Command`. The **command** mode takes the namespace
   that the command(s) can be found in as the argument. This is generally
   defined in the `entry_points` section of either `setup.cfg` or
   `setup.py`. You can specify which command(s) should be displayed using
   `:command:` option.

   .. code-block:: rst

       .. autoprogram-cliff:: openstack.compute.v2
          :command: server add fixed ip

   The **app** mode documents various information of a specified instance of
   :py:class:`cliff.app.App`. The **app** mode takes the python path of the
   corresponding class as the argument. In the **app** mode, `:application:`
   option is usually specified so that the command name is shown in the
   rendered output.

   .. code-block:: rst

       .. autoprogram-cliff:: cliffdemo.main.DemoApp
          :application: cliffdemo

   Refer to the example_ below for more information.

   In addition, the following directive options can be supplied:

   `:command:`
     The name of the command, as it would appear if called from the command
     line without the executable name. This will be defined in `setup.cfg` or
     `setup.py` albeit with underscores. This is optional and `fnmatch-style`__
     wildcarding is supported. Refer to the example_ below for more
     information.

     This option is effective only in the **command** mode.

   `:arguments`
     The arguments to be passed when the cliff application is instantiated.
     Some cliff applications requires arguments when instantiated.
     This option can be used to specify such arguments.

     This option is effective only in the **app** mode.

   `:application:`
     The top-level application name, which will be prefixed before all
     commands. This option overrides the global option
     `autoprogram_cliff_application` described below.
     In most cases the global configuration is enough, but this option is
     useful if your sphinx document handles multiple cliff applications.

     .. seealso:: The ``autoprogram_cliff_application`` configuration option.

   `:ignored:`
     A comma-separated list of options to exclude from documentation for this
     option. This is useful for options that are of low value.

     .. seealso:: The ``autoprogram_cliff_ignored`` configuration option.

   The following global configuration values are supported. These should be
   placed in `conf.py`:

   `autoprogram_cliff_application`
     The top-level application name, which will be prefixed before all
     commands. This is generally defined in the `console_scripts` attribute of
     the `entry_points` section of either `setup.cfg` or `setup.py`. Refer to
     the example_ below for more information.

     For example:

     .. code-block:: python

        autoprogram_cliff_application = 'my-sample-application'

     Defaults to ``''``

     .. seealso:: The ``:command:`` directive option.
     .. seealso:: The ``:application:`` directive option.

   `autoprogram_cliff_ignored`
     A global list of options to exclude from documentation. This can be used
     to prevent duplication of common options, such as those used for
     pagination, across **all** options.

     For example:

     .. code-block:: python

        autoprogram_cliff_ignored = ['--help', '--page', '--order']

     Defaults to ``['--help']``

     .. seealso:: The ``:ignored:`` directive option.

   `autoprogram_cliff_app_dist_name`
     The name of the python distribution (the name used with pip, as opposed to
     the package name used for importing) providing the commands/applications
     being documented. Generated documentation for plugin components includes
     a message indicating the name of the plugin. Setting this option tells
     cliff the name of the distribution providing components natively so their
     documentation does not include this message.

.. seealso::

    Module `sphinxcontrib.autoprogram`
      An equivalent library for use with plain-old `argparse` applications.

    Module `sphinx-click`
      An equivalent library for use with `click` applications.

.. important::

    The :rst:dir:`autoprogram-cliff` directive emits :rst:dir:`code-block`
    snippets marked up as `shell` code. This requires `pygments` >= 0.6.

.. _example:

Examples
========

Simple Example (`demoapp`)
--------------------------

`cliff` provides a sample application, :doc:`demoapp`, to demonstrate some of the
features of `cliff`. This application :ref:`is documented <demoapp-sphinx>`
using the `cliff.sphinxext` Sphinx extension.

Advanced Example (`python-openstackclient`)
-------------------------------------------

It is also possible to document larger applications, such as
`python-openstackclient`__. Take a sample `setup.cfg` file, which is a minimal
version of the `setup.cfg` provided by the `python-openstackclient` project:

.. code-block:: ini

    [entry_points]
    console_scripts =
        openstack = openstackclient.shell:main

    openstack.compute.v2 =
        host_list = openstackclient.compute.v2.host:ListHost
        host_set = openstackclient.compute.v2.host:SetHost
        host_show = openstackclient.compute.v2.host:ShowHost

This will register three commands - ``host list``, ``host set`` and ``host
show`` - for a top-level executable called ``openstack``. To document the first
of these, add the following:

.. code-block:: rst

    .. autoprogram-cliff:: openstack.compute.v2
       :command: host list

You could also register all of these at once like so:

.. code-block:: rst

    .. autoprogram-cliff:: openstack.compute.v2
       :command: host *

Finally, if these are the only commands available in that namespace, you can
omit the `:command:` parameter entirely:

.. code-block:: rst

    .. autoprogram-cliff:: openstack.compute.v2

In all cases, you should add the following to your `conf.py` to ensure all
usage examples show the full command name:

.. code-block:: python

    autoprogram_cliff_application = 'openstack'

__ http://www.sphinx-doc.org/en/stable/extdev/markupapi.html
__ https://docs.python.org/3/library/fnmatch.html
__ https://docs.openstack.org/python-openstackclient/
