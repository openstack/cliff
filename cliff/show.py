"""Application base class for displaying data about a single object.
"""
import abc
import logging

import pkg_resources

from .command import Command


LOG = logging.getLogger(__name__)


class ShowOne(Command):
    """Command base class for displaying data about a single object.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, app, app_args):
        super(ShowOne, self).__init__(app, app_args)
        self.load_formatter_plugins()

    def load_formatter_plugins(self):
        self.formatters = {}
        for ep in pkg_resources.iter_entry_points('cliff.formatter.show'):
            try:
                self.formatters[ep.name] = ep.load()()
            except Exception as err:
                LOG.error(err)
                if self.app_args.debug:
                    raise

    def get_parser(self, prog_name):
        parser = super(ShowOne, self).get_parser(prog_name)
        formatter_group = parser.add_argument_group(
            title='Output Formatters',
            description='List output formatter options',
            )
        formatter_choices = sorted(self.formatters.keys())
        formatter_default = 'table'
        if formatter_default not in formatter_choices:
            formatter_default = formatter_choices[0]
        formatter_group.add_argument(
            '-f', '--format',
            dest='formatter',
            action='store',
            choices=formatter_choices,
            default=formatter_default,
            help='the output format to use, defaults to %s' % formatter_default,
            )
        for name, formatter in sorted(self.formatters.items()):
            formatter.add_argument_group(parser)
        return parser

    @abc.abstractmethod
    def get_data(self, parsed_args):
        """Return a two-part tuple with a tuple of column names
        and a tuple of values.
        """

    def run(self, parsed_args):
        column_names, data = self.get_data(parsed_args)
        formatter = self.formatters[parsed_args.formatter]
        formatter.emit_one(column_names, data, self.app.stdout, parsed_args)
        return 0
