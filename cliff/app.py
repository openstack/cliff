"""Application base class.
"""

import logging
import logging.handlers
import optparse
import os
import sys

LOG = logging.getLogger(__name__)


class App(object):
    """Application base class.
    """

    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG_FILE_MESSAGE_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
    DEFAULT_VERBOSE_LEVEL = 1

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
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
            )
        self.parser.add_option(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors',
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
        sys.exit(0)

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')

        # Set up logging to a file
        root_logger.setLevel(logging.DEBUG)
        file_handler = logging.handlers.RotatingFileHandler(
            self.NAME + '.log',
            maxBytes=10240,
            backupCount=1,
            )
        formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Send higher-level messages to the console, too
        console = logging.StreamHandler()
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)
        formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)
        return

    def run(self, argv):
        if not argv:
            argv = ['-h']
        self.options, remainder = self.parser.parse_args(argv)
        self.configure_logging()
        cmd_factory, cmd_name, sub_argv = self.command_manager.find_command(remainder)
        cmd = cmd_factory(self, self.options)
        cmd_parser = cmd.get_parser(' '.join([self.NAME, cmd_name]))
        parsed_args = cmd_parser.parse_args(sub_argv)
        return cmd.run(parsed_args)
