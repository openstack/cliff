"""Output formatters using PyYAML.
"""

import yaml

from .base import ListFormatter, SingleFormatter
from cliff import columns


class YAMLFormatter(ListFormatter, SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        items = []
        for item in data:
            items.append(
                {n: (i.machine_readable()
                     if isinstance(i, columns.FormattableColumn)
                     else i)
                 for n, i in zip(column_names, item)}
            )
        yaml.safe_dump(items, stream=stdout, default_flow_style=False)

    def emit_one(self, column_names, data, stdout, parsed_args):
        for key, value in zip(column_names, data):
            dict_data = {
                key: (value.machine_readable()
                      if isinstance(value, columns.FormattableColumn)
                      else value)
            }
            yaml.safe_dump(dict_data, stream=stdout, default_flow_style=False)
