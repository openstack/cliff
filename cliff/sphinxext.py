# Copyright (C) 2017, Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import fnmatch
import importlib
import re
import sys

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils import statemachine

from cliff import app
from cliff import commandmanager


def _indent(text):
    """Indent by four spaces."""
    prefix = ' ' * 4

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if line.strip() else line)

    return ''.join(prefixed_lines())


def _format_description(parser):
    """Get parser description.

    We parse this as reStructuredText, allowing users to embed rich
    information in their help messages if they so choose.
    """
    for line in statemachine.string2lines(
            parser.description, tab_width=4, convert_whitespace=True):
        yield line


def _format_usage(parser):
    """Get usage without a prefix."""
    fmt = argparse.HelpFormatter(parser.prog)

    optionals = parser._get_optional_actions()
    positionals = parser._get_positional_actions()
    groups = parser._mutually_exclusive_groups

    # hacked variant of the regex used by the actual argparse module. Unlike
    # that version, this one attempts to group long and short opts with their
    # optional arguments ensuring that, for example, '--format <FORMAT>'
    # becomes ['--format <FORMAT>'] and not ['--format', '<FORMAT>'].
    # Yes, they really do use regexes to break apart and rewrap their help
    # string. Don't ask me why.
    part_regexp = re.compile(r"""
        \(.*?\)+ |
        \[.*?\]+ |
        (?:(?:-\w|--\w+(?:-\w+)*)(?:\s+<?\w[\w-]*>?)?) |
        \S+
    """, re.VERBOSE)

    opt_usage = fmt._format_actions_usage(optionals, groups)
    pos_usage = fmt._format_actions_usage(positionals, groups)

    opt_parts = part_regexp.findall(opt_usage)
    pos_parts = part_regexp.findall(pos_usage)
    parts = opt_parts + pos_parts

    if len(' '.join([parser.prog] + parts)) < 72:
        return [' '.join([parser.prog] + parts)]

    return [parser.prog] + [_indent(x) for x in parts]


def _format_epilog(parser):
    """Get parser epilog.

    We parse this as reStructuredText, allowing users to embed rich
    information in their help messages if they so choose.
    """
    for line in statemachine.string2lines(
            parser.epilog, tab_width=4, convert_whitespace=True):
        yield line


def _format_positional_action(action):
    """Format a positional action."""
    if action.help == argparse.SUPPRESS:
        return

    # NOTE(stephenfin): We strip all types of brackets from 'metavar' because
    # the 'option' directive dictates that only option argument names should be
    # surrounded by angle brackets
    yield '.. option:: {}'.format(
        (action.metavar or action.dest).strip('<>[]() '))
    if action.help:
        yield ''
        for line in statemachine.string2lines(
                action.help, tab_width=4, convert_whitespace=True):
            yield _indent(line)


def _format_optional_action(action):
    """Format an optional action."""
    if action.help == argparse.SUPPRESS:
        return

    if action.nargs == 0:
        yield '.. option:: {}'.format(', '.join(action.option_strings))
    else:
        # TODO(stephenfin): At some point, we may wish to provide more
        # information about the options themselves, for example, if nargs is
        # specified
        option_strings = [' '.join(
            [x, action.metavar or '<{}>'.format(action.dest.upper())])
            for x in action.option_strings]
        yield '.. option:: {}'.format(', '.join(option_strings))

    if action.help:
        yield ''
        for line in statemachine.string2lines(
                action.help, tab_width=4, convert_whitespace=True):
            yield _indent(line)


def _format_parser(parser):
    """Format the output of an argparse 'ArgumentParser' object.

    Given the following parser::

      >>> import argparse
      >>> parser = argparse.ArgumentParser(prog='hello-world', \
              description='This is my description.',
              epilog='This is my epilog')
      >>> parser.add_argument('name', help='User name', metavar='<name>')
      >>> parser.add_argument('--language', action='store', dest='lang', \
              help='Greeting language')

    Returns the following::

      This is my description.

      .. program:: hello-world
      .. code:: shell

          hello-world [-h] [--language LANG] <name>

      .. option:: name

          User name

      .. option:: --language LANG

          Greeting language

      .. option:: -h, --help

          Show this help message and exit

      This is my epilog.
    """
    if parser.description:
        for line in _format_description(parser):
            yield line
        yield ''

    yield '.. program:: {}'.format(parser.prog)

    yield '.. code-block:: shell'
    yield ''
    for line in _format_usage(parser):
        yield _indent(line)
    yield ''

    # In argparse, all arguments and parameters are known as "actions".
    # Optional actions are what would be known as flags or options in other
    # libraries, while positional actions would generally be known as
    # arguments. We present these slightly differently.

    for action in parser._get_optional_actions():
        for line in _format_optional_action(action):
            yield line
        yield ''

    for action in parser._get_positional_actions():
        for line in _format_positional_action(action):
            yield line
        yield ''

    if parser.epilog:
        for line in _format_epilog(parser):
            yield line
        yield ''


class AutoprogramCliffDirective(rst.Directive):
    """Auto-document a subclass of `cliff.command.Command`."""

    has_content = False
    required_arguments = 1
    option_spec = {
        'command': directives.unchanged,
        'arguments': directives.unchanged,
        'ignored': directives.unchanged,
        'application': directives.unchanged,
    }

    def _get_ignored_opts(self):
        global_ignored = self.env.config.autoprogram_cliff_ignored
        local_ignored = self.options.get('ignored', '')
        local_ignored = [x.strip() for x in local_ignored.split(',')
                         if x.strip()]
        return list(set(global_ignored + local_ignored))

    def _drop_ignored_options(self, parser, ignored_opts):
        for action in list(parser._actions):
            for option_string in action.option_strings:
                if option_string in ignored_opts:
                    del parser._actions[parser._actions.index(action)]
                    break

    def _load_app(self):
        mod_str, _sep, class_str = self.arguments[0].rpartition('.')
        if not mod_str:
            return
        try:
            importlib.import_module(mod_str)
        except ImportError:
            return
        try:
            cliff_app_class = getattr(sys.modules[mod_str], class_str)
        except AttributeError:
            return
        if not issubclass(cliff_app_class, app.App):
            return
        app_arguments = self.options.get('arguments', '').split()
        return cliff_app_class(*app_arguments)

    def _load_command(self, manager, command_name):
        """Load a command using an instance of a `CommandManager`."""
        try:
            # find_command expects the value of argv so split to emulate that
            return manager.find_command(command_name.split())[0]
        except ValueError:
            raise self.error('"{}" is not a valid command in the "{}" '
                             'namespace'.format(
                                 command_name, manager.namespace))

    def _load_commands(self):
        # TODO(sfinucan): We should probably add this wildcarding functionality
        # to the CommandManager itself to allow things like "show me the
        # commands like 'foo *'"
        command_pattern = self.options.get('command')
        manager = commandmanager.CommandManager(self.arguments[0])
        if command_pattern:
            commands = [x for x in manager.commands
                        if fnmatch.fnmatch(x, command_pattern)]
        else:
            commands = manager.commands.keys()
        return dict((name, self._load_command(manager, name))
                    for name in commands)

    def _generate_app_node(self, app, application_name):
        ignored_opts = self._get_ignored_opts()

        parser = app.parser

        self._drop_ignored_options(parser, ignored_opts)

        parser.prog = application_name

        source_name = '<{}>'.format(app.__class__.__name__)
        result = statemachine.ViewList()
        for line in _format_parser(parser):
            result.append(line, source_name)

        section = nodes.section()
        self.state.nested_parse(result, 0, section)

        # return [section.children]
        return section.children

    def _generate_nodes_per_command(self, title, command_name, command_class,
                                    ignored_opts):
        """Generate the relevant Sphinx nodes.

        This doesn't bother using raw docutils nodes as they simply don't offer
        the power of directives, like Sphinx's 'option' directive. Instead, we
        generate reStructuredText and parse this in a nested context (to obtain
        correct header levels). Refer to [1] for more information.

        [1] http://www.sphinx-doc.org/en/stable/extdev/markupapi.html

        :param title: Title of command
        :param command_name: Name of command, as used on the command line
        :param command_class: Subclass of :py:class:`cliff.command.Command`
        :param prefix: Prefix to apply before command, if any
        :param ignored_opts: A list of options to exclude from output, if any
        :returns: A list of nested docutil nodes
        """
        command = command_class(None, None)
        parser = command.get_parser(command_name)
        ignored_opts = ignored_opts or []

        self._drop_ignored_options(parser, ignored_opts)

        section = nodes.section(
            '',
            nodes.title(text=title),
            ids=[nodes.make_id(title)],
            names=[nodes.fully_normalize_name(title)])

        source_name = '<{}>'.format(command.__class__.__name__)
        result = statemachine.ViewList()

        for line in _format_parser(parser):
            result.append(line, source_name)

        self.state.nested_parse(result, 0, section)

        return [section]

    def _generate_command_nodes(self, commands, application_name):
        ignored_opts = self._get_ignored_opts()
        output = []
        for command_name in sorted(commands):
            command_class = commands[command_name]
            title = command_name
            if application_name:
                command_name = ' '.join([application_name, command_name])

            output.extend(self._generate_nodes_per_command(
                title, command_name, command_class, ignored_opts))

        return output

    def run(self):
        self.env = self.state.document.settings.env

        application_name = (self.options.get('application')
                            or self.env.config.autoprogram_cliff_application)

        app = self._load_app()
        if app:
            return self._generate_app_node(app, application_name)

        commands = self._load_commands()
        return self._generate_command_nodes(commands, application_name)


def setup(app):
    app.add_directive('autoprogram-cliff', AutoprogramCliffDirective)
    app.add_config_value('autoprogram_cliff_application', '', True)
    app.add_config_value('autoprogram_cliff_ignored', ['--help'], True)
