"""Application base class for providing a list of data as output.
"""
import abc
import six

from .display import DisplayCommandBase


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
        (columns_to_include, selector) = self._generate_columns_and_selector(
            parsed_args, column_names)
        if selector:
            # Generator expression to only return the parts of a row
            # of data that the user has expressed interest in
            # seeing. We have to convert the compress() output to a
            # list so the table formatter can ask for its length.
            data = (list(self._compress_iterable(row, selector))
                    for row in data)
        self.formatter.emit_list(columns_to_include,
                                 data,
                                 self.app.stdout,
                                 parsed_args,
                                 )
        return 0
