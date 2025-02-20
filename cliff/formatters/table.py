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

"""Output formatters using prettytable."""

import argparse
import collections.abc
import os
import sys
import typing as ty

import prettytable

from cliff import columns
from cliff.formatters import base
from cliff import utils

_T = ty.TypeVar('_T')


def _format_row(
    row: collections.abc.Iterable[
        ty.Union[columns.FormattableColumn[ty.Any], str, _T]
    ],
) -> list[ty.Union[_T, str]]:
    new_row = []
    for r in row:
        if isinstance(r, columns.FormattableColumn):
            r = r.human_readable()
        if isinstance(r, str):
            r = r.replace('\r\n', '\n').replace('\r', ' ')
        new_row.append(r)
    return new_row


def _do_fit(fit_width: bool) -> bool:
    if os.name == 'nt':
        # NOTE(pas-ha) the isatty is not reliable enough on Windows,
        # so do not try to auto-fit
        return fit_width
    return sys.stdout.isatty() or fit_width


class TableFormatter(base.ListFormatter, base.SingleFormatter):
    ALIGNMENTS = {
        int: 'r',
        str: 'l',
        float: 'r',
    }

    def add_argument_group(self, parser: argparse.ArgumentParser) -> None:
        group = parser.add_argument_group('table formatter')
        group.add_argument(
            '--max-width',
            metavar='<integer>',
            default=int(os.environ.get('CLIFF_MAX_TERM_WIDTH', 0)),
            type=int,
            help=(
                'Maximum display width, <1 to disable. You can also '
                'use the CLIFF_MAX_TERM_WIDTH environment variable, '
                'but the parameter takes precedence.'
            ),
        )
        group.add_argument(
            '--fit-width',
            action='store_true',
            default=bool(int(os.environ.get('CLIFF_FIT_WIDTH', 0))),
            help=(
                'Fit the table to the display width. '
                'Implied if --max-width greater than 0. '
                'Set the environment variable CLIFF_FIT_WIDTH=1 '
                'to always enable'
            ),
        )
        group.add_argument(
            '--print-empty',
            action='store_true',
            help='Print empty table if there is no data to show.',
        )

    def add_rows(
        self,
        table: prettytable.PrettyTable,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Iterable[collections.abc.Sequence[ty.Any]],
    ) -> None:
        # Figure out the types of the columns in the
        # first row and set the alignment of the
        # output accordingly.
        data_iter = iter(data)
        try:
            first_row = next(data_iter)
        except StopIteration:
            pass
        else:
            for value, name in zip(first_row, column_names):
                alignment = self.ALIGNMENTS.get(type(value), 'l')
                table.align[name] = alignment
            # Now iterate over the data and add the rows.
            table.add_row(_format_row(first_row))
            for row in data_iter:
                table.add_row(_format_row(row))

    def emit_list(
        self,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Iterable[collections.abc.Sequence[ty.Any]],
        stdout: ty.TextIO,
        parsed_args: argparse.Namespace,
    ) -> None:
        x = prettytable.PrettyTable(
            column_names,
            print_empty=parsed_args.print_empty,
        )
        x.padding_width = 1

        # Add rows if data is provided
        if data:
            self.add_rows(x, column_names, data)

        # Choose a reasonable min_width to better handle many columns on a
        # narrow console. The table will overflow the console width in
        # preference to wrapping columns smaller than 8 characters.
        min_width = 8
        self._assign_max_widths(
            x, int(parsed_args.max_width), min_width, parsed_args.fit_width
        )

        formatted = x.get_string()
        stdout.write(formatted)
        stdout.write('\n')
        return

    def emit_one(
        self,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Sequence[ty.Any],
        stdout: ty.TextIO,
        parsed_args: argparse.Namespace,
    ) -> None:
        x = prettytable.PrettyTable(
            field_names=('Field', 'Value'), print_empty=False
        )
        x.padding_width = 1
        # Align all columns left because the values are
        # not all the same type.
        x.align['Field'] = 'l'
        x.align['Value'] = 'l'
        for name, value in zip(column_names, data):
            x.add_row(_format_row((name, value)))

        # Choose a reasonable min_width to better handle a narrow
        # console. The table will overflow the console width in preference
        # to wrapping columns smaller than 16 characters in an attempt to keep
        # the Field column readable.
        min_width = 16
        self._assign_max_widths(
            x, int(parsed_args.max_width), min_width, parsed_args.fit_width
        )

        formatted = x.get_string()
        stdout.write(formatted)
        stdout.write('\n')
        return

    @staticmethod
    def _field_widths(
        field_names: list[str], first_line: str
    ) -> dict[str, int]:
        # use the first line +----+-------+ to infer column widths
        # accounting for padding and dividers
        widths = [max(0, len(i) - 2) for i in first_line.split('+')[1:-1]]
        return dict(zip(field_names, widths))

    @staticmethod
    def _width_info(term_width: int, field_count: int) -> tuple[int, int]:
        # remove padding and dividers for width available to actual content
        usable_total_width = max(0, term_width - 1 - 3 * field_count)

        # calculate width per column if all columns were equal
        if field_count == 0:
            optimal_width = 0
        else:
            optimal_width = max(0, usable_total_width // field_count)

        return usable_total_width, optimal_width

    @staticmethod
    def _build_shrink_fields(
        usable_total_width: int,
        optimal_width: int,
        field_widths: dict[str, int],
        field_names: list[str],
    ) -> tuple[list[str], int]:
        shrink_fields = []
        shrink_remaining = usable_total_width
        for field in field_names:
            w = field_widths[field]
            if w <= optimal_width:
                # leave alone columns which are smaller than the optimal width
                shrink_remaining -= w
            else:
                shrink_fields.append(field)

        return shrink_fields, shrink_remaining

    @staticmethod
    def _assign_max_widths(
        table: prettytable.PrettyTable,
        max_width: int,
        min_width: int = 0,
        fit_width: bool = False,
    ) -> None:
        """Set maximum widths for columns of table `x`,
        with the last column recieving either leftover columns
        or `min_width`, depending on what offers more space.
        """
        if max_width > 0:
            term_width = max_width
        elif not _do_fit(fit_width):
            # Fitting is disabled
            return None
        else:
            _term_width = utils.terminal_width()
            if not _term_width:
                # not a tty, so do not set any max widths
                return None
            term_width = _term_width
        field_count = len(table.field_names)

        try:
            first_line = table.get_string().splitlines()[0]
            if len(first_line) <= term_width:
                return None
        except IndexError:
            return None

        usable_total_width, optimal_width = TableFormatter._width_info(
            term_width, field_count
        )

        field_widths = TableFormatter._field_widths(
            table.field_names, first_line
        )

        shrink_fields, shrink_remaining = TableFormatter._build_shrink_fields(
            usable_total_width, optimal_width, field_widths, table.field_names
        )

        shrink_to = shrink_remaining // len(shrink_fields)
        # make all shrinkable fields size shrink_to apart from the last one
        for field in shrink_fields[:-1]:
            table.max_width[field] = max(min_width, shrink_to)
            shrink_remaining -= shrink_to

        # give the last shrinkable column any remaining shrink or min_width
        field = shrink_fields[-1]
        table.max_width[field] = max(min_width, shrink_remaining)
