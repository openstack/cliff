"""Output formatters using PyYAML.
"""

import yaml

from .base import ListFormatter, SingleFormatter


class YAMLFormatter(ListFormatter, SingleFormatter):

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        items = []
        for item in data:
            items.append(dict(zip(column_names, item)))
        yaml.safe_dump(items, stream=stdout, default_flow_style=False)

    def emit_one(self, column_names, data, stdout, parsed_args):
        for key, value in zip(column_names, data):
            dict_data = {key: value}
            yaml.safe_dump(dict_data, stream=stdout, default_flow_style=False)
