#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""Application base class."""

import itertools
import shlex
import sys
import typing as ty

import autopage.argparse
import cmd2

if ty.TYPE_CHECKING:
    from . import app as _app
    from . import commandmanager as _commandmanager


class InteractiveApp(cmd2.Cmd):
    """Provides "interactive mode" features.

    Refer to the cmd2_ and cmd_ documentation for details
    about subclassing and configuring this class.

    .. _cmd2: https://cmd2.readthedocs.io/en/latest/
    .. _cmd: http://docs.python.org/library/cmd.html

    :param parent_app: The calling application (expected to be derived
                       from :class:`cliff.app.App`).
    :param command_manager: A :class:`cliff.commandmanager.CommandManager`
                            instance.
    :param stdin: Standard input stream
    :param stdout: Standard output stream
    """

    use_rawinput = True
    doc_header = "Shell commands (type help <topic>):"
    app_cmd_header = "Application commands (type help <topic>):"

    def __init__(
        self,
        parent_app: '_app.App',
        command_manager: '_commandmanager.CommandManager',
        stdin: ty.Optional[ty.TextIO],
        stdout: ty.Optional[ty.TextIO],
        errexit: bool = False,
    ):
        self.parent_app = parent_app
        if not hasattr(sys.stdin, 'isatty') or sys.stdin.isatty():
            self.prompt = f'({parent_app.NAME}) '
        else:
            # batch/pipe mode
            self.prompt = ''
        self.command_manager = command_manager
        self.errexit = errexit
        cmd2.Cmd.__init__(self, 'tab', stdin=stdin, stdout=stdout)

    # def _split_line(self, line: cmd2.Statement) -> list[str]:
    def _split_line(self, line: ty.Union[str, cmd2.Statement]) -> list[str]:
        # cmd2 >= 0.9.1 gives us a Statement not a PyParsing parse
        # result.
        parts = shlex.split(line)
        if isinstance(line, cmd2.Statement):
            parts.insert(0, line.command)
        return parts

    def default(self, line: str) -> ty.Optional[bool]:  # type: ignore[override]
        # Tie in the default command processor to
        # dispatch commands known to the command manager.
        # We send the message through our parent app,
        # since it already has the logic for executing
        # the subcommand.
        line_parts = self._split_line(line)
        ret = self.parent_app.run_subcommand(line_parts)
        if self.errexit:
            # Only provide this if errexit is enabled,
            # otherise keep old behaviour
            return bool(ret)
        return None

    def completenames(self, text: str, *ignored: ty.Any) -> list[str]:
        """Tab-completion for command prefix without completer delimiter.

        This method returns cmd style and cliff style commands matching
        provided command prefix (text).
        """
        completions = cmd2.Cmd.completenames(self, text)
        completions += self._complete_prefix(text)
        return completions

    def completedefault(
        self, text: str, line: str, begidx: int, endidx: int
    ) -> list[str]:
        """Default tab-completion for command prefix with completer delimiter.

        This method filters only cliff style commands matching provided
        command prefix (line) as cmd2 style commands cannot contain spaces.
        This method returns text + missing command part of matching commands.
        This method does not handle options in cmd2/cliff style commands, you
        must define complete_$method to handle them.
        """
        return [x[begidx:] for x in self._complete_prefix(line)]

    def _complete_prefix(self, prefix: str) -> list[str]:
        """Returns cliff style commands with a specific prefix."""
        if not prefix:
            return [n for n, v in self.command_manager]
        return [n for n, v in self.command_manager if n.startswith(prefix)]

    def help_help(self) -> None:
        # Use the command manager to get instructions for "help"
        self.default('help help')

    def do_help(self, arg: ty.Optional[str]) -> None:
        if arg:
            # Check if the arg is a builtin command or something
            # coming from the command manager
            arg_parts = shlex.split(arg)
            method_name = '_'.join(
                itertools.chain(
                    ['do'],
                    itertools.takewhile(
                        lambda x: not x.startswith('-'), arg_parts
                    ),
                )
            )
            # Have the command manager version of the help
            # command produce the help text since cmd and
            # cmd2 do not provide help for "help"
            if hasattr(self, method_name):
                cmd2.Cmd.do_help(self, arg)
                return
            # Dispatch to the underlying help command,
            # which knows how to provide help for extension
            # commands.
            self.default(f'help {arg}')
        else:
            stdout = self.stdout
            try:
                with autopage.argparse.help_pager(stdout) as paged_out:  # type: ignore
                    self.stdout = paged_out

                    cmd2.Cmd.do_help(self, arg)  # type: ignore
                    cmd_names = sorted([n for n, v in self.command_manager])
                    self.print_topics(self.app_cmd_header, cmd_names, 15, 80)
            finally:
                self.stdout = stdout
        return

    # Create exit alias to quit the interactive shell.
    do_exit = cmd2.Cmd.do_quit

    def get_names(self) -> list[str]:
        # Override the base class version to filter out
        # things that look like they should be hidden
        # from the user.
        return [
            n for n in cmd2.Cmd.get_names(self) if not n.startswith('do__')
        ]

    def precmd(
        self, statement: ty.Union[cmd2.Statement, str]
    ) -> cmd2.Statement:
        """Hook method executed just before the command is executed by
        :meth:`~cmd2.Cmd.onecmd` and after adding it to history.

        :param statement: subclass of str which also contains the parsed input
        :return: a potentially modified version of the input Statement object
        """
        statement = super().precmd(statement)

        # NOTE(mordred): The above docstring is copied in from cmd2 because
        # current cmd2 has a docstring that sphinx finds if we don't override
        # it, and it breaks sphinx.

        # Pre-process the parsed command in case it looks like one of
        # our subcommands, since cmd2 does not handle multi-part
        # command names by default.
        line_parts = self._split_line(statement)
        try:
            the_cmd = self.command_manager.find_command(line_parts)
            cmd_factory, cmd_name, sub_argv = the_cmd
        except ValueError:
            # Not a plugin command
            pass
        else:
            statement = cmd2.Statement(
                ' '.join(sub_argv),
                raw=statement.raw,
                command=cmd_name,
                arg_list=sub_argv,
                multiline_command=statement.multiline_command,
                terminator=statement.terminator,
                suffix=statement.suffix,
                pipe_to=statement.pipe_to,
                output=statement.output,
                output_to=statement.output_to,
            )
        return statement

    def cmdloop(self, intro: ty.Optional[str] = None) -> None:  # type: ignore[override]
        # We don't want the cmd2 cmdloop() behaviour, just call the old one
        # directly.  In part this is because cmd2.cmdloop() doe not return
        # anything useful and we want to have a useful exit code.
        # FIXME(stephenfin): The above is no longer true: _cmdloop now returns
        # nothing.
        self._cmdloop()
