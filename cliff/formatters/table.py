"""Output formatters using prettytable.
"""

import prettytable

from .base import ListFormatter, SingleFormatter


class TableFormatter(ListFormatter, SingleFormatter):

    ALIGNMENTS = {
        int: 'r',
        str: 'l',
        float: 'r',
        }
    try:
        ALIGNMENTS[unicode] = 'l'
    except NameError:
        pass

    def add_argument_group(self, parser):
        pass

    def emit_list(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(column_names)
        x.padding_width = 1
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
                x.align[name] = alignment
            # Now iterate over the data and add the rows.
            x.add_row(first_row)
            for row in data_iter:
                x.add_row(row)
        formatted = x.get_string(fields=column_names)
        stdout.write(formatted)
        stdout.write('\n')
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(field_names=('Field', 'Value'))
        x.padding_width = 1
        # Align all columns left because the values are
        # not all the same type.
        x.align['Field'] = 'l'
        x.align['Value'] = 'l'
        for name, value in zip(column_names, data):
            x.add_row((name, value))
        formatted = x.get_string(fields=('Field', 'Value'))
        stdout.write(formatted)
        stdout.write('\n')
        return
