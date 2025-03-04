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

"""Output formatters using csv format."""

import argparse
import collections.abc
import csv
import os
import typing as ty

from cliff import columns
from cliff.formatters import base


class CSVLister(base.ListFormatter):
    QUOTE_MODES = {
        'all': csv.QUOTE_ALL,
        'minimal': csv.QUOTE_MINIMAL,
        'nonnumeric': csv.QUOTE_NONNUMERIC,
        'none': csv.QUOTE_NONE,
    }

    def add_argument_group(self, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('CSV Formatter')
        group.add_argument(
            '--quote',
            choices=sorted(self.QUOTE_MODES.keys()),
            dest='quote_mode',
            default='nonnumeric',
            help='when to include quotes, defaults to nonnumeric',
        )

    def emit_list(
        self,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Iterable[collections.abc.Sequence[ty.Any]],
        stdout: ty.TextIO,
        parsed_args: argparse.Namespace,
    ) -> None:
        writer = csv.writer(
            stdout,
            quoting=self.QUOTE_MODES[parsed_args.quote_mode],
            lineterminator=os.linesep,
            escapechar='\\',
        )
        writer.writerow(column_names)
        for row in data:
            writer.writerow(
                [
                    (
                        str(c.machine_readable())
                        if isinstance(c, columns.FormattableColumn)
                        else c
                    )
                    for c in row
                ]
            )
        return
