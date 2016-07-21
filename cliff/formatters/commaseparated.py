"""Output formatters using csv format.
"""

import os
import sys

from .base import ListFormatter
from cliff import columns

import six

if sys.version_info[0] == 3:
    import csv
else:
    import unicodecsv as csv


class CSVLister(ListFormatter):

    QUOTE_MODES = {
        'all': csv.QUOTE_ALL,
        'minimal': csv.QUOTE_MINIMAL,
        'nonnumeric': csv.QUOTE_NONNUMERIC,
        'none': csv.QUOTE_NONE,
    }

    def add_argument_group(self, parser):
        group = parser.add_argument_group('CSV Formatter')
        group.add_argument(
            '--quote',
            choices=sorted(self.QUOTE_MODES.keys()),
            dest='quote_mode',
            default='nonnumeric',
            help='when to include quotes, defaults to nonnumeric',
        )

    def emit_list(self, column_names, data, stdout, parsed_args):
        writer = csv.writer(stdout,
                            quoting=self.QUOTE_MODES[parsed_args.quote_mode],
                            lineterminator=os.linesep,
                            escapechar='\\',
                            )
        writer.writerow(column_names)
        for row in data:
            writer.writerow(
                [(six.text_type(c.machine_readable())
                  if isinstance(c, columns.FormattableColumn)
                  else c)
                 for c in row]
            )
        return
