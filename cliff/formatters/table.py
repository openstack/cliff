"""Output formatters using prettytable.
"""

import prettytable

from .base import ListFormatter, SingleFormatter


class TableFormatter(ListFormatter, SingleFormatter):

    ALIGNMENTS = {
        int: 'r',
        str: 'l',
        unicode: 'l',
        float: 'r',
        }

    def add_argument_group(self, parser):
        group = parser.add_argument_group(
            title='table formatter',
            description='Pretty-print output in a table',
            )
        group.add_argument(
            '-c', '--column',
            action='append',
            default=[],
            dest='columns',
            metavar='COLUMN',
            help='specify the column(s) to include, can be repeated',
            )

    def emit_list(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(column_names)
        x.set_padding_width(1)
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
                x.set_field_align(name, alignment)
            # Now iterate over the data and add the rows.
            x.add_row(first_row)
            for row in data_iter:
                x.add_row(row)
        formatted = x.get_string(fields=(parsed_args.columns or column_names))
        stdout.write(formatted)
        stdout.write('\n')
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(('Field', 'Value'))
        x.set_padding_width(1)
        # Align all columns left because the values are
        # not all the same type.
        x.set_field_align('Field', 'l')
        x.set_field_align('Value', 'l')
        desired_columns = parsed_args.columns
        for name, value in zip(column_names, data):
            if name in desired_columns or not desired_columns:
                x.add_row((name, value))
        formatted = x.get_string(fields=('Field', 'Value'))
        stdout.write(formatted)
        stdout.write('\n')
        return
