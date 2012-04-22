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
    LOG_FILE_MESSAGE_FORMAT = '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'
    DEFAULT_VERBOSE_LEVEL = 1

    def __init__(self, description, version, command_manager,
                 stdin=None, stdout=None, stderr=None):
        """Initialize the application.

        :param description: One liner explaining the program purpose
        :param version: String containing the application version number
        :param command_manager: A CommandManager instance
        :param stdin: Standard input stream
        :param stdout: Standard output stream
        :param stderr: Standard error output stream
        """
        self.command_manager = command_manager
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.parser = self.build_option_parser(description, version)

    def build_option_parser(self, description, version):
        """Return an optparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.
        """
        parser = optparse.OptionParser(
            description=description,
            version='%prog {}'.format(version),
            add_help_option=False,
            )
        parser.disable_interspersed_args()
        parser.add_option(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
            )
        parser.add_option(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors',
            )
        parser.add_option(
            '-h', action='help',
            help="show this help message and exit",
            )
        parser.add_option(
            '--help', action='callback',
            callback=self.show_verbose_help,
            help="show verbose help message and exit",
            )
        parser.add_option(
            '--debug', 
            default=False,
            action='store_true',
            help='show tracebacks on errors',
            )
        return parser

    def show_verbose_help(self, *args):
        """Displays the normal syntax info and a list of available subcommands.
        """
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

        # Send higher-level messages to the console via stderr
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

    def prepare_to_run_command(self, cmd):
        """Perform any preliminary work needed to run a command.
        """
        return

    def clean_up(self, cmd, result, err):
        """Hook run after a command is done to shutdown the app.
        """
        return

    def run(self, argv):
        """Equivalent to the main program for the application.
        """
        if not argv:
            argv = ['-h']
        self.options, remainder = self.parser.parse_args(argv)
        self.configure_logging()
        cmd_factory, cmd_name, sub_argv = self.command_manager.find_command(remainder)
        cmd = cmd_factory(self, self.options)
        err = None
        result = 1
        try:
            self.prepare_to_run_command(cmd)
            cmd_parser = cmd.get_parser(' '.join([self.NAME, cmd_name]))
            parsed_args = cmd_parser.parse_args(sub_argv)
            result = cmd.run(parsed_args)
        except Exception as err:
            if self.options.debug:
                LOG.exception(err)
                raise
            LOG.error('ERROR: %s', err)
        finally:
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    LOG.exception(err2)
                else:
                    LOG.error('Could not clean up: %s', err2)
        return result
