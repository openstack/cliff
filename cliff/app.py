"""Application base class.
"""

import logging
import optparse
import os
import sys

LOG = logging.getLogger(__name__)


class App(object):
    """Application base class.
    """

    NAME = os.path.basename(sys.argv[0])

    def __init__(self, description, version, command_manager):
        self.command_manager = command_manager
        self._build_parser(description, version)

    def _build_parser(self, description, version):
        self.parser = optparse.OptionParser(
            description=description,
            )
        self.parser.disable_interspersed_args()
        self.parser.add_option(
            '-v', '--verbose',
            action='count',
            dest='verbose',
            help='Increase verbosity of output. Can be repeated.',
            )
        # self.parser.add_option(
        #     '-V', '--version',
        #     action='version',
        #     version='%(prog)s {}'.format(version),
        #     )
        # FIXME(dhellmann): Add help option to list available commands.
        # subparsers = self.parser.add_subparsers(dest='command')
        # for name, factory in self.command_manager.commands.items():
        #     subparsers.add_parser(name)
        return

    def run(self, argv):
        parsed_args, remainder = self.parser.parse_args(argv)
        # FIXME(dhellmann): set up logging based on verbosity flag
        cmd_factory, cmd_name, sub_argv = self.command_manager.find_command(remainder)
        cmd = cmd_factory(self, parsed_args)
        cmd_parser = cmd.get_parser(' '.join([self.NAME, cmd_name]))
        parsed_args = cmd_parser.parse_args(sub_argv)
        return cmd.run(parsed_args)
