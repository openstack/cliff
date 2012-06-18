try:
    from StringIO import StringIO
except:
    from io import StringIO

import mock

from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager
from cliff.help import HelpCommand


class TestParser(object):

    def print_help(self, stdout):
        stdout.write('TestParser')


class TestCommand(Command):

    @classmethod
    def load(cls):
        return cls

    def get_parser(self, ignore):
        # Make it look like this class is the parser
        # so parse_args() is called.
        return TestParser()

    def take_action(self, args):
        return


class TestCommandManager(CommandManager):
    def _load_commands(self):
        self.commands = {
            'one': TestCommand,
            'two words': TestCommand,
            'three word command': TestCommand,
            }


def test_show_help_for_command():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = App('testing', '1', TestCommandManager('cliff.test'), stdout=stdout)
    app.NAME = 'test'
    help_cmd = HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args(['one'])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    assert stdout.getvalue() == 'TestParser'


def test_list_matching_commands():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = App('testing', '1', TestCommandManager('cliff.test'), stdout=stdout)
    app.NAME = 'test'
    help_cmd = HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args(['t'])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    help_output = stdout.getvalue()
    assert 'Command "t" matches:' in help_output
    assert 'two' in help_output
    assert 'three' in help_output


def test_list_matching_commands_no_match():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = App('testing', '1', TestCommandManager('cliff.test'), stdout=stdout)
    app.NAME = 'test'
    help_cmd = HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args(['z'])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    except ValueError:
        pass
    else:
        assert False, 'Should have seen a ValueError'


def test_show_help_for_help():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = App('testing', '1', TestCommandManager('cliff.test'), stdout=stdout)
    app.NAME = 'test'
    help_cmd = HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args([])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    help_text = stdout.getvalue()
    assert 'usage: test help [-h]' in help_text
