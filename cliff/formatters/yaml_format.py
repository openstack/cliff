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

"""Output formatters using PyYAML."""

import argparse
import collections.abc
import typing as ty

from cliff import columns
from cliff.formatters import base


def _yaml_friendly(value: ty.Any) -> ty.Any:
    if isinstance(value, columns.FormattableColumn):
        return value.machine_readable()
    elif hasattr(value, "toDict"):
        return value.toDict()
    elif hasattr(value, "to_dict"):
        return value.to_dict()
    else:
        return value


class YAMLFormatter(base.ListFormatter, base.SingleFormatter):
    def add_argument_group(self, parser: argparse.ArgumentParser) -> None:
        pass

    def emit_list(
        self,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Iterable[collections.abc.Sequence[ty.Any]],
        stdout: ty.TextIO,
        parsed_args: argparse.Namespace,
    ) -> None:
        # the yaml import is slow, so defer loading until we know we want it
        import yaml

        items = []
        for item in data:
            items.append(
                {n: _yaml_friendly(i) for n, i in zip(column_names, item)}
            )
        yaml.safe_dump(items, stream=stdout, default_flow_style=False)

    def emit_one(
        self,
        column_names: collections.abc.Sequence[str],
        data: collections.abc.Sequence[ty.Any],
        stdout: ty.TextIO,
        parsed_args: argparse.Namespace,
    ) -> None:
        # the yaml import is slow, so defer loading until we know we want it
        import yaml

        for key, value in zip(column_names, data):
            dict_data = {key: _yaml_friendly(value)}
            yaml.safe_dump(dict_data, stream=stdout, default_flow_style=False)
