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

"""Bash completion tests
"""

import mock

from cliff import app as application
from cliff import commandmanager
from cliff import complete


def test_complete_dictionary():
    sot = complete.CompleteDictionary()
    sot.add_command("image delete".split(),
                    [mock.Mock(option_strings=["1"])])
    sot.add_command("image list".split(),
                    [mock.Mock(option_strings=["2"])])
    sot.add_command("image create".split(),
                    [mock.Mock(option_strings=["3"])])
    sot.add_command("volume type create".split(),
                    [mock.Mock(option_strings=["4"])])
    sot.add_command("volume type delete".split(),
                    [mock.Mock(option_strings=["5"])])
    assert "image volume" == sot.get_commands()
    result = sot.get_data()
    assert "image" == result[0][0]
    assert "create delete list" == result[0][1]
    assert "image_create" == result[1][0]
    assert "3" == result[1][1]
    assert "image_delete" == result[2][0]
    assert "1" == result[2][1]
    assert "image_list" == result[3][0]
    assert "2" == result[3][1]


def test_complete_dictionary_subcmd():
    sot = complete.CompleteDictionary()
    sot.add_command("image delete".split(),
                    [mock.Mock(option_strings=["1"])])
    sot.add_command("image list".split(),
                    [mock.Mock(option_strings=["2"])])
    sot.add_command("image list better".split(),
                    [mock.Mock(option_strings=["3"])])
    assert "image" == sot.get_commands()
    result = sot.get_data()
    assert "image" == result[0][0]
    assert "delete list list_better" == result[0][1]
    assert "image_delete" == result[1][0]
    assert "1" == result[1][1]
    assert "image_list" == result[2][0]
    assert "2 better" == result[2][1]
    assert "image_list_better" == result[3][0]
    assert "3" == result[3][1]


class FakeStdout:
    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result = result + line
        return result


def given_cmdo_data():
    cmdo = "image server"
    data = [("image", "create"),
            ("image_create", "--eolus"),
            ("server", "meta ssh"),
            ("server_meta_delete", "--wilson"),
            ("server_ssh", "--sunlight")]
    return cmdo, data


def then_data(content):
    assert "  cmds='image server'\n" in content
    assert "  cmds_image='create'\n" in content
    assert "  cmds_image_create='--eolus'\n" in content
    assert "  cmds_server='meta ssh'\n" in content
    assert "  cmds_server_meta_delete='--wilson'\n" in content
    assert "  cmds_server_ssh='--sunlight'\n" in content


def test_complete_no_code():
    output = FakeStdout()
    sot = complete.CompleteNoCode("doesNotMatter", output)
    sot.write(*given_cmdo_data())
    then_data(output.content)


def test_complete_bash():
    output = FakeStdout()
    sot = complete.CompleteBash("openstack", output)
    sot.write(*given_cmdo_data())
    then_data(output.content)
    assert "_openstack()\n" in output.content[0]
    assert "complete -F _openstack openstack\n" in output.content[-1]


def test_complete_command_parser():
    sot = complete.CompleteCommand(mock.Mock(), mock.Mock())
    parser = sot.get_parser('nothing')
    assert "nothing" == parser.prog
    assert "print bash completion command\n    " == parser.description


def given_complete_command():
    cmd_mgr = commandmanager.CommandManager('cliff.tests')
    app = application.App('testing', '1', cmd_mgr, stdout=FakeStdout())
    sot = complete.CompleteCommand(app, mock.Mock())
    cmd_mgr.add_command('complete', complete.CompleteCommand)
    return sot, app, cmd_mgr


def then_actions_equal(actions):
    optstr = ' '.join(opt for action in actions
                      for opt in action.option_strings)
    assert '-h --help --name --shell' == optstr


def test_complete_command_get_actions():
    sot, app, cmd_mgr = given_complete_command()
    app.interactive_mode = False
    actions = sot.get_actions(["complete"])
    then_actions_equal(actions)


def test_complete_command_get_actions_interactive():
    sot, app, cmd_mgr = given_complete_command()
    app.interactive_mode = True
    actions = sot.get_actions(["complete"])
    then_actions_equal(actions)


def test_complete_command_take_action():
    sot, app, cmd_mgr = given_complete_command()
    parsed_args = mock.Mock()
    parsed_args.name = "test_take"
    parsed_args.shell = "bash"
    content = app.stdout.content
    assert 0 == sot.take_action(parsed_args)
    assert "_test_take()\n" in content[0]
    assert "complete -F _test_take test_take\n" in content[-1]
    assert "  cmds='complete help'\n" in content
    assert "  cmds_complete='-h --help --name --shell'\n" in content
    assert "  cmds_help='-h --help'\n" in content


def test_complete_command_remove_dashes():
    sot, app, cmd_mgr = given_complete_command()
    parsed_args = mock.Mock()
    parsed_args.name = "test-take"
    parsed_args.shell = "bash"
    content = app.stdout.content
    assert 0 == sot.take_action(parsed_args)
    assert "_test_take()\n" in content[0]
    assert "complete -F _test_take test-take\n" in content[-1]
