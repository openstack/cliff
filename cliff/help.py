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
import inspect
import traceback

import autopage.argparse

from . import command


class HelpExit(SystemExit):
    """Special exception type to trigger quick exit from the application

    We subclass from SystemExit to preserve API compatibility for
    anything that used to catch SystemExit, but use a different class
    so that cliff's Application can tell the difference between
    something trying to hard-exit and help saying it's done.
    """


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        app = self.default
        pager = autopage.argparse.help_pager(app.stdout)
        color = pager.to_terminal()
        autopage.argparse.use_color_for_parser(parser, color)
        with pager as out:
            parser.print_help(out)
            title_hl = ('\033[4m', '\033[0m') if color else ('', '')
            out.write('\n{}Commands{}:\n'.format(*title_hl))
            dists_by_module = command._get_distributions_by_modules()

            def dist_for_obj(obj):
                name = inspect.getmodule(obj).__name__.partition('.')[0]
                return dists_by_module.get(name)

            app_dist = dist_for_obj(app)
            command_manager = app.command_manager
            for name, ep in sorted(command_manager):
                try:
                    factory = ep.load()
                except Exception:
                    out.write(f'Could not load {ep!r}\n')
                    if namespace.debug:
                        traceback.print_exc(file=out)
                    continue
                try:
                    kwargs = {}
                    fact_args = inspect.getfullargspec(factory.__init__).args
                    if 'cmd_name' in fact_args:
                        kwargs['cmd_name'] = name
                    cmd = factory(app, None, **kwargs)
                    if cmd.deprecated:
                        continue
                except Exception as err:
                    out.write(f'Could not instantiate {ep!r}: {err}\n')
                    if namespace.debug:
                        traceback.print_exc(file=out)
                    continue
                one_liner = cmd.get_description().split('\n')[0].rstrip('.')
                dist_name = dist_for_obj(factory)
                if dist_name and dist_name != app_dist:
                    dist_info = ' (' + dist_name + ')'
                    if color:
                        dist_info = f'\033[90m{dist_info}\033[39m'
                else:
                    dist_info = ''
                if color:
                    name = f'\033[36m{name}\033[39m'
                out.write('  %-13s  %s%s\n' % (name, one_liner, dist_info))
        raise HelpExit()


class HelpCommand(command.Command):
    """print detailed help for another command"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'cmd',
            nargs='*',
            help='name of the command',
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.cmd:
            try:
                the_cmd = self.app.command_manager.find_command(
                    parsed_args.cmd,
                )
                cmd_factory, cmd_name, search_args = the_cmd
            except ValueError:
                # Did not find an exact match
                cmd = parsed_args.cmd[0]
                fuzzy_matches = [
                    k[0]
                    for k in self.app.command_manager
                    if k[0].startswith(cmd)
                ]
                if not fuzzy_matches:
                    raise
                self.app.stdout.write(f'Command "{cmd}" matches:\n')
                for fm in sorted(fuzzy_matches):
                    self.app.stdout.write(f'  {fm}\n')
                return
            self.app_args.cmd = search_args
            kwargs = {}
            if 'cmd_name' in inspect.getfullargspec(cmd_factory.__init__).args:
                kwargs['cmd_name'] = cmd_name
            cmd = cmd_factory(self.app, self.app_args, **kwargs)
            full_name = (
                cmd_name
                if self.app.interactive_mode
                else ' '.join([self.app.NAME, cmd_name])
            )
            cmd_parser = cmd.get_parser(full_name)
            pager = autopage.argparse.help_pager(self.app.stdout)
            with pager as out:
                autopage.argparse.use_color_for_parser(
                    cmd_parser, pager.to_terminal()
                )
                cmd_parser.print_help(out)
        else:
            action = HelpAction(None, None, default=self.app)
            action(self.app.parser, self.app.options, None, None)
        return 0
