"""Application base class.
"""

import argparse
import logging
import logging.handlers
import os
import sys

from .help import HelpAction, HelpCommand
from .interactive import InteractiveApp

# Make sure the cliff library has a logging handler
# in case the app developer doesn't set up logging.
# For py26 compat, create a NullHandler

if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

logging.getLogger('cliff').addHandler(NullHandler())


LOG = logging.getLogger(__name__)


class App(object):
    """Application base class.

    :param description: one-liner explaining the program purpose
    :paramtype description: str
    :param version: application version number
    :paramtype version: str
    :param command_manager: plugin loader
    :paramtype command_manager: cliff.commandmanager.CommandManager
    :param stdin: Standard input stream
    :paramtype stdin: readable I/O stream
    :param stdout: Standard output stream
    :paramtype stdout: writable I/O stream
    :param stderr: Standard error output stream
    :paramtype stderr: writable I/O stream
    :param interactive_app_factory: callable to create an
                                    interactive application
    :paramtype interactive_app_factory: cliff.interactive.InteractiveApp
    """

    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'
    DEFAULT_VERBOSE_LEVEL = 1

    def __init__(self, description, version, command_manager,
                 stdin=None, stdout=None, stderr=None,
                 interactive_app_factory=InteractiveApp):
        """Initialize the application.
        """
        self.command_manager = command_manager
        self.command_manager.add_command('help', HelpCommand)
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.interactive_app_factory = interactive_app_factory
        self.parser = self.build_option_parser(description, version)
        self.interactive_mode = False

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
            )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
            )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
            )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors',
            )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit",
            )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='show tracebacks on errors',
            )
        return parser

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        # Set up logging to a file
        if self.options.log_file:
            file_handler = logging.FileHandler(
                filename=self.options.log_file,
                )
            formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
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
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
            self.configure_logging()
            self.interactive_mode = not remainder
            self.initialize_app(remainder)
        except Exception as err:
            if hasattr(self, 'options'):
                debug = self.options.debug
            else:
                debug = True
            if debug:
                LOG.exception(err)
                raise
            else:
                LOG.error(err)
            return 1
        result = 1
        if self.interactive_mode:
            result = self.interact()
        else:
            result = self.run_subcommand(remainder)
        return result

    # FIXME(dhellmann): Consider moving these command handling methods
    # to a separate class.
    def initialize_app(self, argv):
        """Hook for subclasses to take global initialization action
        after the arguments are parsed but before a command is run.
        Invoked only once, even in interactive mode.

        :param argv: List of arguments, including the subcommand to run.
                     Empty for interactive mode.
        """
        return

    def prepare_to_run_command(self, cmd):
        """Perform any preliminary work needed to run a command.

        :param cmd: command processor being invoked
        :paramtype cmd: cliff.command.Command
        """
        return

    def clean_up(self, cmd, result, err):
        """Hook run after a command is done to shutdown the app.

        :param cmd: command processor being invoked
        :paramtype cmd: cliff.command.Command
        :param result: return value of cmd
        :paramtype result: int
        :param err: exception or None
        :paramtype err: Exception
        """
        return

    def interact(self):
        interpreter = self.interactive_app_factory(self,
                                                   self.command_manager,
                                                   self.stdin,
                                                   self.stdout,
                                                   )
        interpreter.cmdloop()
        return 0

    def run_subcommand(self, argv):
        subcommand = self.command_manager.find_command(argv)
        cmd_factory, cmd_name, sub_argv = subcommand
        cmd = cmd_factory(self, self.options)
        err = None
        result = 1
        try:
            self.prepare_to_run_command(cmd)
            full_name = (cmd_name
                         if self.interactive_mode
                         else ' '.join([self.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            parsed_args = cmd_parser.parse_args(sub_argv)
            result = cmd.run(parsed_args)
        except Exception as err:
            if self.options.debug:
                LOG.exception(err)
            else:
                LOG.error(err)
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    LOG.exception(err2)
                else:
                    LOG.error('Could not clean up: %s', err2)
            if self.options.debug:
                raise
        else:
            try:
                self.clean_up(cmd, result, None)
            except Exception as err3:
                if self.options.debug:
                    LOG.exception(err3)
                else:
                    LOG.error('Could not clean up: %s', err3)
        return result
