
"""Bash completion for the CLI.
"""

import logging

from cliff import command


class CompleteDictionary:
    """dictionary for bash completion
    """

    def __init__(self):
        self._dictionary = {}

    def add_command(self, command, actions):
        optstr = ""
        dicto = self._dictionary
        for action in actions:
            for opt in action.option_strings:
                if optstr:
                    optstr += " " + opt
                else:
                    optstr += opt
        last = None
        lastsubcmd = None
        for subcmd in command:
            if subcmd not in dicto:
                dicto[subcmd] = {}
            last = dicto
            lastsubcmd = subcmd
            dicto = dicto[subcmd]
        last[lastsubcmd] = optstr

    def get_commands(self):
        cmdo = ""
        keys = sorted(self._dictionary.keys())
        for cmd in keys:
            if cmdo == "":
                cmdo += cmd
            else:
                cmdo += " " + cmd
        return cmdo

    def _get_data_recurse(self, dictionary, path):
        ray = []
        keys = sorted(dictionary.keys())
        for cmd in keys:
            if path == "":
                name = str(cmd)
            else:
                name = path + "_" + str(cmd)
            value = dictionary[cmd]
            if isinstance(value, str):
                ray.append((name, value))
            else:
                cmdlist = ' '.join(sorted(value.keys()))
                ray.append((name, cmdlist))
                ray += self._get_data_recurse(value, name)
        return ray

    def get_data(self):
        return sorted(self._get_data_recurse(self._dictionary, ""))


class CompleteNoCode:
    """completion with no code
    """
    def __init__(self, name):
        self.name = name

    def get_header(self):
        return ''

    def get_trailer(self):
        return ''


class CompleteBash:
    """completion for bash
    """
    def __init__(self, name):
        self.name = str(name)

    def get_header(self):
        return ('_' + self.name + '()\n\
{\n\
  local cur prev words\n\
  COMPREPLY=()\n\
  _get_comp_words_by_ref -n : cur prev words\n\
\n\
  # Command data:\n')

    def get_trailer(self):
        return ('\
\n\
  cmd=""\n\
  words[0]=""\n\
  completed="${cmds}" \n\
  for var in "${words[@]:1}"\n\
  do\n\
    if [[ ${var} == -* ]] ; then\n\
      break\n\
    fi\n\
    if [ -z "${cmd}" ] ; then\n\
      proposed="${var}"\n\
    else\n\
      proposed="${cmd}_${var}"\n\
    fi\n\
    local i="cmds_${proposed}"\n\
    local comp="${!i}"\n\
    if [ -z "${comp}" ] ; then\n\
      break\n\
    fi\n\
    if [[ ${comp} == -* ]] ; then\n\
      if [[ ${cur} != -* ]] ; then\n\
        completed=""\n\
        break\n\
      fi\n\
    fi\n\
    cmd="${proposed}"\n\
    completed="${comp}"\n\
  done\n\
\n\
  if [ -z "${completed}" ] ; then\n\
    COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )\n\
  else\n\
    COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )\n\
  fi\n\
  return 0\n\
}\n\
complete -F _' + self.name + ' ' + self.name + '\n')


class CompleteCommand(command.Command):
    """print bash completion command
    """

    log = logging.getLogger(__name__ + '.CompleteCommand')

    def get_parser(self, prog_name):
        parser = super(CompleteCommand, self).get_parser(prog_name)
        parser.add_argument(
            "--name",
            default=None,
            metavar='<command_name>',
            help="Command name to support with command completion"
        )
        parser.add_argument(
            "--shell",
            default='bash',
            metavar='<shell>',
            choices=['bash', 'none'],
            help="Shell being used. Use none for data only (default: bash)"
        )
        return parser

    def get_actions(self, command):
        the_cmd = self.app.command_manager.find_command(command)
        cmd_factory, cmd_name, search_args = the_cmd
        cmd = cmd_factory(self.app, search_args)
        if self.app.interactive_mode:
            full_name = (cmd_name)
        else:
            full_name = (' '.join([self.app.NAME, cmd_name]))
        cmd_parser = cmd.get_parser(full_name)
        return cmd_parser._get_optional_actions()

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        if parsed_args.name:
            name = parsed_args.name
        else:
            name = self.app.NAME
        if parsed_args.shell == "none":
            shell = CompleteNoCode(name)
        else:
            shell = CompleteBash(name)

        self.app.stdout.write(shell.get_header())

        dicto = CompleteDictionary()
        for cmd in self.app.command_manager:
            command = cmd[0].split()
            dicto.add_command(command, self.get_actions(command))

        cmdo = dicto.get_commands()
        self.app.stdout.write("  cmds='{0}'\n".format(cmdo))
        for datum in dicto.get_data():
            self.app.stdout.write('  cmds_{0}=\'{1}\'\n'.format(*datum))

        self.app.stdout.write(shell.get_trailer())

        return 0
