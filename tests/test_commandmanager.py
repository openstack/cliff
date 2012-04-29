
import mock

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


def test_find_invalid_command():
    mgr = TestCommandManager('test')
    def check_one(argv):
        try:
            mgr.find_command(argv)
        except ValueError as err:
            assert '-b' in ('%s' % err)
        else:
            assert False, 'expected a failure'
    for argv in [['a', '-b'],
                 ['-b'],
                 ]:
        yield check_one, argv


def test_find_unknown_command():
    mgr = TestCommandManager('test')
    try:
        mgr.find_command(['a', 'b'])
    except ValueError as err:
        assert "['a', 'b']" in ('%s' % err)
    else:
        assert False, 'expected a failure'


def test_add_command():
    mgr = TestCommandManager('test')
    mock_cmd = mock.Mock()
    mgr.add_command('mock', mock_cmd)
    found_cmd, name, args = mgr.find_command(['mock'])
    assert found_cmd is mock_cmd


def test_load_commands():
    testcmd = mock.Mock(name='testcmd')
    testcmd.name.replace.return_value = 'test'
    mock_pkg_resources = mock.Mock(return_value=[testcmd])
    with mock.patch('pkg_resources.iter_entry_points', mock_pkg_resources) as iter_entry_points:
        mgr = CommandManager('test')
        assert iter_entry_points.called_once_with('test')
        names = [n for n, v in mgr]
        assert names == ['test']
