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

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils import statemachine

from cliff import commandmanager


def _indent(text):
    """Indent by four spaces."""
    prefix = ' ' * 4

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if line.strip() else line)

    return ''.join(prefixed_lines())


def _format_usage(parser):
    """Get usage without a prefix."""
    fmt = argparse.HelpFormatter(parser.prog)
    fmt.add_usage(parser.usage, parser._actions,
                  parser._mutually_exclusive_groups, prefix='')

    return fmt.format_help().strip().splitlines()


def _format_positional_action(action):
    """Format a positional action."""
    if action.help == argparse.SUPPRESS:
        return

    # NOTE(stephenfin): We use 'dest' - not 'metavar' - because the 'option'
    # directive dictates that only option argument names should be surrounded
    # by angle brackets
    yield '.. option:: {}'.format(action.dest)
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
      >>> parser = argparse.ArgumentParser(prog='hello-world')
      >>> parser.add_argument('name', help='User name', metavar='<name>')
      >>> parser.add_argument('--language', action='store', dest='lang', \
              help='Greeting language')

    Returns the following::

      .. program:: hello-world
      .. code:: shell

          hello-world [-h] [--language LANG] <name>

      .. option:: name

          User name

      .. option:: --language LANG

          Greeting language

      .. option:: -h, --help

          Show this help message and exit
    """
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


class AutoprogramCliffDirective(rst.Directive):
    """Auto-document a subclass of `cliff.command.Command`."""

    has_content = False
    required_arguments = 1
    option_spec = {
        'command': directives.unchanged,
    }

    def _load_command(self, manager, command_name):
        """Load a command using an instance of a `CommandManager`."""
        try:
            # find_command expects the value of argv so split to emulate that
            return manager.find_command(command_name.split())[0]
        except ValueError:
            raise self.error('"{}" is not a valid command in the "{}" '
                             'namespace'.format(
                                 command_name, manager.namespace))

    def _generate_nodes(self, title, command_name, command_class):
        """Generate the relevant Sphinx nodes.

        This is a little funky. Parts of this use raw docutils nodes while
        other parts use reStructuredText and nested parsing. The reason for
        this is simple: it avoids us having to reinvent the wheel. While raw
        docutils nodes are helpful for the simpler elements of the output,
        they don't provide an easy way to use Sphinx's own directives, such as
        the 'option' directive. Refer to [1] for more information.

        [1] http://www.sphinx-doc.org/en/stable/extdev/markupapi.html

        :param title: Title of command
        :param command_name: Name of command, as used on the command line
        :param command_class: Subclass of :py:class:`cliff.command.Command`
        :param prefix: Prefix to apply before command, if any
        :returns: A list of nested docutil nodes
        """
        command = command_class(None, None)
        parser = command.get_parser(command_name)
        description = command.get_description()
        epilog = command.get_epilog()

        # Drop the automatically-added help action
        for action in parser._actions:
            if isinstance(action, argparse._HelpAction):
                del parser._actions[parser._actions.index(action)]

        # Title

        # We build this with plain old docutils nodes

        section = nodes.section(
            '',
            nodes.title(text=title),
            ids=[nodes.make_id(title)],
            names=[nodes.fully_normalize_name(title)])

        source_name = '<{}>'.format(command.__class__.__name__)
        result = statemachine.ViewList()

        # Description

        # We parse this as reStructuredText, allowing users to embed rich
        # information in their help messages if they so choose.

        if description:
            for line in statemachine.string2lines(
                    description, tab_width=4, convert_whitespace=True):
                result.append(line, source_name)

            result.append('', source_name)

        # Summary

        # We both build and parse this as reStructuredText

        for line in _format_parser(parser):
            result.append(line, source_name)

        self.state.nested_parse(result, 0, section)

        # Epilog

        # Like description, this is parsed as reStructuredText

        if epilog:
            result.append('', source_name)

            for line in statemachine.string2lines(
                    epilog, tab_width=4, convert_whitespace=True):
                result.append(line, source_name)

        return [section]

    def run(self):
        self.env = self.state.document.settings.env

        command_pattern = self.options.get('command')
        application_name = self.env.config.autoprogram_cliff_application or ''

        # TODO(sfinucan): We should probably add this wildcarding functionality
        # to the CommandManager itself to allow things like "show me the
        # commands like 'foo *'"
        manager = commandmanager.CommandManager(self.arguments[0])
        if command_pattern:
            commands = [x for x in manager.commands
                        if fnmatch.fnmatch(x, command_pattern)]
        else:
            commands = manager.commands.keys()

        output = []
        for command_name in sorted(commands):
            command_class = self._load_command(manager, command_name)

            title = command_name
            if application_name:
                command_name = ' '.join([application_name, command_name])

            output.extend(self._generate_nodes(
                title, command_name, command_class))

        return output


def setup(app):
    app.add_directive('autoprogram-cliff', AutoprogramCliffDirective)
    app.add_config_value('autoprogram_cliff_application', '', True)
