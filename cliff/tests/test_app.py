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
import codecs
import io
from unittest import mock

from cliff import app as application
from cliff import command as c_cmd
from cliff import commandmanager
from cliff.tests import base
from cliff.tests import utils as test_utils
from cliff import utils
import sys


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

    # Register a command that is interrrupted
    interrupt_command = mock.Mock(name='interrupt_command', spec=c_cmd.Command)
    interrupt_command_inst = mock.Mock(spec=c_cmd.Command)
    interrupt_command_inst.run = mock.Mock(side_effect=KeyboardInterrupt)
    interrupt_command.return_value = interrupt_command_inst
    cmd_mgr.add_command('interrupt', interrupt_command)

    # Register a command that is interrrupted by a broken pipe
    pipeclose_command = mock.Mock(name='pipeclose_command', spec=c_cmd.Command)
    pipeclose_command_inst = mock.Mock(spec=c_cmd.Command)
    pipeclose_command_inst.run = mock.Mock(side_effect=BrokenPipeError)
    pipeclose_command.return_value = pipeclose_command_inst
    cmd_mgr.add_command('pipe-close', pipeclose_command)

    app = application.App(
        'testing interactive mode',
        '1',
        cmd_mgr,
        stderr=mock.Mock(),  # suppress warning messages
        **kwargs,
    )
    return app, command


class TestInteractiveMode(base.TestBase):
    def test_no_args_triggers_interactive_mode(self):
        app, command = make_app()
        app.interact = mock.MagicMock(name='inspect')
        app.run([])
        app.interact.assert_called_once_with()

    def test_interactive_mode_cmdloop(self):
        app, command = make_app()
        app.interactive_app_factory = mock.MagicMock(
            name='interactive_app_factory'
        )
        self.assertIsNone(app.interpreter)
        ret = app.run([])
        self.assertIsNotNone(app.interpreter)
        cmdloop = app.interactive_app_factory.return_value.cmdloop
        cmdloop.assert_called_once_with()
        self.assertNotEqual(ret, 0)

    def test_interactive_mode_cmdloop_error(self):
        app, command = make_app()
        cmdloop_mock = mock.MagicMock(
            name='cmdloop',
        )
        cmdloop_mock.return_value = 1
        app.interactive_app_factory = mock.MagicMock(
            name='interactive_app_factory'
        )
        self.assertIsNone(app.interpreter)
        ret = app.run([])
        self.assertIsNotNone(app.interpreter)
        cmdloop = app.interactive_app_factory.return_value.cmdloop
        cmdloop.assert_called_once_with()
        self.assertNotEqual(ret, 0)


class TestInitAndCleanup(base.TestBase):
    def test_initialize_app(self):
        app, command = make_app()
        app.initialize_app = mock.MagicMock(name='initialize_app')
        app.run(['mock'])
        app.initialize_app.assert_called_once_with(['mock'])

    def test_prepare_to_run_command(self):
        app, command = make_app()
        app.prepare_to_run_command = mock.MagicMock(
            name='prepare_to_run_command',
        )
        app.run(['mock'])
        app.prepare_to_run_command.assert_called_once_with(command())

    def test_interrupt_command(self):
        app, command = make_app()
        result = app.run(['interrupt'])
        self.assertEqual(result, 130)

    def test_pipeclose_command(self):
        app, command = make_app()
        result = app.run(['pipe-close'])
        self.assertEqual(result, 141)

    def test_clean_up_success(self):
        app, command = make_app()
        app.clean_up = mock.MagicMock(name='clean_up')
        ret = app.run(['mock'])
        app.clean_up.assert_called_once_with(command.return_value, 0, None)
        self.assertEqual(ret, 0)

    def test_clean_up_error(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(name='clean_up')
        ret = app.run(['error'])
        self.assertNotEqual(ret, 0)

        app.clean_up.assert_called_once_with(mock.ANY, mock.ANY, mock.ANY)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 1, mock.ANY), call_args)
        args, kwargs = call_args
        self.assertIsInstance(args[2], RuntimeError)
        self.assertEqual(('test exception',), args[2].args)

    def test_clean_up_error_debug(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(name='clean_up')
        ret = app.run(['--debug', 'error'])
        self.assertNotEqual(ret, 0)

        self.assertTrue(app.clean_up.called)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 1, mock.ANY), call_args)
        args, kwargs = call_args
        self.assertIsInstance(args[2], RuntimeError)
        self.assertEqual(('test exception',), args[2].args)

    def test_clean_up_interrupt(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(name='clean_up')
        ret = app.run(['interrupt'])
        self.assertNotEqual(ret, 0)

        app.clean_up.assert_called_once_with(mock.ANY, mock.ANY, mock.ANY)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 130, mock.ANY), call_args)
        args, kwargs = call_args
        self.assertIsInstance(args[2], KeyboardInterrupt)

    def test_clean_up_pipeclose(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(name='clean_up')
        ret = app.run(['pipe-close'])
        self.assertNotEqual(ret, 0)

        app.clean_up.assert_called_once_with(mock.ANY, mock.ANY, mock.ANY)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 141, mock.ANY), call_args)
        args, kwargs = call_args
        self.assertIsInstance(args[2], BrokenPipeError)

    def test_error_handling_clean_up_raises_exception(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(
            name='clean_up',
            side_effect=RuntimeError('within clean_up'),
        )
        app.run(['error'])

        self.assertTrue(app.clean_up.called)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 1, mock.ANY), call_args)
        args, kwargs = call_args
        self.assertIsInstance(args[2], RuntimeError)
        self.assertEqual(('test exception',), args[2].args)

    def test_error_handling_clean_up_raises_exception_debug(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(
            name='clean_up',
            side_effect=RuntimeError('within clean_up'),
        )
        try:
            ret = app.run(['--debug', 'error'])
        except RuntimeError as err:
            if not hasattr(err, '__context__'):
                # The exception passed to clean_up is not the exception
                # caused *by* clean_up.  This test is only valid in python
                # 2 because under v3 the original exception is re-raised
                # with the new one as a __context__ attribute.
                self.assertIsNot(err, app.clean_up.call_args_list[0][0][2])
        else:
            self.assertNotEqual(ret, 0)

        self.assertTrue(app.clean_up.called)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 1, mock.ANY), call_args)
        args, kwargs = call_args
        self.assertIsInstance(args[2], RuntimeError)
        self.assertEqual(('test exception',), args[2].args)

    def test_normal_clean_up_raises_exception(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(
            name='clean_up',
            side_effect=RuntimeError('within clean_up'),
        )
        app.run(['mock'])

        self.assertTrue(app.clean_up.called)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 0, None), call_args)

    def test_normal_clean_up_raises_exception_debug(self):
        app, command = make_app()

        app.clean_up = mock.MagicMock(
            name='clean_up',
            side_effect=RuntimeError('within clean_up'),
        )
        app.run(['--debug', 'mock'])

        self.assertTrue(app.clean_up.called)
        call_args = app.clean_up.call_args_list[0]
        self.assertEqual(mock.call(mock.ANY, 0, None), call_args)


class TestOptionParser(base.TestBase):
    def test_conflicting_option_should_throw(self):
        class MyApp(application.App):
            def __init__(self):
                super().__init__(
                    description='testing',
                    version='0.1',
                    command_manager=commandmanager.CommandManager('tests'),
                )

            def build_option_parser(self, description, version):
                parser = super().build_option_parser(description, version)
                parser.add_argument(
                    '-h',
                    '--help',
                    default=self,  # tricky
                    help="Show help message and exit.",
                )

        self.assertRaises(
            argparse.ArgumentError,
            MyApp,
        )

    def test_conflicting_option_custom_arguments_should_not_throw(self):
        class MyApp(application.App):
            def __init__(self):
                super().__init__(
                    description='testing',
                    version='0.1',
                    command_manager=commandmanager.CommandManager('tests'),
                )

            def build_option_parser(self, description, version):
                argparse_kwargs = {'conflict_handler': 'resolve'}
                parser = super().build_option_parser(
                    description, version, argparse_kwargs=argparse_kwargs
                )
                parser.add_argument(
                    '-h',
                    '--help',
                    default=self,  # tricky
                    help="Show help message and exit.",
                )

        MyApp()

    def test_option_parser_abbrev_issue(self):
        class MyCommand(c_cmd.Command):
            def get_parser(self, prog_name):
                parser = super().get_parser(prog_name)
                parser.add_argument("--end")
                return parser

            def take_action(self, parsed_args):
                assert parsed_args.end == '123'

        class MyCommandManager(commandmanager.CommandManager):
            def load_commands(self, namespace):
                self.add_command("mycommand", MyCommand)

        class MyApp(application.App):
            def __init__(self):
                super().__init__(
                    description='testing',
                    version='0.1',
                    command_manager=MyCommandManager(None),
                )

            def build_option_parser(self, description, version):
                parser = super().build_option_parser(
                    description,
                    version,
                    argparse_kwargs={'allow_abbrev': False},
                )
                parser.add_argument('--endpoint')
                return parser

        app = MyApp()
        # NOTE(jd) --debug is necessary so assert in take_action()
        # raises correctly here
        app.run(['--debug', 'mycommand', '--end', '123'])


class TestHelpHandling(base.TestBase):
    def _test_help(self, deferred_help):
        app, _ = make_app(deferred_help=deferred_help)
        with mock.patch.object(app, 'initialize_app') as init:
            with mock.patch(
                'cliff.help.HelpAction.__call__', side_effect=SystemExit(0)
            ) as helper:
                self.assertRaises(
                    SystemExit,
                    app.run,
                    ['--help'],
                )
                self.assertTrue(helper.called)
            self.assertEqual(deferred_help, init.called)

    def test_help(self):
        self._test_help(False)

    def test_deferred_help(self):
        self._test_help(True)

    def _test_interrupted_help(self, deferred_help):
        app, _ = make_app(deferred_help=deferred_help)
        with mock.patch(
            'cliff.help.HelpAction.__call__', side_effect=KeyboardInterrupt
        ):
            result = app.run(['--help'])
            self.assertEqual(result, 130)

    def test_interrupted_help(self):
        self._test_interrupted_help(False)

    def test_interrupted_deferred_help(self):
        self._test_interrupted_help(True)

    def _test_pipeclose_help(self, deferred_help):
        app, _ = make_app(deferred_help=deferred_help)
        with mock.patch(
            'cliff.help.HelpAction.__call__', side_effect=BrokenPipeError
        ):
            app.run(['--help'])

    def test_pipeclose_help(self):
        self._test_pipeclose_help(False)

    def test_pipeclose_deferred_help(self):
        self._test_pipeclose_help(True)

    def test_subcommand_help(self):
        app, _ = make_app(deferred_help=False)

        # Help is called immediately
        with mock.patch('cliff.help.HelpAction.__call__') as helper:
            app.run(['show', 'files', '--help'])

        self.assertTrue(helper.called)

    def test_subcommand_deferred_help(self):
        app, _ = make_app(deferred_help=True)

        # Show that provide_help_if_requested() did not show help and exit
        with mock.patch.object(app, 'run_subcommand') as helper:
            app.run(['show', 'files', '--help'])

        helper.assert_called_once_with(['help', 'show', 'files'])


class TestCommandLookup(base.TestBase):
    def test_unknown_cmd(self):
        app, command = make_app()
        self.assertEqual(2, app.run(['hell']))

    def test_unknown_cmd_debug(self):
        app, command = make_app()
        try:
            self.assertEqual(2, app.run(['--debug', 'hell']))
        except ValueError as err:
            self.assertIn("['hell']", str(err))

    def test_list_matching_commands(self):
        stdout = io.StringIO()
        app = application.App(
            'testing',
            '1',
            test_utils.TestCommandManager(test_utils.TEST_NAMESPACE),
            stdout=stdout,
        )
        app.NAME = 'test'
        try:
            self.assertEqual(2, app.run(['t']))
        except SystemExit:
            pass
        output = stdout.getvalue()
        self.assertIn(
            "test: 't' is not a test command. See 'test --help'.", output
        )
        self.assertIn('Did you mean one of these?', output)
        self.assertIn('three word command\n  two words\n', output)

    def test_fuzzy_no_commands(self):
        cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
        app = application.App('test', '1.0', cmd_mgr)
        cmd_mgr.commands = {}
        matches = app.get_fuzzy_matches('foo')
        self.assertEqual([], matches)

    def test_fuzzy_common_prefix(self):
        # searched string is a prefix of all commands
        cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
        app = application.App('test', '1.0', cmd_mgr)
        cmd_mgr.commands = {}
        cmd_mgr.add_command('user list', test_utils.TestCommand)
        cmd_mgr.add_command('user show', test_utils.TestCommand)
        matches = app.get_fuzzy_matches('user')
        self.assertEqual(['user list', 'user show'], matches)

    def test_fuzzy_same_distance(self):
        # searched string has the same distance to all commands
        cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
        app = application.App('test', '1.0', cmd_mgr)
        cmd_mgr.add_command('user', test_utils.TestCommand)
        for cmd in cmd_mgr.commands.keys():
            self.assertEqual(
                8,
                utils.damerau_levenshtein('node', cmd, utils.COST),
            )
        matches = app.get_fuzzy_matches('node')
        self.assertEqual(['complete', 'help', 'user'], matches)

    def test_fuzzy_no_prefix(self):
        # search by distance, no common prefix with any command
        cmd_mgr = commandmanager.CommandManager('cliff.fuzzy')
        app = application.App('test', '1.0', cmd_mgr)
        cmd_mgr.add_command('user', test_utils.TestCommand)
        matches = app.get_fuzzy_matches('uesr')
        self.assertEqual(['user'], matches)


class TestVerboseMode(base.TestBase):
    def test_verbose(self):
        app, command = make_app()
        app.clean_up = mock.MagicMock(name='clean_up')
        app.run(['--verbose', 'mock'])
        app.clean_up.assert_called_once_with(command.return_value, 0, None)
        app.clean_up.reset_mock()
        app.run(['--quiet', 'mock'])
        app.clean_up.assert_called_once_with(command.return_value, 0, None)
        self.assertRaises(
            SystemExit,
            app.run,
            ['--verbose', '--quiet', 'mock'],
        )


class TestIO(base.TestBase):
    def test_io_streams(self):
        cmd_mgr = commandmanager.CommandManager('cliff.tests')
        io = mock.Mock()

        app = application.App('no io streams', 1, cmd_mgr)
        self.assertIs(sys.stdin, app.stdin)
        self.assertIs(sys.stdout, app.stdout)
        self.assertIs(sys.stderr, app.stderr)

        app = application.App('with stdin io stream', 1, cmd_mgr, stdin=io)
        self.assertIs(io, app.stdin)
        self.assertIs(sys.stdout, app.stdout)
        self.assertIs(sys.stderr, app.stderr)

        app = application.App('with stdout io stream', 1, cmd_mgr, stdout=io)
        self.assertIs(sys.stdin, app.stdin)
        self.assertIs(io, app.stdout)
        self.assertIs(sys.stderr, app.stderr)

        app = application.App('with stderr io stream', 1, cmd_mgr, stderr=io)
        self.assertIs(sys.stdin, app.stdin)
        self.assertIs(sys.stdout, app.stdout)
        self.assertIs(io, app.stderr)

    def test_writer_encoding(self):
        # The word "test" with the e replaced by
        # Unicode latin small letter e with acute,
        # U+00E9, utf-8 encoded as 0xC3 0xA9
        text = 't\u00e9st'
        text_utf8 = text.encode('utf-8')

        # In PY3 you can't write encoded bytes to a text writer
        # instead text functions require text.
        out = io.StringIO()
        writer = codecs.getwriter('utf-8')(out)
        self.assertRaises(TypeError, writer.write, text)

        out = io.StringIO()
        writer = codecs.getwriter('utf-8')(out)
        self.assertRaises(TypeError, writer.write, text_utf8)
