#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

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
        writer_kwargs = dict(
            quoting=self.QUOTE_MODES[parsed_args.quote_mode],
            lineterminator=os.linesep,
            escapechar='\\',
        )

        # In Py2 we replace the csv module with unicodecsv because the
        # Py2 csv module cannot handle unicode. unicodecsv encodes
        # unicode objects based on the value of it's encoding keyword
        # with the result unicodecsv emits encoded bytes in a str
        # object. The utils.getwriter assures no attempt is made to
        # re-encode the encoded bytes in the str object.

        if six.PY2:
            writer_kwargs['encoding'] = (getattr(stdout, 'encoding', None)
                                         or 'utf-8')

        writer = csv.writer(stdout, **writer_kwargs)
        writer.writerow(column_names)
        for row in data:
            writer.writerow(
                [(six.text_type(c.machine_readable())
                  if isinstance(c, columns.FormattableColumn)
                  else c)
                 for c in row]
            )
        return
