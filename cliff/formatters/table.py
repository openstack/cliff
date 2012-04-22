"""Output formatters using prettytable.
"""

import prettytable

from .base import ListFormatter


class TableLister(ListFormatter):

    ALIGNMENTS = {
        int: 'r',
        str: 'l',
        unicode: 'l',
        float: 'r',
        }

    def add_argument_group(self, parser):
        group = parser.add_argument_group('Table Formatter')
        group.add_argument(
            '-c', '--column',
            action='append',
            default=[],
            dest='columns',
            help='specify the column(s) to include, can be repeated',
            )

    def emit_list(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(column_names)
        x.set_padding_width(1)
        # Figure out the types of the columns in the
        # first row and set the alignment of the
        # output accordingly.
        data_iter = iter(data)
        first_row = next(data_iter)
        for value, name in zip(first_row, column_names):
            alignment = self.ALIGNMENTS.get(type(value), 'l')
            x.set_field_align(name, alignment)
        # Now iterate over the data and add the rows.
        x.add_row(first_row)
        for row in data_iter:
            x.add_row(row)
        formatted = x.get_string(fields=(parsed_args.columns or column_names))
        stdout.write(formatted)
        stdout.write('\n')
        return
