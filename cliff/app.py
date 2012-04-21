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
            version='%prog {}'.format(version),
            add_help_option=False,
            )
        self.parser.disable_interspersed_args()
        self.parser.add_option(
            '-v', '--verbose',
            action='count',
            dest='verbose',
            help='Increase verbosity of output. Can be repeated.',
            )
        self.parser.add_option(
            '-h', action='help',
            help="show this help message and exit",
            )
        self.parser.add_option(
            '--help', action='callback',
            callback=self.show_verbose_help,
            help="show verbose help message and exit",
            )
        return

    def show_verbose_help(self, *args):
        self.parser.print_help()
        print('')
        print('Commands:')
        for name, ep in sorted(self.command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            print('  %-13s  %s' % (name, cmd.get_description()))
        raise SystemExit()

    def run(self, argv):
        parsed_args, remainder = self.parser.parse_args(argv)
        # FIXME(dhellmann): set up logging based on verbosity flag
        cmd_factory, cmd_name, sub_argv = self.command_manager.find_command(remainder)
        cmd = cmd_factory(self, parsed_args)
        cmd_parser = cmd.get_parser(' '.join([self.NAME, cmd_name]))
        parsed_args = cmd_parser.parse_args(sub_argv)
        return cmd.run(parsed_args)
