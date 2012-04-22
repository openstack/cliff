"""Base classes for formatters.
"""

import abc


class Formatter(object):

    def __init__(self):
        return

    def add_argument_group(self, parser):
        """Add any options to the argument parser.

        Should use our own argument group.
        """
        return


class ListFormatter(Formatter):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def emit_list(self, column_names, data, stdout):
        """Format and print the list from the iterable data source.
        """
