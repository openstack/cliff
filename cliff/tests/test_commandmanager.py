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

import testscenarios
from unittest import mock

from cliff import command
from cliff import commandmanager
from cliff.tests import base
from cliff.tests import utils


load_tests = testscenarios.load_tests_apply_scenarios


class TestLookupAndFind(base.TestBase):
    scenarios = [
        ('one-word', {'argv': ['one']}),
        ('two-words', {'argv': ['two', 'words']}),
        ('three-words', {'argv': ['three', 'word', 'command']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        cmd, name, remaining = mgr.find_command(self.argv)
        self.assertTrue(cmd)
        self.assertEqual(' '.join(self.argv), name)
        self.assertFalse(remaining)


class TestLookupWithRemainder(base.TestBase):
    scenarios = [
        ('one', {'argv': ['one', '--opt']}),
        ('two', {'argv': ['two', 'words', '--opt']}),
        ('three', {'argv': ['three', 'word', 'command', '--opt']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        cmd, name, remaining = mgr.find_command(self.argv)
        self.assertTrue(cmd)
        self.assertEqual(['--opt'], remaining)


class TestFindInvalidCommand(base.TestBase):
    scenarios = [
        ('no-such-command', {'argv': ['a', '-b']}),
        ('no-command-given', {'argv': ['-b']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        try:
            mgr.find_command(self.argv)
        except ValueError as err:
            # make sure err include 'a' when ['a', '-b']
            self.assertIn(self.argv[0], str(err))
            self.assertIn('-b', str(err))
        else:
            self.fail('expected a failure')


class TestFindUnknownCommand(base.TestBase):
    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        try:
            mgr.find_command(['a', 'b'])
        except ValueError as err:
            self.assertIn("['a', 'b']", str(err))
        else:
            self.fail('expected a failure')


class FooCommand(command.Command):
    """Description of foo command."""

    def take_action(self, parsed_args):
        return 'foo'


class FooBarCommand(command.Command):
    """Description of foobar command."""

    def take_action(self, parsed_args):
        return 'foobar'


class TestDynamicCommands(base.TestBase):
    def test_add(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mock_cmd = mock.Mock()
        mgr.add_command('mock', mock_cmd)
        found_cmd, name, args = mgr.find_command(['mock'])
        self.assertIs(mock_cmd, found_cmd)

    def test_intersected_commands(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mgr.add_command('foo', FooCommand)
        mgr.add_command('foo bar', FooBarCommand)

        self.assertIs(FooBarCommand, mgr.find_command(['foo', 'bar'])[0])
        self.assertIs(FooCommand, mgr.find_command(['foo', 'arg0'])[0])


class TestLoad(base.TestBase):
    def test_load_commands(self):
        testcmd = mock.Mock(name='testcmd')
        testcmd.name.replace.return_value = 'test'
        mock_get_group_all = mock.Mock(return_value=[testcmd])
        with mock.patch(
            'stevedore.ExtensionManager', mock_get_group_all
        ) as mock_manager:
            mgr = commandmanager.CommandManager('test')
            mock_manager.assert_called_once_with('test')
            names = [n for n, v in mgr]
            self.assertEqual(['test'], names)

    def test_load_commands_keep_underscores(self):
        testcmd = mock.Mock()
        testcmd.name = 'test_cmd'
        mock_get_group_all = mock.Mock(return_value=[testcmd])
        with mock.patch(
            'stevedore.ExtensionManager', mock_get_group_all
        ) as mock_manager:
            mgr = commandmanager.CommandManager(
                'test',
                convert_underscores=False,
            )
            mock_manager.assert_called_once_with('test')
            names = [n for n, v in mgr]
            self.assertEqual(['test_cmd'], names)

    def test_load_commands_replace_underscores(self):
        testcmd = mock.Mock()
        testcmd.name = 'test_cmd'
        mock_get_group_all = mock.Mock(return_value=[testcmd])
        with mock.patch(
            'stevedore.ExtensionManager', mock_get_group_all
        ) as mock_manager:
            mgr = commandmanager.CommandManager(
                'test',
                convert_underscores=True,
            )
            mock_manager.assert_called_once_with('test')
            names = [n for n, v in mgr]
            self.assertEqual(['test cmd'], names)


class FauxCommand(command.Command):
    def take_action(self, parsed_args):
        return 0


class FauxCommand2(FauxCommand):
    pass


class TestLegacyCommand(base.TestBase):
    def test_find_legacy(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mgr.add_command('new name', FauxCommand)
        mgr.add_legacy_command('old name', 'new name')
        cmd, name, remaining = mgr.find_command(['old', 'name'])
        self.assertIs(cmd, FauxCommand)
        self.assertEqual(name, 'old name')

    def test_legacy_overrides_new(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mgr.add_command('cmd1', FauxCommand)
        mgr.add_command('cmd2', FauxCommand2)
        mgr.add_legacy_command('cmd2', 'cmd1')
        cmd, name, remaining = mgr.find_command(['cmd2'])
        self.assertIs(cmd, FauxCommand)
        self.assertEqual(name, 'cmd2')

    def test_no_legacy(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mgr.add_command('cmd1', FauxCommand)
        self.assertRaises(
            ValueError,
            mgr.find_command,
            ['cmd2'],
        )

    def test_no_command(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        mgr.add_legacy_command('cmd2', 'cmd1')
        self.assertRaises(
            ValueError,
            mgr.find_command,
            ['cmd2'],
        )


class TestLookupAndFindPartialName(base.TestBase):
    scenarios = [
        ('one-word', {'argv': ['o']}),
        ('two-words', {'argv': ['t', 'w']}),
        ('three-words', {'argv': ['t', 'w', 'c']}),
    ]

    def test(self):
        mgr = utils.TestCommandManager(utils.TEST_NAMESPACE)
        cmd, name, remaining = mgr.find_command(self.argv)
        self.assertTrue(cmd)
        self.assertEqual(' '.join(self.argv), name)
        self.assertFalse(remaining)


class TestGetByPartialName(base.TestBase):
    def setUp(self):
        super().setUp()
        self.commands = {
            'resource provider list': 1,
            'resource class list': 2,
            'server list': 3,
            'service list': 4,
        }

    def test_no_candidates(self):
        self.assertEqual(
            [],
            commandmanager._get_commands_by_partial_name(
                ['r', 'p'], list(self.commands)
            ),
        )
        self.assertEqual(
            [],
            commandmanager._get_commands_by_partial_name(
                ['r', 'p', 'c'], list(self.commands)
            ),
        )

    def test_multiple_candidates(self):
        self.assertEqual(
            2,
            len(
                commandmanager._get_commands_by_partial_name(
                    ['se', 'li'], list(self.commands)
                )
            ),
        )

    def test_one_candidate(self):
        self.assertEqual(
            ['resource provider list'],
            commandmanager._get_commands_by_partial_name(
                ['r', 'p', 'l'], list(self.commands)
            ),
        )
        self.assertEqual(
            ['resource provider list'],
            commandmanager._get_commands_by_partial_name(
                ['resource', 'provider', 'list'], list(self.commands)
            ),
        )
        self.assertEqual(
            ['server list'],
            commandmanager._get_commands_by_partial_name(
                ['serve', 'l'], list(self.commands)
            ),
        )


FAKE_CMD_ONE = commandmanager.EntryPointWrapper('one', utils.TestCommand)
FAKE_CMD_TWO = commandmanager.EntryPointWrapper('two', utils.TestCommand)
FAKE_CMD_ALPHA = commandmanager.EntryPointWrapper('alpha', utils.TestCommand)
FAKE_CMD_BETA = commandmanager.EntryPointWrapper('beta', utils.TestCommand)


class FakeCommandManager(commandmanager.CommandManager):
    commands = {}

    def load_commands(self, namespace):
        if namespace == 'test':
            self.commands['one'] = FAKE_CMD_ONE
            self.commands['two'] = FAKE_CMD_TWO
            self.group_list.append(namespace)
        elif namespace == 'greek':
            self.commands['alpha'] = FAKE_CMD_ALPHA
            self.commands['beta'] = FAKE_CMD_BETA
            self.group_list.append(namespace)


class TestCommandManagerGroups(base.TestBase):
    def test_add_command_group(self):
        mgr = FakeCommandManager('test')

        # Make sure add_command() still functions
        mock_cmd_one = mock.Mock()
        mgr.add_command('mock', mock_cmd_one)
        cmd_mock, name, args = mgr.find_command(['mock'])
        self.assertEqual(mock_cmd_one, cmd_mock)

        # Find a command added in initialization
        cmd_one, name, args = mgr.find_command(['one'])
        self.assertEqual(FAKE_CMD_ONE.load(), cmd_one)

        # Load another command group
        mgr.add_command_group('greek')

        # Find a new command
        cmd_alpha, name, args = mgr.find_command(['alpha'])
        self.assertEqual(FAKE_CMD_ALPHA.load(), cmd_alpha)

        # Ensure that the original commands were not overwritten
        cmd_two, name, args = mgr.find_command(['two'])
        self.assertEqual(FAKE_CMD_TWO.load(), cmd_two)

    def test_get_command_groups(self):
        mgr = FakeCommandManager('test')

        # Make sure add_command() still functions
        mock_cmd_one = mock.Mock()
        mgr.add_command('mock', mock_cmd_one)
        cmd_mock, name, args = mgr.find_command(['mock'])
        self.assertEqual(mock_cmd_one, cmd_mock)

        # Load another command group
        mgr.add_command_group('greek')

        gl = mgr.get_command_groups()
        self.assertEqual(['test', 'greek'], gl)

    def test_get_command_names(self):
        mock_cmd_one = mock.Mock()
        mock_cmd_one.name = 'one'
        mock_cmd_two = mock.Mock()
        mock_cmd_two.name = 'cmd two'
        mock_get_group_all = mock.Mock(
            return_value=[mock_cmd_one, mock_cmd_two],
        )
        with mock.patch(
            'stevedore.ExtensionManager',
            mock_get_group_all,
        ) as mock_manager:
            mgr = commandmanager.CommandManager('test')
            mock_manager.assert_called_once_with('test')
            cmds = mgr.get_command_names('test')
            self.assertEqual(['one', 'cmd two'], cmds)
