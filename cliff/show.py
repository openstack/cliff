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

"""Application base class for displaying data about a single object."""

import abc
import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from cliff import display
from cliff.formatters import base as base_formatters


class ShowOne(
    display.DisplayCommandBase[base_formatters.SingleFormatter],
    metaclass=abc.ABCMeta,
):
    """Command base class for displaying data about a single object."""

    @property
    def formatter_namespace(self) -> str:
        return 'cliff.formatter.show'

    @property
    def formatter_default(self) -> str:
        return 'table'

    @abc.abstractmethod
    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        """Run command.

        Return a tuple containing the column names and an iterable containing
        the data to be listed.
        """

    def produce_output(
        self,
        parsed_args: argparse.Namespace,
        column_names: Sequence[str],
        data: Sequence[Any],
    ) -> int:
        columns_to_include, selector = self._generate_columns_and_selector(
            parsed_args, column_names
        )
        if selector:
            data = list(self._compress_iterable(data, selector))
        self.formatter.emit_one(
            columns_to_include, data, self.app.stdout, parsed_args
        )
        return 0

    def dict2columns(
        self, data: dict[str, Any]
    ) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        """Implement the common task of converting a dict-based object
        to the two-column output that ShowOne expects.
        """
        if not data:
            return ((), ())
        else:
            return (tuple(data.keys()), tuple(data.values()))


class ShowOneWithDetails(
    display.DisplayCommandBase[base_formatters.ListFormatter],
    metaclass=abc.ABCMeta,
):
    """Display a single object's fields with additional columns.

    Each row starts with a field name, followed by its value and any
    additional details. The ``-c`` option selects fields (rows), not output
    columns. Output is rendered using list formatters.
    """

    @property
    def formatter_namespace(self) -> str:
        return 'cliff.formatter.list'

    @property
    def formatter_default(self) -> str:
        return 'table'

    @abc.abstractmethod
    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Sequence[Any]]]:
        """Return output column names and an iterable of field rows.

        The first item in each row must be a string containing the field
        name used for selection with ``-c``. The remaining items contain
        the field's value and additional details, in column order.
        """

    def produce_output(
        self,
        parsed_args: argparse.Namespace,
        column_names: Sequence[str],
        data: Iterable[Sequence[Any]],
    ) -> int:
        if parsed_args.columns:
            rows = list(data)
            field_names = [row[0] for row in rows]
            _, selector = self._generate_columns_and_selector(
                parsed_args, field_names
            )
            if selector:
                data = self._compress_iterable(rows, selector)

        self.formatter.emit_list(
            column_names, data, self.app.stdout, parsed_args
        )
        return 0
