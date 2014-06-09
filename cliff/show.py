"""Application base class for displaying data about a single object.
"""
import abc
import logging

import six

from .display import DisplayCommandBase


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class ShowOne(DisplayCommandBase):
    """Command base class for displaying data about a single object.
    """

    @property
    def formatter_namespace(self):
        return 'cliff.formatter.show'

    @property
    def formatter_default(self):
        return 'table'

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Return a two-part tuple with a tuple of column names
        and a tuple of values.
        """

    def produce_output(self, parsed_args, column_names, data):
        if not parsed_args.columns:
            columns_to_include = column_names
        else:
            columns_to_include = [c for c in column_names
                                  if c in parsed_args.columns]
            # Set up argument to compress()
            selector = [(c in columns_to_include)
                        for c in column_names]
            data = list(self._compress_iterable(data, selector))
        self.formatter.emit_one(columns_to_include,
                                data,
                                self.app.stdout,
                                parsed_args)
        return 0

    def dict2columns(self, data):
        """Implement the common task of converting a dict-based object
        to the two-column output that ShowOne expects.
        """
        if not data:
            return ({}, {})
        else:
            return zip(*sorted(data.items()))
