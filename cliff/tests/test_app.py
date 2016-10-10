# -*- encoding: utf-8 -*-
#
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

import argparse
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import codecs
import locale
import mock
import six
import sys

from cliff import app as application
from cliff import command as c_cmd
from cliff import commandmanager
from cliff.tests import utils as test_utils
from cliff import utils


def make_app(**kwargs):
    cmd_mgr = commandmanager.CommandManager('cliff.tests')

    # Register a command that succeeds
    command = mock.MagicMock(spec=c_cmd.Command)
    command_inst = mock.MagicMock(spec=c_cmd.Command)
    command_inst.run.return_value = 0
    command.return_value = command_inst
    cmd_mgr.add_command('mock', command)

    # Register a command that fails
    err_command = mock.Mock(name='err_command', spec=c_cmd.Command)
    err_command_inst = mock.Mock(spec=c_cmd.Command)
    err_command_inst.run = mock.Mock(
        side_effect=RuntimeError('test exception')
    )
    err_command.return_value = err_command_inst
    cmd_mgr.add_command('error', err_command)

    app = application.App('testing interactive mode',
                          '1',
                          cmd_mgr,
                          stderr=mock.Mock(),  # suppress warning messages
                          **kwargs
                          )
    return app, command


def test_no_args_triggers_interactive_mode():
    app, command = make_app()
    app.interact = mock.MagicMock(name='inspect')
    app.run([])
    app.interact.assert_called_once_with()


def test_interactive_mode_cmdloop():
    app, command = make_app()
    app.interactive_app_factory = mock.MagicMock(
        name='interactive_app_factory'
    )
    assert app.interpreter is None
    app.run([])
    assert app.interpreter is not None
    app.interactive_app_factory.return_value.cmdloop.assert_called_once_with()


def test_initialize_app():
    app, command = make_app()
    app.initialize_app = mock.MagicMock(name='initialize_app')
    app.run(['mock'])
    app.initialize_app.assert_called_once_with(['mock'])


def test_prepare_to_run_command():
    app, command = make_app()
    app.prepare_to_run_command = mock.MagicMock(name='prepare_to_run_command')
    app.run(['mock'])
    app.prepare_to_run_command.assert_called_once_with(command())


def test_clean_up_success():
    app, command = make_app()
    app.clean_up = mock.MagicMock(name='clean_up')
    app.run(['mock'])
    app.clean_up.assert_called_once_with(command.return_value, 0, None)


def test_clean_up_error():
    app, command = make_app()

    app.clean_up = mock.MagicMock(name='clean_up')
    app.run(['error'])

    app.clean_up.assert_called_once_with(mock.ANY, mock.ANY, mock.ANY)
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 1, mock.ANY)
    args, kwargs = call_args
    assert isinstance(args[2], RuntimeError)
    assert args[2].args == ('test exception',)


def test_clean_up_error_debug():
    app, command = make_app()

    app.clean_up = mock.MagicMock(name='clean_up')
    try:
        app.run(['--debug', 'error'])
    except RuntimeError as err:
        assert app.clean_up.call_args_list[0][0][2] is err
    else:
        assert False, 'Should have had an exception'

    assert app.clean_up.called
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 1, mock.ANY)
    args, kwargs = call_args
    assert isinstance(args[2], RuntimeError)
    assert args[2].args == ('test exception',)


def test_error_handling_clean_up_raises_exception():
    app, command = make_app()

    app.clean_up = mock.MagicMock(
        name='clean_up',
        side_effect=RuntimeError('within clean_up'),
    )
    app.run(['error'])

    assert app.clean_up.called
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 1, mock.ANY)
    args, kwargs = call_args
    assert isinstance(args[2], RuntimeError)
    assert args[2].args == ('test exception',)


def test_error_handling_clean_up_raises_exception_debug():
    app, command = make_app()

    app.clean_up = mock.MagicMock(
        name='clean_up',
        side_effect=RuntimeError('within clean_up'),
    )
    try:
        app.run(['--debug', 'error'])
    except RuntimeError as err:
        if not hasattr(err, '__context__'):
            # The exception passed to clean_up is not the exception
            # caused *by* clean_up.  This test is only valid in python
            # 2 because under v3 the original exception is re-raised
            # with the new one as a __context__ attribute.
            assert app.clean_up.call_args_list[0][0][2] is not err
    else:
        assert False, 'Should have had an exception'

    assert app.clean_up.called
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 1, mock.ANY)
    args, kwargs = call_args
    assert isinstance(args[2], RuntimeError)
    assert args[2].args == ('test exception',)


def test_normal_clean_up_raises_exception():
    app, command = make_app()

    app.clean_up = mock.MagicMock(
        name='clean_up',
        side_effect=RuntimeError('within clean_up'),
    )
    app.run(['mock'])

    assert app.clean_up.called
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 0, None)


def test_normal_clean_up_raises_exception_debug():
    app, command = make_app()

    app.clean_up = mock.MagicMock(
        name='clean_up',
        side_effect=RuntimeError('within clean_up'),
    )
    app.run(['--debug', 'mock'])

    assert app.clean_up.called
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 0, None)


def test_build_option_parser_conflicting_option_should_throw():
    class MyApp(application.App):
        def __init__(self):
            super(MyApp, self).__init__(
                description='testing',
                version='0.1',
                command_manager=commandmanager.CommandManager('tests'),
            )

        def build_option_parser(self, description, version):
            parser = super(MyApp, self).build_option_parser(description,
                                                            version)
            parser.add_argument(
                '-h', '--help',
                default=self,  # tricky
                help="Show help message and exit.",
            )

    # TODO: tests should really use unittest2.
    try:
        MyApp()
    except argparse.ArgumentError:
        pass
    else:
        raise Exception('Exception was not thrown')


def test_option_parser_conflicting_option_custom_arguments_should_not_throw():
    class MyApp(application.App):
        def __init__(self):
            super(MyApp, self).__init__(
                description='testing',
                version='0.1',
                command_manager=commandmanager.CommandManager('tests'),
            )

        def build_option_parser(self, description, version):
            argparse_kwargs = {'conflict_handler': 'resolve'}
            parser = super(MyApp, self).build_option_parser(
                description,
                version,
                argparse_kwargs=argparse_kwargs)
            parser.add_argument(
                '-h', '--help',
                default=self,  # tricky
                help="Show help message and exit.",
            )

    MyApp()


def test_option_parser_abbrev_issue():
    class MyCommand(c_cmd.Command):
        def get_parser(self, prog_name):
            parser = super(MyCommand, self).get_parser(prog_name)
            parser.add_argument("--end")
            return parser

        def take_action(self, parsed_args):
            assert(parsed_args.end == '123')

    class MyCommandManager(commandmanager.CommandManager):
        def load_commands(self, namespace):
            self.add_command("mycommand", MyCommand)

    class MyApp(application.App):
        def __init__(self):
            super(MyApp, self).__init__(
                description='testing',
                version='0.1',
                command_manager=MyCommandManager(None),
            )

        def build_option_parser(self, description, version):
            parser = super(MyApp, self).build_option_parser(
                description,
                version,
                argparse_kwargs={'allow_abbrev': False})
            parser.add_argument('--endpoint')
            return parser

    app = MyApp()
    # NOTE(jd) --debug is necessary so assert in take_action() raises correctly
    # here
    app.run(['--debug', 'mycommand', '--end', '123'])


def _test_help(deferred_help):
    app, _ = make_app(deferred_help=deferred_help)
    with mock.patch.object(app, 'initialize_app') as init:
        with mock.patch('cliff.help.HelpAction.__call__',
                        side_effect=SystemExit(0)) as helper:
            try:
                app.run(['--help'])
            except SystemExit:
                pass
            else:
                raise Exception('Exception was not thrown')
            assert helper.called
        assert init.called == deferred_help


def test_help():
    _test_help(False)


def test_deferred_help():
    _test_help(True)


def test_subcommand_help():
    app, _ = make_app(deferred_help=False)

    # Help is called immediately
    with mock.patch('cliff.help.HelpAction.__call__') as helper:
        app.run(['show', 'files', '--help'])

    assert helper.called


def test_subcommand_deferred_help():
    app, _ = make_app(deferred_help=True)

    # Show that provide_help_if_requested() did not show help and exit
    with mock.patch.object(app, 'run_subcommand') as helper:
        app.run(['show', 'files', '--help'])

    helper.assert_called_once_with(['help', 'show', 'files'])


def test_unknown_cmd():
    app, command = make_app()
    assert app.run(['hell']) == 2


def test_unknown_cmd_debug():
    app, command = make_app()
    try:
        app.run(['--debug', 'hell']) == 2
    except ValueError as err:
        assert "['hell']" in ('%s' % err)


def test_list_matching_commands():
    stdout = StringIO()
    app = application.App('testing', '1',
                          test_utils.TestCommandManager(
                            test_utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    try:
        assert app.run(['t']) == 2
    except SystemExit:
        pass
    output = stdout.getvalue()
    assert "test: 't' is not a test command. See 'test --help'." in output
    assert 'Did you mean one of these?' in output
    assert 'three word command\n  two words\n' in output


def test_fuzzy_no_commands():
    cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
    app = application.App('test', '1.0', cmd_mgr)
    cmd_mgr.commands = {}
    matches = app.get_fuzzy_matches('foo')
    assert matches == []


def test_fuzzy_common_prefix():
    # searched string is a prefix of all commands
    cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
    app = application.App('test', '1.0', cmd_mgr)
    cmd_mgr.commands = {}
    cmd_mgr.add_command('user list', test_utils.TestCommand)
    cmd_mgr.add_command('user show', test_utils.TestCommand)
    matches = app.get_fuzzy_matches('user')
    assert matches == ['user list', 'user show']


def test_fuzzy_same_distance():
    # searched string has the same distance to all commands
    cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
    app = application.App('test', '1.0', cmd_mgr)
    cmd_mgr.add_command('user', test_utils.TestCommand)
    for cmd in cmd_mgr.commands.keys():
        assert utils.damerau_levenshtein('node', cmd, utils.COST) == 8
    matches = app.get_fuzzy_matches('node')
    assert matches == ['complete', 'help', 'user']


def test_fuzzy_no_prefix():
    # search by distance, no common prefix with any command
    cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
    app = application.App('test', '1.0', cmd_mgr)
    cmd_mgr.add_command('user', test_utils.TestCommand)
    matches = app.get_fuzzy_matches('uesr')
    assert matches == ['user']


def test_verbose():
    app, command = make_app()
    app.clean_up = mock.MagicMock(name='clean_up')
    app.run(['--verbose', 'mock'])
    app.clean_up.assert_called_once_with(command.return_value, 0, None)
    app.clean_up.reset_mock()
    app.run(['--quiet', 'mock'])
    app.clean_up.assert_called_once_with(command.return_value, 0, None)
    try:
        app.run(['--verbose', '--quiet', 'mock'])
    except SystemExit:
        pass
    else:
        raise Exception('Exception was not thrown')


def test_io_streams():
    cmd_mgr = commandmanager.CommandManager('cliff.tests')
    io = mock.Mock()

    if six.PY2:
        stdin_save = sys.stdin
        stdout_save = sys.stdout
        stderr_save = sys.stderr
        encoding = locale.getpreferredencoding() or 'utf-8'

        app = application.App('no io streams', 1, cmd_mgr)
        assert isinstance(app.stdin, codecs.StreamReader)
        assert isinstance(app.stdout, codecs.StreamWriter)
        assert isinstance(app.stderr, codecs.StreamWriter)

        app = application.App('with stdin io stream', 1, cmd_mgr, stdin=io)
        assert app.stdin is io
        assert isinstance(app.stdout, codecs.StreamWriter)
        assert isinstance(app.stderr, codecs.StreamWriter)

        app = application.App('with stdout io stream', 1, cmd_mgr, stdout=io)
        assert isinstance(app.stdin, codecs.StreamReader)
        assert app.stdout is io
        assert isinstance(app.stderr, codecs.StreamWriter)

        app = application.App('with stderr io stream', 1, cmd_mgr, stderr=io)
        assert isinstance(app.stdin, codecs.StreamReader)
        assert isinstance(app.stdout, codecs.StreamWriter)
        assert app.stderr is io

        try:
            sys.stdin = codecs.getreader(encoding)(sys.stdin)
            app = application.App(
                'with wrapped sys.stdin io stream', 1, cmd_mgr)
            assert app.stdin is sys.stdin
            assert isinstance(app.stdout, codecs.StreamWriter)
            assert isinstance(app.stderr, codecs.StreamWriter)
        finally:
            sys.stdin = stdin_save

        try:
            sys.stdout = codecs.getwriter(encoding)(sys.stdout)
            app = application.App('with wrapped stdout io stream', 1, cmd_mgr)
            assert isinstance(app.stdin, codecs.StreamReader)
            assert app.stdout is sys.stdout
            assert isinstance(app.stderr, codecs.StreamWriter)
        finally:
            sys.stdout = stdout_save

        try:
            sys.stderr = codecs.getwriter(encoding)(sys.stderr)
            app = application.App('with wrapped stderr io stream', 1, cmd_mgr)
            assert isinstance(app.stdin, codecs.StreamReader)
            assert isinstance(app.stdout, codecs.StreamWriter)
            assert app.stderr is sys.stderr
        finally:
            sys.stderr = stderr_save

    else:
        app = application.App('no io streams', 1, cmd_mgr)
        assert app.stdin is sys.stdin
        assert app.stdout is sys.stdout
        assert app.stderr is sys.stderr

        app = application.App('with stdin io stream', 1, cmd_mgr, stdin=io)
        assert app.stdin is io
        assert app.stdout is sys.stdout
        assert app.stderr is sys.stderr

        app = application.App('with stdout io stream', 1, cmd_mgr, stdout=io)
        assert app.stdin is sys.stdin
        assert app.stdout is io
        assert app.stderr is sys.stderr

        app = application.App('with stderr io stream', 1, cmd_mgr, stderr=io)
        assert app.stdin is sys.stdin
        assert app.stdout is sys.stdout
        assert app.stderr is io
