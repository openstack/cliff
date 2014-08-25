=================
 Release History
=================

1.7.0
-----

* Updated dependencies from OpenStack global requirements
* Clean up default tox environment list
* Do not allow wheels for stable tests
* Set the main logger name to match the application
* CSV formatter should use system-dependent line ending
* Make show option compatible with Python 2.6
* Use six.add_metaclass instead of __metaclass__
* fixed typos found by RETF rules
* The --variable option to shell format is redundant
* Expose load_commands publicly
* Fix wrong method name assert_called_once
* Fix pep8 failures on rule E265

1.6.1
-----

* Remove PrettyTable from documentation requirements
* Fix a bug in ShellFormatter's escaping of double quotes in strings
* Import run_cross_tests.sh from oslo-incubator
* add doc requirements to venv

1.6.0
-----

* Add max-width support for table formatter
* Add value only output formattter
* Update readme with links to bug tracker and source
* Move pep8 dependency into pep8 tox test
* Fix doc build with Python 2.6.x
* Fix interactive mode with command line args
* Update .gitreview after repo rename
* Escape double quotes in shell formatter
* Add unit test for shell formatter
* Rename private attribute to avoid conflict
* Sync with global requirements
* Add integration tests with known consumers
* update history for previous change
* Make the formatters a private part of the command

1.5.2
-----

- Fix the arguments passed to commands when they are instantiated to
  pull out help. See https://github.com/dreamhost/cliff/issues/52 for
  details.
- Add bash command completion. (Contributed by Terry Howe)
- Use stevedore to load formatter plugins.
- Use pbr for packaging.

1.4.5
-----

- Update the pyparsing dependency to a version that supports both
  Python 2 and Python 3.
- Add PyPy testing.

1.4.4
-----

- Provide better error handling for unknown commands run from the
  command line. (Contributed by Christophe Chauvet.)

1.4.3
-----

- More stdout encoding issues with Python 2.6.

1.4.2
-----

- Fix an issue with unicode output under Python 2.6. See
  https://github.com/dreamhost/cliff/pull/40 for details.

1.4.1
-----

- Add ``dict2columns`` method to ``ShowOne``. (Contributed by Dean
  Troyer)
- Pin the requirement for cmd2 more tightly.

1.4
---

- Store a reference to the InteractiveApp on the App while in
  interactive mode to allow commands to update the interactive
  state. (Contributed by Tomaz Muraus)
- Remove reliance on distribute, now that it has merged with
  setuptools 0.7. Providing an explicit dependency on setuptools
  breaks updates in some cases, so just fail if it isn't there.

1.3.3
-----

  - Restore compatibility with prettytable < 0.7.2 by forcing no
    output if there is no data (instead of printing an empty
    table). Contributed by Dirk Mueller.
  - Update to allow cmd2 version 0.6.5.1. Contributed by Dirk Mueller.

1.3.2
-----

  - Add ``convert_underscores`` parameter to ``CommandManager`` ``__init__``
    method to allow underscores to be used in command names. This optional
    argument is defaulted to True to maintain current behavior.
    (contributed by Joe Server)
  - Use flake8_ for style checking.
  - Relax version requirement for PrettyTable dependency to allow
    point releases of 0.7.

.. _flake8: https://pypi.python.org/pypi/flake8

1.3.1
-----

  - Sort list of commands in interactive help mode. (contributed by
    Ilya Shakhat)
  - Fix a dependency issue with PyParsing until the cmd2 package can
    release an update setting the version of its dependency based on
    the Python version.

1.3
---

  - Allow user to pass ``argparse_kwargs`` argument to the
    ``build_option_parser`` method. This argument can contain extra
    keyword arguments which are passed to the ``ArgumentParser`` constructor.
    (contributed by Tomaz Muraus)
  - Updated documentation to include dependency on distribute.

1.2.1
-----

  - Fix problem with documentation packaging.
  - Fix problem with missing ``izip`` import in ``lister.py``.

1.2
---

  - Fix problem with interactive mode ``help`` command.
  - Disable logging by default but add a ``--log-file`` option to
    re-enable it at runtime.
  - Add support for python 2.6. (contributed by Mark McClain for
    OpenStack Quantum)

1.1.2
-----

  - Fix a packaging problem introduced in version 1.1.

1.1
---

  - Move tablib support (JSON, YAML, and HTML formatters) to a
    separate project to comply with Ubuntu packaging requirements. See
    https://github.com/dreamhost/cliff-tablib

1.0
---

  - Add trailing newlines after output from tablib-based formatters
    (JSON, YAML, and HTML). Contributed by Matt Joyce.
  - Some :pep:`8` fixes.
  - Refactor the API in :class:`Command` to add :func:`take_action`
    and make :func:`run` a concrete method. Existing users should only
    need to rename :func:`run()` to :func:`take_action()` since the
    function signatures have not changed.
  - In :class:`Lister` and :class:`ShowOne` use :func:`take_action`
    instead of :func:`get_data`.

0.7
---

  - Clean up interactive mode flag setting.
  - Add support for Python 2.6, contributed by heavenshell.
  - Fix multi-word commands in interactive mode.

0.6
---

  - Pass the non-global argument list to :func:`initialize_app` to be
    used in initialization work.

0.5.1
-----

  - Remove pinned version requirement for PrettyTable until the
    OpenStack clients catch up to the API change.

0.5
---

  - Asking for help about a command by prefix lists all matching
    commands.
  - Add formatters for HTML, JSON, and YAML.

0.4
---

  - Add shell formatter for single objects.
  - Add interactive mode.
  - Expand documentation.

0.3
---

  - Add ShowOne base class for commands that show details about single
    objects.
  - Fix a problem with Lister when there is no data to be printed.

0.2
---

  - Incorporate changes from dtroyer to replace use of optparse in App
    with argparse.
  - Added "help" subcommand to replace ``--help`` option handling in
    subcommands.

0.1
---

  - Initial public release.
  - Included App, CommandManager, Lister, csv and table formatters, a
    demo application, and basic documentation.
