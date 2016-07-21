"""Formattable column tools.
"""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class FormattableColumn(object):

    def __init__(self, value):
        self._value = value

    @abc.abstractmethod
    def human_readable(self):
        """Return a basic human readable version of the data.
        """

    def machine_readable(self):
        """Return a raw data structure using only Python built-in types.

        It must be possible to serialize the return value directly
        using a formatter like JSON, and it will be up to the
        formatter plugin to decide how to make that transformation.

        """
        return self._value
