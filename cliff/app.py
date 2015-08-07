"""Application base class.
"""

import argparse
import codecs
import inspect
import locale
import logging
import logging.handlers
import os
import sys
import operator

from .complete import CompleteCommand
from .help import HelpAction, HelpCommand
from .utils import damerau_levenshtein, COST

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
    LOG = logging.getLogger(NAME)

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'
    DEFAULT_VERBOSE_LEVEL = 1
    DEFAULT_OUTPUT_ENCODING = 'utf-8'

    def __init__(self, description, version, command_manager,
                 stdin=None, stdout=None, stderr=None,
                 interactive_app_factory=None,
                 deferred_help=False):
        """Initialize the application.
        """
        self.command_manager = command_manager
        self.command_manager.add_command('help', HelpCommand)
        self.command_manager.add_command('complete', CompleteCommand)
        self._set_streams(stdin, stdout, stderr)
        self.interactive_app_factory = interactive_app_factory
        self.deferred_help = deferred_help
        self.parser = self.build_option_parser(description, version)
        self.interactive_mode = False
        self.interpreter = None

    def _set_streams(self, stdin, stdout, stderr):
        try:
            locale.setlocale(locale.LC_ALL, '')
        except locale.Error:
            pass
        if sys.version_info[:2] == (2, 6):
            # Configure the input and output streams. If a stream is
            # provided, it must be configured correctly by the
            # caller. If not, make sure the versions of the standard
            # streams used by default are wrapped with encodings. This
            # works around a problem with Python 2.6 fixed in 2.7 and
            # later (http://hg.python.org/cpython/rev/e60ef17561dc/).
            lang, encoding = locale.getdefaultlocale()
            encoding = (getattr(sys.stdout, 'encoding', None) or
                        encoding or
                        self.DEFAULT_OUTPUT_ENCODING)
            self.stdin = stdin or codecs.getreader(encoding)(sys.stdin)
            self.stdout = stdout or codecs.getwriter(encoding)(sys.stdout)
            self.stderr = stderr or codecs.getwriter(encoding)(sys.stderr)
        else:
            self.stdin = stdin or sys.stdin
            self.stdout = stdout or sys.stdout
            self.stderr = stderr or sys.stderr

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
            help='Suppress output except warnings and errors.',
        )
        if self.deferred_help:
            parser.add_argument(
                '-h', '--help',
                dest='deferred_help',
                action='store_true',
                help="Show help message and exit.",
            )
        else:
            parser.add_argument(
                '-h', '--help',
                action=HelpAction,
                nargs=0,
                default=self,  # tricky
                help="Show this help message and exit.",
            )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
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

    def print_help_if_requested(self):
        """Print help and exits if deferred help is enabled and requested.

        '--help' shows the help message and exits:
         * without calling initialize_app if not self.deferred_help (default),
         * after initialize_app call if self.deferred_help,
         * during initialize_app call if self.deferred_help and subclass calls
           explicitly this method in initialize_app.
        """
        if self.deferred_help and self.options.deferred_help:
            action = HelpAction(None, None, default=self)
            action(self.parser, self.options, None, None)

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
            self.configure_logging()
            self.interactive_mode = not remainder
            if self.deferred_help and self.options.deferred_help and remainder:
                # When help is requested and `remainder` has any values disable
                # `deferred_help` and instead allow the help subcommand to
                # handle the request during run_subcommand(). This turns
                # "app foo bar --help" into "app help foo bar". However, when
                # `remainder` is empty use print_help_if_requested() to allow
                # for an early exit.
                # Disabling `deferred_help` here also ensures that
                # print_help_if_requested will not fire if called by a subclass
                # during its initialize_app().
                self.options.deferred_help = False
                remainder.insert(0, "help")
            self.initialize_app(remainder)
            self.print_help_if_requested()
        except Exception as err:
            if hasattr(self, 'options'):
                debug = self.options.debug
            else:
                debug = True
            if debug:
                self.LOG.exception(err)
                raise
            else:
                self.LOG.error(err)
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
        # Defer importing .interactive as cmd2 is a slow import
        from .interactive import InteractiveApp

        if self.interactive_app_factory is None:
            self.interactive_app_factory = InteractiveApp
        self.interpreter = self.interactive_app_factory(self,
                                                        self.command_manager,
                                                        self.stdin,
                                                        self.stdout,
                                                        )
        self.interpreter.cmdloop()
        return 0

    def get_fuzzy_matches(self, cmd):
        """return fuzzy matches of unknown command
        """

        sep = '_'
        if self.command_manager.convert_underscores:
            sep = ' '
        all_cmds = [k[0] for k in self.command_manager]
        dist = []
        for candidate in sorted(all_cmds):
            prefix = candidate.split(sep)[0]
            # Give prefix match a very good score
            if candidate.startswith(cmd):
                dist.append((candidate, 0))
                continue
            # Levenshtein distance
            dist.append((candidate, damerau_levenshtein(cmd, prefix, COST)+1))
        dist = sorted(dist, key=operator.itemgetter(1, 0))
        matches = []
        i = 0
        # Find the best similarity
        while (not dist[i][1]):
            matches.append(dist[i][0])
            i += 1
        best_similarity = dist[i][1]
        while (dist[i][1] == best_similarity):
            matches.append(dist[i][0])
            i += 1

        return matches

    def run_subcommand(self, argv):
        try:
            subcommand = self.command_manager.find_command(argv)
        except ValueError as err:
            # If there was no exact match, try to find a fuzzy match
            the_cmd = argv[0]
            fuzzy_matches = self.get_fuzzy_matches(the_cmd)
            if fuzzy_matches:
                article = 'a'
                if self.NAME[0] in 'aeiou':
                    article = 'an'
                self.stdout.write('%s: \'%s\' is not %s %s command. '
                                  'See \'%s --help\'.\n'
                                  % (self.NAME, the_cmd, article,
                                      self.NAME, self.NAME))
                self.stdout.write('Did you mean one of these?\n')
                for match in fuzzy_matches:
                    self.stdout.write('  %s\n' % match)
            else:
                if self.options.debug:
                    raise
                else:
                    self.LOG.error(err)
            return 2
        cmd_factory, cmd_name, sub_argv = subcommand
        kwargs = {}
        if 'cmd_name' in inspect.getargspec(cmd_factory.__init__).args:
            kwargs['cmd_name'] = cmd_name
        cmd = cmd_factory(self, self.options, **kwargs)
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
                self.LOG.exception(err)
            else:
                self.LOG.error(err)
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    self.LOG.exception(err2)
                else:
                    self.LOG.error('Could not clean up: %s', err2)
            if self.options.debug:
                raise
        else:
            try:
                self.clean_up(cmd, result, None)
            except Exception as err3:
                if self.options.debug:
                    self.LOG.exception(err3)
                else:
                    self.LOG.error('Could not clean up: %s', err3)
        return result
