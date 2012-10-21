=================
 Release History
=================

1.3

  - Allow user to pass ``argparse_kwargs`` argument to the
    ``build_option_parser`` method. This argument can contain extra
    keyword arguments which are passed to the ``ArgumentParser`` constructor.
    (contributed by Tomaz Muraus)
  - Updated documentation to include dependency on distribute.

1.2.1

  - Fix problem with documentation packaging.
  - Fix problem with missing ``izip`` import in ``lister.py``.

1.2

  - Fix problem with interactive mode ``help`` command.
  - Disable logging by default but add a ``--log-file`` option to
    re-enable it at runtime.
  - Add support for python 2.6. (contributed by Mark McClain for
    OpenStack Quantum)

1.1.2

  - Fix a packaging problem introduced in version 1.1.

1.1

  - Move tablib support (JSON, YAML, and HTML formatters) to a
    separate project to comply with Ubuntu packaging requirements. See
    https://github.com/dreamhost/cliff-tablib

1.0

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

  - Clean up interactive mode flag settting.
  - Add support for Python 2.6, contributed by heavenshell.
  - Fix multi-word commands in interactive mode.

0.6

  - Pass the non-global argument list to :func:`initialize_app` to be
    used in initialization work.

0.5.1

  - Remove pinned version requirement for PrettyTable until the
    OpenStack clients catch up to the API change.

0.5

  - Asking for help about a command by prefix lists all matching
    commands.
  - Add formatters for HTML, JSON, and YAML.

0.4

  - Add shell formatter for single objects.
  - Add interactive mode.
  - Expand documentation.

0.3

  - Add ShowOne base class for commands that show details about single
    objects.
  - Fix a problem with Lister when there is no data to be printed.

0.2

  - Incorporate changes from dtroyer to replace use of optparse in App
    with argparse.
  - Added "help" subcommand to replace ``--help`` option handling in
    subcommands.

0.1

  - Initial public release.
  - Included App, CommandManager, Lister, csv and table formatters, a
    demo application, and basic documentation.
