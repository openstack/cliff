"""Application base class for displaying data.
"""
import abc

try:
    from itertools import compress
except ImportError:
    # for py26 compat
    from itertools import izip

    def compress(data, selectors):
        return (d for d, s in izip(data, selectors) if s)

import logging

import six
import stevedore

from .command import Command


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class DisplayCommandBase(Command):
    """Command base class for displaying data about a single object.
    """

    def __init__(self, app, app_args, cmd_name=None):
        super(DisplayCommandBase, self).__init__(app, app_args,
                                                 cmd_name=cmd_name)
        self._formatter_plugins = self._load_formatter_plugins()

    @abc.abstractproperty
    def formatter_namespace(self):
        "String specifying the namespace to use for loading formatter plugins."

    @abc.abstractproperty
    def formatter_default(self):
        "String specifying the name of the default formatter."

    def _load_formatter_plugins(self):
        # Here so tests can override
        return stevedore.ExtensionManager(
            self.formatter_namespace,
            invoke_on_load=True,
        )

    def get_parser(self, prog_name):
        parser = super(DisplayCommandBase, self).get_parser(prog_name)
        formatter_group = parser.add_argument_group(
            title='output formatters',
            description='output formatter options',
        )
        formatter_choices = sorted(self._formatter_plugins.names())
        formatter_default = self.formatter_default
        if formatter_default not in formatter_choices:
            formatter_default = formatter_choices[0]
        formatter_group.add_argument(
            '-f', '--format',
            dest='formatter',
            action='store',
            choices=formatter_choices,
            default=formatter_default,
            help='the output format, defaults to %s' % formatter_default,
        )
        formatter_group.add_argument(
            '-c', '--column',
            action='append',
            default=[],
            dest='columns',
            metavar='COLUMN',
            help='specify the column(s) to include, can be repeated',
        )
        for formatter in self._formatter_plugins:
            formatter.obj.add_argument_group(parser)
        return parser

    @abc.abstractmethod
    def produce_output(self, parsed_args, column_names, data):
        """Use the formatter to generate the output.

        :param parsed_args: argparse.Namespace instance with argument values
        :param column_names: sequence of strings containing names
                             of output columns
        :param data: iterable with values matching the column names
        """

    def run(self, parsed_args):
        self.formatter = self._formatter_plugins[parsed_args.formatter].obj
        column_names, data = self.take_action(parsed_args)
        self.produce_output(parsed_args, column_names, data)
        return 0

    @staticmethod
    def _compress_iterable(iterable, selectors):
        return compress(iterable, selectors)
