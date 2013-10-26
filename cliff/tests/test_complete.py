"""Bash completion tests
"""

import mock
import os

from cliff import complete


def test_add_command():
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

def create_complete_command_mocks():
    app = mock.Mock(name="app")
    app_args = mock.Mock(name="app_args")
    # actions
    action_one = mock.Mock(name="action_one")
    action_one.option_strings = ["Eolus"]
    action_two = mock.Mock(name="action_two")
    action_two.option_strings = ["Wilson", "Sunlight"]
    actions = [action_one, action_two]
    # get_optional_actions
    get_optional_actions = mock.Mock(name="get_optional_actions")
    get_optional_actions.return_value = actions
    # cmd_parser
    cmd_parser = mock.Mock(name="cmd_parser")
    cmd_parser._get_optional_actions = get_optional_actions
    # get_parser
    get_parser = mock.Mock(name="get_parser")
    get_parser.return_value = cmd_parser
    # cmd_factory_init
    cmd_factory_init = mock.Mock("cmd_factory_init")
    cmd_factory_init.get_parser = get_parser
    # cmd_factory
    cmd_factory = mock.Mock(name="cmd_factory")
    cmd_factory.return_value = cmd_factory_init
    # find_command
    cmd_name = "yale"
    search_args = "search_args"
    find_command = mock.Mock(name="find_command")
    find_command.return_value = (cmd_factory, cmd_name, search_args)
    # command_manager
    commands = [["image create"], ["server meta delete"], ["server ssh"]]
    command_manager = mock.MagicMock()
    command_manager.__iter__.return_value = iter(commands)
    command_manager.find_command = find_command
    app.command_manager = command_manager
    app.NAME = "openstack"
    app.interactive_mode = False
    app.stdout = FakeStdout()
    return (complete.CompleteCommand(app, app_args), app, actions, cmd_factory_init)

def check_parser(cmd, args, verify_args):
    cmd_parser = cmd.get_parser('check_parser')
    parsed_args = cmd_parser.parse_args(args)
    for av in verify_args:
        attr, value = av
        if attr:
            assert attr in parsed_args
            assert getattr(parsed_args, attr) == value

def test_parser_nothing():
    sot, app, actions, cmd_factory_init = create_complete_command_mocks()
    check_parser(sot, [], [('name', None), ('shell', 'bash')])

def test_parser_no_code():
    sot, app, actions, cmd_factory_init = create_complete_command_mocks()
    check_parser(sot, ["--shell", "none", "--name", "foo"],
                      [('name', 'foo'), ('shell', 'none')])

def test_get_actions():
    sot, app, actions, cmd_factory_init = create_complete_command_mocks()
    result = sot.get_actions("yale")
    cmd_factory_init.get_parser.assert_called_with('openstack yale')
    assert actions == result

def test_get_actions_interactive():
    sot, app, actions, cmd_factory_init = create_complete_command_mocks()
    app.interactive_mode = True
    result = sot.get_actions("yale")
    cmd_factory_init.get_parser.assert_called_with('yale')
    assert actions == result

def verify_data(content):
    assert "  cmds='image server'\n" in content
    assert "  cmds_image='create'\n" in content
    assert "  cmds_image_create='Eolus Wilson Sunlight'\n" in content
    assert "  cmds_server='meta ssh'\n" in content
    assert "  cmds_server_meta_delete='Eolus Wilson Sunlight'\n" in content
    assert "  cmds_server_ssh='Eolus Wilson Sunlight'\n" in content

def test_take_action_nocode():
    sot, app, actions, cmd_factory_init = create_complete_command_mocks()
    parsed_args = mock.Mock()
    parsed_args.shell = "none"
    sot.take_action(parsed_args)
    verify_data(app.stdout.content)

def test_take_action_code():
    sot, app, actions, cmd_factory_init = create_complete_command_mocks()
    parsed_args = mock.Mock()
    parsed_args.name = "openstack"
    sot.take_action(parsed_args)
    verify_data(app.stdout.content)
    assert "_openstack()\n" in app.stdout.content[0]
    assert "complete -F _openstack openstack\n" in app.stdout.content[-1]
