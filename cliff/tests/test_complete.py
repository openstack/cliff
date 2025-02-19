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

"""Bash completion tests"""

import io
from unittest import mock

from cliff import app as application
from cliff import commandmanager
from cliff import complete
from cliff.tests import base


class TestCompletion(base.TestBase):
    def test_dictionary(self):
        sot = complete.CompleteDictionary()
        sot.add_command(
            "image delete".split(), [mock.Mock(option_strings=["1"])]
        )
        sot.add_command(
            "image list".split(), [mock.Mock(option_strings=["2"])]
        )
        sot.add_command(
            "image create".split(), [mock.Mock(option_strings=["3"])]
        )
        sot.add_command(
            "volume type create".split(), [mock.Mock(option_strings=["4"])]
        )
        sot.add_command(
            "volume type delete".split(), [mock.Mock(option_strings=["5"])]
        )
        self.assertEqual("image volume", sot.get_commands())
        result = sot.get_data()
        self.assertEqual("image", result[0][0])
        self.assertEqual("create delete list", result[0][1])
        self.assertEqual("image_create", result[1][0])
        self.assertEqual("3", result[1][1])
        self.assertEqual("image_delete", result[2][0])
        self.assertEqual("1", result[2][1])
        self.assertEqual("image_list", result[3][0])
        self.assertEqual("2", result[3][1])

    def test_complete_dictionary_subcmd(self):
        sot = complete.CompleteDictionary()
        sot.add_command(
            "image delete".split(), [mock.Mock(option_strings=["1"])]
        )
        sot.add_command(
            "image list".split(), [mock.Mock(option_strings=["2"])]
        )
        sot.add_command(
            "image list better".split(), [mock.Mock(option_strings=["3"])]
        )
        self.assertEqual("image", sot.get_commands())
        result = sot.get_data()
        self.assertEqual("image", result[0][0])
        self.assertEqual("delete list list_better", result[0][1])
        self.assertEqual("image_delete", result[1][0])
        self.assertEqual("1", result[1][1])
        self.assertEqual("image_list", result[2][0])
        self.assertEqual("2 better", result[2][1])
        self.assertEqual("image_list_better", result[3][0])
        self.assertEqual("3", result[3][1])


class TestCompletionAlternatives(base.TestBase):
    def given_cmdo_data(self):
        cmdo = "image server"
        data = [
            ("image", "create"),
            ("image_create", "--eolus"),
            ("server", "meta ssh"),
            ("server_meta_delete", "--wilson"),
            ("server_ssh", "--sunlight"),
        ]
        return cmdo, data

    def then_data(self, content):
        self.assertIn("  cmds='image server'", content)
        self.assertIn("  cmds_image='create'", content)
        self.assertIn("  cmds_image_create='--eolus'", content)
        self.assertIn("  cmds_server='meta ssh'", content)
        self.assertIn("  cmds_server_meta_delete='--wilson'", content)
        self.assertIn("  cmds_server_ssh='--sunlight'", content)

    def test_complete_no_code(self):
        output = io.StringIO()
        sot = complete.CompleteNoCode("doesNotMatter", output)
        sot.write(*self.given_cmdo_data())
        self.then_data(output.getvalue().splitlines())

    def test_complete_bash(self):
        output = io.StringIO()
        sot = complete.CompleteBash("openstack", output)
        sot.write(*self.given_cmdo_data())
        self.then_data(output.getvalue().splitlines())
        self.assertIn("_openstack()", output.getvalue().splitlines()[0])
        self.assertIn(
            "complete -F _openstack openstack",
            output.getvalue().splitlines()[-1],
        )

    def test_complete_command_parser(self):
        sot = complete.CompleteCommand(mock.Mock(), mock.Mock())
        parser = sot.get_parser('nothing')
        self.assertEqual("nothing", parser.prog)
        self.assertEqual("print bash completion command", parser.description)


class TestCompletionAction(base.TestBase):
    def given_complete_command(self):
        cmd_mgr = commandmanager.CommandManager('cliff.tests')
        app = application.App('testing', '1', cmd_mgr, stdout=io.StringIO())
        sot = complete.CompleteCommand(app, mock.Mock())
        cmd_mgr.add_command('complete', complete.CompleteCommand)
        return sot, app, cmd_mgr

    def then_actions_equal(self, actions):
        optstr = ' '.join(
            opt for action in actions for opt in action.option_strings
        )
        self.assertEqual('-h --help --name --shell', optstr)

    def test_complete_command_get_actions(self):
        sot, app, cmd_mgr = self.given_complete_command()
        app.interactive_mode = False
        actions = sot.get_actions(["complete"])
        self.then_actions_equal(actions)

    def test_complete_command_get_actions_interactive(self):
        sot, app, cmd_mgr = self.given_complete_command()
        app.interactive_mode = True
        actions = sot.get_actions(["complete"])
        self.then_actions_equal(actions)

    def test_complete_command_take_action(self):
        sot, app, cmd_mgr = self.given_complete_command()
        parsed_args = mock.Mock()
        parsed_args.name = "test_take"
        parsed_args.shell = "bash"
        self.assertEqual(0, sot.take_action(parsed_args))
        content = app.stdout.getvalue().splitlines()
        self.assertIn("_test_take()", content[0])
        self.assertIn("complete -F _test_take test_take", content[-1])
        self.assertIn("  cmds='complete help'", content)
        self.assertIn("  cmds_complete='-h --help --name --shell'", content)
        self.assertIn("  cmds_help='-h --help'", content)

    def test_complete_command_remove_dashes(self):
        sot, app, cmd_mgr = self.given_complete_command()
        parsed_args = mock.Mock()
        parsed_args.name = "test-take"
        parsed_args.shell = "bash"
        self.assertEqual(0, sot.take_action(parsed_args))
        content = app.stdout.getvalue().splitlines()
        self.assertIn("_test_take()", content[0])
        self.assertIn("complete -F _test_take test-take", content[-1])
