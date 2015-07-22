"""Output formatters using prettytable.
"""

import prettytable
import six

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
        group = parser.add_argument_group('table formatter')
        group.add_argument(
            '--max-width',
            metavar='<integer>',
            default=0,
            type=int,
            help='Maximum display width, 0 to disable',
        )

    def emit_list(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(
            column_names,
            print_empty=False,
        )
        x.padding_width = 1
        if parsed_args.max_width > 0:
            x.max_width = int(parsed_args.max_width)
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
                row = [r.replace('\r\n', '\n').replace('\r', ' ')
                       if isinstance(r, six.string_types) else r
                       for r in row]
                x.add_row(row)
        formatted = x.get_string(fields=column_names)
        stdout.write(formatted)
        stdout.write('\n')
        return

    def emit_one(self, column_names, data, stdout, parsed_args):
        x = prettytable.PrettyTable(field_names=('Field', 'Value'),
                                    print_empty=False)
        x.padding_width = 1
        if parsed_args.max_width > 0:
            x.max_width = int(parsed_args.max_width)
        # Align all columns left because the values are
        # not all the same type.
        x.align['Field'] = 'l'
        x.align['Value'] = 'l'
        for name, value in zip(column_names, data):
            value = (value.replace('\r\n', '\n').replace('\r', ' ') if
                     isinstance(value, six.string_types) else value)
            x.add_row((name, value))
        formatted = x.get_string(fields=('Field', 'Value'))
        stdout.write(formatted)
        stdout.write('\n')
        return
