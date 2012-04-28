import argparse
import sys

from .command import Command


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        print('')
        print('Commands:')
        command_manager = self.default
        for name, ep in sorted(command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            print('  %-13s  %s' % (name, one_liner))
        sys.exit(0)


class HelpCommand(Command):
    """print detailed help for another command
    """

    def get_parser(self, prog_name):
        parser = super(HelpCommand, self).get_parser(prog_name)
        parser.add_argument('cmd',
                            nargs='*',
                            help='name of the command',
                            )
        return parser

    def run(self, parsed_args):
        if parsed_args.cmd:
            cmd_factory, cmd_name, search_args = self.app.command_manager.find_command(parsed_args.cmd)
            cmd = cmd_factory(self.app, search_args)
            full_name = (cmd_name
                         if self.app.interactive_mode
                         else ' '.join([self.app.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
        else:
            cmd_parser = self.get_parser(' '.join([self.app.NAME, 'help']))
        cmd_parser.parse_args(['--help'])
        return 0
