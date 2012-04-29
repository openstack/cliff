"""Application base class for providing a list of data as output.
"""
import abc
import logging

from .display import DisplayCommandBase


LOG = logging.getLogger(__name__)


class Lister(DisplayCommandBase):
    """Command base class for providing a list of data as output.
    """
    __metaclass__ = abc.ABCMeta

    @property
    def formatter_namespace(self):
        return 'cliff.formatter.list'

    @property
    def formatter_default(self):
        return 'table'

    @abc.abstractmethod
    def get_data(self, parsed_args):
        """Return a tuple containing the column names and an iterable
        containing the data to be listed.
        """

    def run(self, parsed_args):
        column_names, data = self.get_data(parsed_args)
        formatter = self.formatters[parsed_args.formatter]
        formatter.emit_list(column_names, data, self.app.stdout, parsed_args)
        return 0
