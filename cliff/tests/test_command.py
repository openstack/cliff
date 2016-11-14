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

from cliff import command


class TestCommand(command.Command):
    """Description of command.
    """

    def take_action(self, parsed_args):
        return 42


class TestCommandNoDocstring(command.Command):

    def take_action(self, parsed_args):
        return 42


def test_get_description_docstring():
    cmd = TestCommand(None, None)
    desc = cmd.get_description()
    assert desc == "Description of command.\n    "


def test_get_description_attribute():
    cmd = TestCommand(None, None)
    # Artificially inject a value for _description to verify that it
    # overrides the docstring.
    cmd._description = 'this is not the default'
    desc = cmd.get_description()
    assert desc == 'this is not the default'


def test_get_description_default():
    cmd = TestCommandNoDocstring(None, None)
    desc = cmd.get_description()
    assert desc == ''


def test_get_parser():
    cmd = TestCommand(None, None)
    parser = cmd.get_parser('NAME')
    assert parser.prog == 'NAME'


def test_get_name():
    cmd = TestCommand(None, None, cmd_name='object action')
    assert cmd.cmd_name == 'object action'


def test_run_return():
    cmd = TestCommand(None, None, cmd_name='object action')
    assert cmd.run(None) == 42
