
from cliff.commandmanager import CommandManager


class TestCommand(object):
    @classmethod
    def load(cls):
        return cls

    def __init__(self):
        return


class TestCommandManager(CommandManager):
    def _load_commands(self):
        self.commands = {
            'one': TestCommand,
            'two words': TestCommand,
            'three word command': TestCommand,
            }


def test_lookup_and_find():
    def check(mgr, argv):
        cmd, name, remaining = mgr.find_command(argv)
        assert cmd
        assert name == ' '.join(argv)
        assert not remaining
    mgr = TestCommandManager('test')
    for expected in [['one'],
                     ['two', 'words'],
                     ['three', 'word', 'command'],
                     ]:
        yield check, mgr, expected
    return


def test_lookup_with_remainder():
    def check(mgr, argv):
        cmd, name, remaining = mgr.find_command(argv)
        assert cmd
        assert remaining == ['--opt']
    mgr = TestCommandManager('test')
    for expected in [['one', '--opt'],
                     ['two', 'words', '--opt'],
                     ['three', 'word', 'command', '--opt'],
                     ]:
        yield check, mgr, expected
    return
