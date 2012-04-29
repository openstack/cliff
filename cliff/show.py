"""Application base class for displaying data about a single object.
"""
import abc
import logging

from .display import DisplayCommandBase


LOG = logging.getLogger(__name__)


class ShowOne(DisplayCommandBase):
    """Command base class for displaying data about a single object.
    """
    __metaclass__ = abc.ABCMeta

    @property
    def formatter_namespace(self):
        return 'cliff.formatter.show'

    @property
    def formatter_default(self):
        return 'table'

    @abc.abstractmethod
    def get_data(self, parsed_args):
        """Return a two-part tuple with a tuple of column names
        and a tuple of values.
        """

    def run(self, parsed_args):
        column_names, data = self.get_data(parsed_args)
        formatter = self.formatters[parsed_args.formatter]
        formatter.emit_one(column_names, data, self.app.stdout, parsed_args)
        return 0
