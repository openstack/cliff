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

try:
    from StringIO import StringIO
except:
    from io import StringIO
import os
import sys

import mock

from cliff import app as application
from cliff import commandmanager
from cliff import help
from cliff.tests import utils


def test_show_help_for_command():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    help_cmd = help.HelpCommand(app, mock.Mock())
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
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    help_cmd = help.HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args(['t'])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    help_output = stdout.getvalue()
    assert 'Command "t" matches:' in help_output
    assert 'three word command\n  two words\n' in help_output


def test_list_matching_commands_no_match():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    help_cmd = help.HelpCommand(app, mock.Mock())
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
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    app.options = mock.Mock()
    help_cmd = help.HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args([])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    help_text = stdout.getvalue()
    basecommand = os.path.split(sys.argv[0])[1]
    assert 'usage: %s [--version]' % basecommand in help_text
    assert 'optional arguments:\n  --version' in help_text
    expected = (
        '  one            Test command.\n'
        '  three word command  Test command.\n'
    )
    assert expected in help_text


def test_list_deprecated_commands():
    # FIXME(dhellmann): Are commands tied too closely to the app? Or
    # do commands know too much about apps by using them to get to the
    # command manager?
    stdout = StringIO()
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    try:
        app.run(['--help'])
    except SystemExit:
        pass
    help_output = stdout.getvalue()
    assert 'two words' in help_output
    assert 'three word command' in help_output
    assert 'old cmd' not in help_output


@mock.patch.object(commandmanager.EntryPointWrapper, 'load',
                   side_effect=Exception('Could not load EntryPoint'))
def test_show_help_with_ep_load_fail(mock_load):
    stdout = StringIO()
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    app.options = mock.Mock()
    app.options.debug = False
    help_cmd = help.HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args([])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    help_output = stdout.getvalue()
    assert 'Commands:' in help_output
    assert 'Could not load' in help_output
    assert 'Exception: Could not load EntryPoint' not in help_output


@mock.patch.object(commandmanager.EntryPointWrapper, 'load',
                   side_effect=Exception('Could not load EntryPoint'))
def test_show_help_print_exc_with_ep_load_fail(mock_load):
    stdout = StringIO()
    app = application.App('testing', '1',
                          utils.TestCommandManager(utils.TEST_NAMESPACE),
                          stdout=stdout)
    app.NAME = 'test'
    app.options = mock.Mock()
    app.options.debug = True
    help_cmd = help.HelpCommand(app, mock.Mock())
    parser = help_cmd.get_parser('test')
    parsed_args = parser.parse_args([])
    try:
        help_cmd.run(parsed_args)
    except SystemExit:
        pass
    help_output = stdout.getvalue()
    assert 'Commands:' in help_output
    assert 'Could not load' in help_output
    assert 'Exception: Could not load EntryPoint' in help_output
