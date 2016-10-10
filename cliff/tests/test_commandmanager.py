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

import mock

from cliff import commandmanager
from cliff.tests import utils


def test_lookup_and_find():
    def check(mgr, argv):
        cmd, name, remaining = mgr.find_command(argv)
        assert cmd
        assert name == ' '.join(argv)
        assert not remaining
    mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
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
    mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
    for expected in [['one', '--opt'],
                     ['two', 'words', '--opt'],
                     ['three', 'word', 'command', '--opt'],
                     ]:
        yield check, mgr, expected
    return


def test_find_invalid_command():
    mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)

    def check_one(argv):
        try:
            mgr.find_command(argv)
        except ValueError as err:
            # make sure err include 'a' when ['a', '-b']
            assert argv[0] in ('%s' % err)
            assert '-b' in ('%s' % err)
        else:
            assert False, 'expected a failure'
    for argv in [['a', '-b'],
                 ['-b'],
                 ]:
        yield check_one, argv


def test_find_unknown_command():
    mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
    try:
        mgr.find_command(['a', 'b'])
    except ValueError as err:
        assert "['a', 'b']" in ('%s' % err)
    else:
        assert False, 'expected a failure'


def test_add_command():
    mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
    mock_cmd = mock.Mock()
    mgr.add_command('mock', mock_cmd)
    found_cmd, name, args = mgr.find_command(['mock'])
    assert found_cmd is mock_cmd


def test_load_commands():
    testcmd = mock.Mock(name='testcmd')
    testcmd.name.replace.return_value = 'test'
    mock_pkg_resources = mock.Mock(return_value=[testcmd])
    with mock.patch('pkg_resources.iter_entry_points',
                    mock_pkg_resources) as iter_entry_points:
        mgr = commandmanager.CommandManager('test')
        iter_entry_points.assert_called_once_with('test')
        names = [n for n, v in mgr]
        assert names == ['test']


def test_load_commands_keep_underscores():
    testcmd = mock.Mock()
    testcmd.name = 'test_cmd'
    mock_pkg_resources = mock.Mock(return_value=[testcmd])
    with mock.patch('pkg_resources.iter_entry_points',
                    mock_pkg_resources) as iter_entry_points:
        mgr = commandmanager.CommandManager('test', convert_underscores=False)
        iter_entry_points.assert_called_once_with('test')
        names = [n for n, v in mgr]
        assert names == ['test_cmd']


def test_load_commands_replace_underscores():
    testcmd = mock.Mock()
    testcmd.name = 'test_cmd'
    mock_pkg_resources = mock.Mock(return_value=[testcmd])
    with mock.patch('pkg_resources.iter_entry_points',
                    mock_pkg_resources) as iter_entry_points:
        mgr = commandmanager.CommandManager('test', convert_underscores=True)
        iter_entry_points.assert_called_once_with('test')
        names = [n for n, v in mgr]
        assert names == ['test cmd']
