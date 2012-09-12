from argparse import ArgumentError

from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager

import mock


def make_app():
    cmd_mgr = CommandManager('cliff.tests')

    # Register a command that succeeds
    command = mock.MagicMock(spec=Command)
    command_inst = mock.MagicMock(spec=Command)
    command_inst.run.return_value = 0
    command.return_value = command_inst
    cmd_mgr.add_command('mock', command)

    # Register a command that fails
    err_command = mock.Mock(name='err_command', spec=Command)
    err_command_inst = mock.Mock(spec=Command)
    err_command_inst.run = mock.Mock(side_effect=RuntimeError('test exception'))
    err_command.return_value = err_command_inst
    cmd_mgr.add_command('error', err_command)

    app = App('testing interactive mode',
              '1',
              cmd_mgr,
              stderr=mock.Mock(),  # suppress warning messages
              )
    return app, command


def test_no_args_triggers_interactive_mode():
    app, command = make_app()
    app.interact = mock.MagicMock(name='inspect')
    app.run([])
    app.interact.assert_called_once_with()


def test_interactive_mode_cmdloop():
    app, command = make_app()
    app.interactive_app_factory = mock.MagicMock(name='interactive_app_factory')
    app.run([])
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

    app.clean_up.assert_called_once()
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

    app.clean_up.assert_called_once()
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

    app.clean_up.assert_called_once()
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

    app.clean_up.assert_called_once()
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

    app.clean_up.assert_called_once()
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 0, None)


def test_normal_clean_up_raises_exception_debug():
    app, command = make_app()

    app.clean_up = mock.MagicMock(
        name='clean_up',
        side_effect=RuntimeError('within clean_up'),
        )
    app.run(['--debug', 'mock'])

    app.clean_up.assert_called_once()
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 0, None)

def test_build_option_parser_conflicting_option_should_throw():
    class MyApp(App):
        def __init__(self):
            super(MyApp, self).__init__(
                description='testing',
                version='0.1',
                command_manager=CommandManager('tests'),
            )

        def build_option_parser(self, description, version):
            parser = super(MyApp, self).build_option_parser(description,
                                                             version)
            parser.add_argument(
                '-h', '--help',
                default=self,  # tricky
                help="show this help message and exit",
                )

    # TODO: tests should really use unittest2.
    try:
        MyApp()
    except ArgumentError:
        pass
    else:
        raise Exception('Exception was not thrown')

def test_build_option_parser_conflicting_option_custom_arguments_should_not_throw():
    class MyApp(App):
        def __init__(self):
            super(MyApp, self).__init__(
                description='testing',
                version='0.1',
                command_manager=CommandManager('tests'),
            )

        def build_option_parser(self, description, version):
            argparse_kwargs = {'conflict_handler': 'resolve'}
            parser = super(MyApp, self).build_option_parser(description,
                                                            version,
                                           argparse_kwargs=argparse_kwargs)
            parser.add_argument(
                '-h', '--help',
                default=self,  # tricky
                help="show this help message and exit",
                )

    MyApp()
