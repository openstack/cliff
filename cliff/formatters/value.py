"""Output formatters values only
"""

import six

from .base import ListFormatter
from .base import SingleFormatter


class ValueFormatter(ListFormatter, SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        for row in data:
            stdout.write(' '.join(map(six.text_type, row)) + u'\n')
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        for value in data:
            stdout.write('%s\n' % str(value))
        return
