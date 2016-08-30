"""Output formatters values only
"""

import six

from . import base
from cliff import columns


class ValueFormatter(base.ListFormatter, base.SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        for row in data:
            stdout.write(
                ' '.join(
                    six.text_type(c.machine_readable()
                                  if isinstance(c, columns.FormattableColumn)
                                  else c)
                    for c in row) + u'\n')
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        for value in data:
            stdout.write('%s\n' % six.text_type(
                value.machine_readable()
                if isinstance(value, columns.FormattableColumn)
                else value)
            )
        return
