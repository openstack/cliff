"""Application base class for providing a list of data as output.
"""
import abc
import logging

import six

from .display import DisplayCommandBase


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Lister(DisplayCommandBase):
    """Command base class for providing a list of data as output.
    """

    @property
    def formatter_namespace(self):
        return 'cliff.formatter.list'

    @property
    def formatter_default(self):
        return 'table'

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Return a tuple containing the column names and an iterable
        containing the data to be listed.
        """

    def produce_output(self, parsed_args, column_names, data):
        if not parsed_args.columns:
            columns_to_include = column_names
            data_gen = data
        else:
            columns_to_include = [c for c in column_names
                                  if c in parsed_args.columns
                                  ]
            if not columns_to_include:
                raise ValueError('No recognized column names in %s' %
                                 str(parsed_args.columns))
            # Set up argument to compress()
            selector = [(c in columns_to_include)
                        for c in column_names]
            # Generator expression to only return the parts of a row
            # of data that the user has expressed interest in
            # seeing. We have to convert the compress() output to a
            # list so the table formatter can ask for its length.
            data_gen = (list(self._compress_iterable(row, selector))
                        for row in data)
        self.formatter.emit_list(columns_to_include,
                                 data_gen,
                                 self.app.stdout,
                                 parsed_args,
                                 )
        return 0
