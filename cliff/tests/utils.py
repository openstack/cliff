
from cliff.command import Command
from cliff.commandmanager import CommandManager

TEST_NAMESPACE = 'cliff.test'


class TestParser(object):

    def print_help(self, stdout):
        stdout.write('TestParser')


class TestCommand(Command):

    def get_parser(self, ignore):
        # Make it look like this class is the parser
        # so parse_args() is called.
        return TestParser()

    def take_action(self, args):
        return


class TestDeprecatedCommand(TestCommand):

    deprecated = True


class TestCommandManager(CommandManager):

    def load_commands(self, namespace):
        if namespace == TEST_NAMESPACE:
            for key in ('one', 'two words', 'three word command'):
                self.add_command(key, TestCommand)
            self.add_command('old cmd', TestDeprecatedCommand)
