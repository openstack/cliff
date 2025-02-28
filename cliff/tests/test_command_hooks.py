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

from cliff import app as application
from cliff import command
from cliff import commandmanager
from cliff import hooks
from cliff import lister
from cliff import show
from cliff.tests import base

from stevedore import extension
from unittest import mock


def make_app(**kwargs):
    cmd_mgr = commandmanager.CommandManager('cliff.tests')

    # Register a command that succeeds
    cmd = mock.MagicMock(spec=command.Command)
    command_inst = mock.MagicMock(spec=command.Command)
    command_inst.run.return_value = 0
    cmd.return_value = command_inst
    cmd_mgr.add_command('mock', cmd)

    # Register a command that fails
    err_command = mock.Mock(name='err_command', spec=command.Command)
    err_command_inst = mock.Mock(spec=command.Command)
    err_command_inst.run = mock.Mock(
        side_effect=RuntimeError('test exception')
    )
    err_command.return_value = err_command_inst
    cmd_mgr.add_command('error', err_command)

    app = application.App(
        'testing command hooks',
        '1',
        cmd_mgr,
        stderr=mock.Mock(),  # suppress warning messages
        **kwargs,
    )
    return app


class TestCommand(command.Command):
    """Description of command."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        return 42


class TestShowCommand(show.ShowOne):
    """Description of command."""

    def take_action(self, parsed_args):
        return (('Name',), ('value',))


class TestListerCommand(lister.Lister):
    """Description of command."""

    def take_action(self, parsed_args):
        return (('Name',), [('value',)])


class TestHook(hooks.CommandHook):
    """A hook that returns an epilog and a new argument."""

    _before_called = False
    _after_called = False

    def get_parser(self, parser):
        parser.add_argument('--added-by-hook')
        return parser

    def get_epilog(self):
        return 'hook epilog'

    def before(self, parsed_args):
        self._before_called = True

    def after(self, parsed_args, return_code):
        self._after_called = True


class TestNullHook(hooks.CommandHook):
    """A hook that does not return an epilog nor any new arguments."""

    _before_called = False
    _after_called = False

    def get_parser(self, parser):
        return None

    def get_epilog(self):
        return None

    def before(self, parsed_args):
        self._before_called = True

    def after(self, parsed_args, return_code):
        self._after_called = True


class TestChangeHook(hooks.CommandHook):
    """A hook that modifies the parsed arguments and the return code.

    This would be used with subclasses of the Command base command class.
    """

    _before_called = False
    _after_called = False

    def get_parser(self, parser):
        parser.add_argument('--added-by-hook')
        return parser

    def get_epilog(self):
        return 'hook epilog'

    def before(self, parsed_args):
        self._before_called = True
        parsed_args.added_by_hook = 'othervalue'
        parsed_args.added_by_before = True
        return parsed_args

    def after(self, parsed_args, return_code):
        self._after_called = True
        return 24


class TestDisplayChangeHook(hooks.CommandHook):
    """A hook that modifies the parsed arguments and the output.

    This would be used with subclasses of :class:`cliff.show.ShowOne`.
    """

    _before_called = False
    _after_called = False

    def get_parser(self, parser):
        parser.add_argument('--added-by-hook')
        return parser

    def get_epilog(self):
        return 'hook epilog'

    def before(self, parsed_args):
        self._before_called = True
        parsed_args.added_by_hook = 'othervalue'
        parsed_args.added_by_before = True
        return parsed_args

    def after(self, parsed_args, return_code):
        self._after_called = True
        return (('Name',), ('othervalue',))


class TestListerChangeHook(hooks.CommandHook):
    """A hook that modifies the parsed arguments and the output.

    This would be used with subclasses of :class:`cliff.show.Lister`.
    """

    _before_called = False
    _after_called = False

    def get_parser(self, parser):
        parser.add_argument('--added-by-hook')
        return parser

    def get_epilog(self):
        return 'hook epilog'

    def before(self, parsed_args):
        self._before_called = True
        parsed_args.added_by_hook = 'othervalue'
        parsed_args.added_by_before = True
        return parsed_args

    def after(self, parsed_args, return_code):
        self._after_called = True
        return (('Name',), [('othervalue',)])


class TestCommandLoadHooks(base.TestBase):
    def test_no_name(self):
        app = make_app()
        cmd = TestCommand(app, None)
        self.assertEqual([], cmd._hooks)

    @mock.patch('stevedore.extension.ExtensionManager')
    def test_app_and_name(self, em):
        app = make_app()
        TestCommand(app, None, cmd_name='test')
        print(em.mock_calls[0])
        name, args, kwargs = em.mock_calls[0]
        print(kwargs)
        self.assertEqual('cliff.tests.test', kwargs['namespace'])


class TestHooks(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = make_app()
        self.cmd = TestCommand(self.app, None, cmd_name='test')
        self.hook_a = TestHook(self.cmd)
        self.hook_b = TestNullHook(self.cmd)
        self.mgr = extension.ExtensionManager.make_test_instance(
            [
                extension.Extension('parser-hook-a', None, None, self.hook_a),
                extension.Extension('parser-hook-b', None, None, self.hook_b),
            ],
        )
        # Replace the auto-loaded hooks with our explicitly created
        # manager.
        self.cmd._hooks = self.mgr

    def test_get_parser(self):
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.assertEqual(results.added_by_hook, 'value')

    def test_get_epilog(self):
        results = self.cmd.get_epilog()
        self.assertIn('hook epilog', results)

    def test_before(self):
        self.assertFalse(self.hook_a._before_called)
        self.assertFalse(self.hook_b._before_called)
        self.cmd.run(argparse.Namespace())
        self.assertTrue(self.hook_a._before_called)
        self.assertTrue(self.hook_b._before_called)

    def test_after(self):
        self.assertFalse(self.hook_a._after_called)
        self.assertFalse(self.hook_b._after_called)
        result = self.cmd.run(argparse.Namespace())
        self.assertTrue(self.hook_a._after_called)
        self.assertTrue(self.hook_b._after_called)
        self.assertEqual(result, 42)


class TestChangeHooks(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = make_app()
        self.cmd = TestCommand(self.app, None, cmd_name='test')
        self.hook = TestChangeHook(self.cmd)
        self.mgr = extension.ExtensionManager.make_test_instance(
            [extension.Extension('parser-hook', None, None, self.hook)],
        )
        # Replace the auto-loaded hooks with our explicitly created
        # manager.
        self.cmd._hooks = self.mgr

    def test_get_parser(self):
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.assertEqual(results.added_by_hook, 'value')

    def test_get_epilog(self):
        results = self.cmd.get_epilog()
        self.assertIn('hook epilog', results)

    def test_before(self):
        self.assertFalse(self.hook._before_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._before_called)
        self.assertEqual(results.added_by_hook, 'othervalue')
        self.assertTrue(results.added_by_before)

    def test_after(self):
        self.assertFalse(self.hook._after_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        result = self.cmd.run(results)
        self.assertTrue(self.hook._after_called)
        self.assertEqual(result, 24)


class TestShowOneHooks(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = make_app()
        self.cmd = TestShowCommand(self.app, None, cmd_name='test')
        self.hook = TestHook(self.cmd)
        self.mgr = extension.ExtensionManager.make_test_instance(
            [extension.Extension('parser-hook', None, None, self.hook)],
        )
        # Replace the auto-loaded hooks with our explicitly created
        # manager.
        self.cmd._hooks = self.mgr

    def test_get_parser(self):
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.assertEqual(results.added_by_hook, 'value')

    def test_get_epilog(self):
        results = self.cmd.get_epilog()
        self.assertIn('hook epilog', results)

    def test_before(self):
        self.assertFalse(self.hook._before_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._before_called)

    def test_after(self):
        self.assertFalse(self.hook._after_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._after_called)


class TestShowOneChangeHooks(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = make_app()
        self.cmd = TestShowCommand(self.app, None, cmd_name='test')
        self.hook = TestDisplayChangeHook(self.cmd)
        self.mgr = extension.ExtensionManager.make_test_instance(
            [extension.Extension('parser-hook', None, None, self.hook)],
        )
        # Replace the auto-loaded hooks with our explicitly created
        # manager.
        self.cmd._hooks = self.mgr

    def test_get_parser(self):
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.assertEqual(results.added_by_hook, 'value')

    def test_get_epilog(self):
        results = self.cmd.get_epilog()
        self.assertIn('hook epilog', results)

    def test_before(self):
        self.assertFalse(self.hook._before_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._before_called)
        self.assertEqual(results.added_by_hook, 'othervalue')
        self.assertTrue(results.added_by_before)

    def test_after(self):
        self.assertFalse(self.hook._after_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        result = self.cmd.run(results)
        self.assertTrue(self.hook._after_called)
        self.assertEqual(result, 0)


class TestListerHooks(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = make_app()
        self.cmd = TestListerCommand(self.app, None, cmd_name='test')
        self.hook = TestHook(self.cmd)
        self.mgr = extension.ExtensionManager.make_test_instance(
            [extension.Extension('parser-hook', None, None, self.hook)],
        )
        # Replace the auto-loaded hooks with our explicitly created
        # manager.
        self.cmd._hooks = self.mgr

    def test_get_parser(self):
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.assertEqual(results.added_by_hook, 'value')

    def test_get_epilog(self):
        results = self.cmd.get_epilog()
        self.assertIn('hook epilog', results)

    def test_before(self):
        self.assertFalse(self.hook._before_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._before_called)

    def test_after(self):
        self.assertFalse(self.hook._after_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._after_called)


class TestListerChangeHooks(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = make_app()
        self.cmd = TestListerCommand(self.app, None, cmd_name='test')
        self.hook = TestListerChangeHook(self.cmd)
        self.mgr = extension.ExtensionManager.make_test_instance(
            [extension.Extension('parser-hook', None, None, self.hook)],
        )
        # Replace the auto-loaded hooks with our explicitly created
        # manager.
        self.cmd._hooks = self.mgr

    def test_get_parser(self):
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.assertEqual(results.added_by_hook, 'value')

    def test_get_epilog(self):
        results = self.cmd.get_epilog()
        self.assertIn('hook epilog', results)

    def test_before(self):
        self.assertFalse(self.hook._before_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        self.cmd.run(results)
        self.assertTrue(self.hook._before_called)
        self.assertEqual(results.added_by_hook, 'othervalue')
        self.assertTrue(results.added_by_before)

    def test_after(self):
        self.assertFalse(self.hook._after_called)
        parser = self.cmd.get_parser('test')
        results = parser.parse_args(['--added-by-hook', 'value'])
        result = self.cmd.run(results)
        self.assertTrue(self.hook._after_called)
        self.assertEqual(result, 0)
