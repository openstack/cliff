==============
 Introduction
==============

The cliff framework is meant to be used to create multi-level commands
such as subversion and git, where the main program handles some basic
argument parsing and then invokes a sub-command to do the work. 

Command Plugins
===============

Cliff takes advantage of Python's ability to load code dynamically to
allow the sub-commands of a main program to be implemented, packaged,
and distributed separately from the main program. This organization
provides a unified view of the command for *users*, while giving
developers the opportunity organize source code in any way they see
fit.

Cliff Objects
=============

Cliff is organized around five objects that are combined to create a
useful command line program.

The Application
---------------

An :class:`cliff.app.App` is the main program that you run from the shell
command prompt. It is responsible for global operations that apply to
all of the commands, such as configuring logging and setting up I/O
streams.

The CommandManager
------------------

The :class:`cliff.commandmanager.CommandManager` knows how to load
individual command plugins. The default implementation uses
`entry points`_ but any mechanism for loading commands can
be used by replacing the default :class:`CommandManager` when
instantiating an :class:`App`.

The Command
-----------

The :class:`cliff.command.Command` class is where the real work
happens. The rest of the framework is present to help the user
discover the command plugins and invoke them, and to provide runtime
support for those plugins. Each :class:`Command` subclass is
responsible for taking action based on instructions from the user. It
defines its own local argument parser (usually using argparse_) and a
:func:`take_action` method that does the appropriate work.

The CommandHook
---------------

The :class:`cliff.hooks.CommandHook` class can extend a Command by
modifying the command line arguments available, for example to add
options used by a driver. Each CommandHook subclass must implement the
full hook API, defined by the base class. Extensions should be
registered using an entry point namespace based on the application
namespace and the command name::

  application_namespace + '.' + command_name.replace(' ', '_')

The Interactive Application
---------------------------

The main program uses an :class:`cliff.interactive.InteractiveApp`
instance to provide a command-shell mode in which the user can type
multiple commands before the program exits. Many cliff-based
applications will be able to use the default implementation of
:class:`InteractiveApp` without subclassing it.

.. _entry points: https://packaging.python.org/specifications/entry-points/
.. _argparse: http://docs.python.org/library/argparse.html
