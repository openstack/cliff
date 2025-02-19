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

"""Application base class for providing a list of data as output."""

import abc
import argparse
import collections.abc
import logging
import typing as ty

from cliff import _argparse
from cliff import display


class Lister(display.DisplayCommandBase, metaclass=abc.ABCMeta):
    """Command base class for providing a list of data as output."""

    log = logging.getLogger(__name__)

    @property
    def formatter_namespace(self) -> str:
        return 'cliff.formatter.list'

    @property
    def formatter_default(self) -> str:
        return 'table'

    @property
    def need_sort_by_cliff(self) -> bool:
        """Whether sort procedure is performed by cliff itself.

        Should be overridden (return False) when there is a need to implement
        custom sorting procedure or data is already sorted.
        """
        return True

    @abc.abstractmethod
    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[
        collections.abc.Sequence[str], collections.abc.Iterable[ty.Any]
    ]:
        """Run command.

        Return a tuple containing the column names and an iterable containing
        the data to be listed.
        """

    def get_parser(self, prog_name: str) -> _argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        group = self._formatter_group
        group.add_argument(
            '--sort-column',
            action='append',
            default=[],
            dest='sort_columns',
            metavar='SORT_COLUMN',
            help=(
                'specify the column(s) to sort the data (columns specified '
                'first have a priority, non-existing columns are ignored), '
                'can be repeated'
            ),
        )
        sort_dir_group = group.add_mutually_exclusive_group()
        sort_dir_group.add_argument(
            '--sort-ascending',
            action='store_const',
            dest='sort_direction',
            const='asc',
            help=('sort the column(s) in ascending order'),
        )
        sort_dir_group.add_argument(
            '--sort-descending',
            action='store_const',
            dest='sort_direction',
            const='desc',
            help=('sort the column(s) in descending order'),
        )
        return parser

    def produce_output(
        self,
        parsed_args: argparse.Namespace,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Iterable[collections.abc.Sequence[ty.Any]],
    ) -> int:
        if parsed_args.sort_columns and self.need_sort_by_cliff:
            indexes = [
                column_names.index(c)
                for c in parsed_args.sort_columns
                if c in column_names
            ]
            reverse = parsed_args.sort_direction == 'desc'
            for index in indexes[::-1]:
                try:
                    # We need to handle unset values (i.e. None) so we sort on
                    # multiple conditions: the first comparing the results of
                    # an 'is None' type check and the second comparing the
                    # actual value. The second condition will only be checked
                    # if the first returns True, which only happens if the
                    # returns from the 'is None' check on the two values are
                    # the same, i.e. both None or both not-None
                    data = sorted(
                        data,
                        key=lambda k: (k[index] is None, k[index]),
                        reverse=reverse,
                    )
                except TypeError:
                    # Simply log and then ignore this; sorting is best effort
                    self.log.warning(
                        "Could not sort on field '%s'; unsortable types",
                        parsed_args.sort_columns[index],
                    )

        columns_to_include, selector = self._generate_columns_and_selector(
            parsed_args,
            column_names,
        )
        if selector:
            # Generator expression to only return the parts of a row
            # of data that the user has expressed interest in
            # seeing. We have to convert the compress() output to a
            # list so the table formatter can ask for its length.
            data = (
                list(self._compress_iterable(row, selector)) for row in data
            )

        self.formatter.emit_list(
            columns_to_include,
            data,
            self.app.stdout,
            parsed_args,
        )

        return 0
