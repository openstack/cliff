"""Output formatters for JSON.
"""

import json

from .base import ListFormatter, SingleFormatter


class JSONFormatter(ListFormatter, SingleFormatter):

    def add_argument_group(self, parser):
        group = parser.add_argument_group(title='json formatter')
        group.add_argument(
            '--noindent',
            action='store_true',
            dest='noindent',
            help='whether to disable indenting the JSON'
        )

    def emit_list(self, column_names, data, stdout, parsed_args):
        items = []
        for item in data:
            items.append(dict(zip(column_names, item)))
        indent = None if parsed_args.noindent else 2
        json.dump(items, stdout, indent=indent)

    def emit_one(self, column_names, data, stdout, parsed_args):
        one = dict(zip(column_names, data))
        indent = None if parsed_args.noindent else 2
        json.dump(one, stdout, indent=indent)
