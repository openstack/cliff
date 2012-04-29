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


def test_initialize_app():
    app, command = make_app()
    app.initialize_app = mock.MagicMock(name='initialize_app')
    app.run(['mock'])
    app.initialize_app.assert_called_once_with()


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

    # Register a command that fails
    err_command = mock.Mock(name='err_command', spec=Command)
    err_command_inst = mock.Mock(spec=Command)
    def raise_exception(*args):
        #raise RuntimeError('test exception %s' % args[0])
        raise RuntimeError('test exception')
    err_command_inst.run = mock.Mock(side_effect=raise_exception)
    err_command.return_value = err_command_inst
    app.command_manager.add_command('error', err_command)

    app.clean_up = mock.MagicMock(name='clean_up')
    app.run(['error'])

    app.clean_up.assert_called_once()
    call_args = app.clean_up.call_args_list[0]
    assert call_args == mock.call(mock.ANY, 1, mock.ANY)
    args, kwargs = call_args
    assert isinstance(args[2], RuntimeError)
    assert args[2].args == ('test exception',)
