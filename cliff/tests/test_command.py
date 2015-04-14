
from cliff.command import Command


class TestCommand(Command):
    """Description of command.
    """

    def take_action(self, parsed_args):
        return


def test_get_description():
    cmd = TestCommand(None, None)
    desc = cmd.get_description()
    assert desc == "Description of command.\n    "


def test_get_parser():
    cmd = TestCommand(None, None)
    parser = cmd.get_parser('NAME')
    assert parser.prog == 'NAME'


def test_get_name():
    cmd = TestCommand(None, None, cmd_name='object action')
    assert cmd.cmd_name == 'object action'
