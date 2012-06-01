"""Output formatters using shell syntax.
"""

from .base import SingleFormatter


class ShellFormatter(SingleFormatter):

    def add_argument_group(self, parser):
        group = parser.add_argument_group(
            title='shell formatter',
            description='a format a UNIX shell can parse (variable="value")',
            )
        group.add_argument(
            '--variable',
            action='append',
            default=[],
            dest='variables',
            metavar='VARIABLE',
            help='specify the variable(s) to include, can be repeated',
            )
        group.add_argument(
            '--prefix',
            action='store',
            default='',
            dest='prefix',
            help='add a prefix to all variable names',
            )

    def emit_one(self, column_names, data, stdout, parsed_args):
        variable_names = [c.lower().replace(' ', '_')
                          for c in column_names
                          ]
        desired_columns = parsed_args.variables
        for name, value in zip(variable_names, data):
            if name in desired_columns or not desired_columns:
                stdout.write('%s%s="%s"\n' % (parsed_args.prefix, name, value))
        return
