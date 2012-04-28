
import abc
import argparse
import inspect


class Command(object):
    """Base class for command plugins.

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, app, app_args):
        self.app = app
        self.app_args = app_args
        return

    def get_description(self):
        """Return the command description.
        """
        return inspect.getdoc(self.__class__) or ''

    def get_parser(self, prog_name):
        """Return an argparse.ArgumentParser.
        """
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
            )
        return parser

    @abc.abstractmethod
    def run(self, parsed_args):
        """Do something useful.
        """
