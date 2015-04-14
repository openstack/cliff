
import abc
import argparse
import inspect

import six


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    """Base class for command plugins.

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App
    """

    deprecated = False

    def __init__(self, app, app_args, cmd_name=None):
        self.app = app
        self.app_args = app_args
        self.cmd_name = cmd_name
        return

    def get_description(self):
        """Return the command description.
        """
        return inspect.getdoc(self.__class__) or ''

    def get_parser(self, prog_name):
        """Return an :class:`argparse.ArgumentParser`.
        """
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
        )
        return parser

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Override to do something useful.
        """

    def run(self, parsed_args):
        """Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        Developers creating new command base classes (such as
        :class:`Lister` and :class:`ShowOne`) should override this
        method to wrap :meth:`take_action`.
        """
        self.take_action(parsed_args)
        return 0
