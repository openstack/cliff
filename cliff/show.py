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
import collections.abc
import typing as ty

from cliff import display


class ShowOne(display.DisplayCommandBase, metaclass=abc.ABCMeta):
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
    ) -> tuple[tuple[str, ...], tuple[ty.Any, ...]]:
        """Return a two-part tuple with a tuple of column names
        and a tuple of values.
        """

    def produce_output(
        self,
        parsed_args: argparse.Namespace,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Iterable[collections.abc.Sequence[ty.Any]],
    ) -> int:
        (columns_to_include, selector) = self._generate_columns_and_selector(
            parsed_args, column_names
        )
        if selector:
            data = list(self._compress_iterable(data, selector))
        self.formatter.emit_one(
            columns_to_include, data, self.app.stdout, parsed_args
        )
        return 0

    def dict2columns(
        self, data: dict[str, ty.Any]
    ) -> tuple[tuple[str, ...], tuple[ty.Any, ...]]:
        """Implement the common task of converting a dict-based object
        to the two-column output that ShowOne expects.
        """
        if not data:
            return ((), ())
        else:
            return (tuple(data.keys()), tuple(data.values()))
