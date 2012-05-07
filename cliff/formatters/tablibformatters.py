"""Output formatters using tablib.
"""

from .base import ListFormatter, SingleFormatter

import tablib


class TablibFormatterBase(ListFormatter, SingleFormatter):

    def add_argument_group(self, parser):
        return

    def emit_list(self, column_names, data, stdout, parsed_args):
        dataset = tablib.Dataset(headers=column_names)
        for row in data:
            dataset.append(row)
        stdout.write(self._format_dataset(dataset))
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        dataset = tablib.Dataset(headers=('Field', 'Value'))
        for name, value in zip(column_names, data):
            dataset.append((name, value))
        stdout.write(self._format_dataset(dataset))
        return


class YamlFormatter(TablibFormatterBase):
    """YAML output"""

    def _format_dataset(self, dataset):
        return dataset.yaml


class HtmlFormatter(TablibFormatterBase):
    """HTML output"""

    def _format_dataset(self, dataset):
        return dataset.html


class JsonFormatter(TablibFormatterBase):
    """JSON output"""

    def _format_dataset(self, dataset):
        return dataset.json
