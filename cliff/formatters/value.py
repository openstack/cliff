"""Output formatters values only
"""

from .base import SingleFormatter


class ValueFormatter(SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_one(self, column_names, data, stdout, parsed_args):
        for value in data:
            stdout.write('%s\n' % str(value))
        return
