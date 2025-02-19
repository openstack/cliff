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

"""Discover and lookup command plugins."""

import collections.abc
import inspect
import logging
import typing as ty

import stevedore

from cliff import command

LOG = logging.getLogger(__name__)


def _get_commands_by_partial_name(
    args: list[str], commands: list[str]
) -> list[str]:
    n = len(args)
    candidates = []
    for command_name in commands:
        command_parts = command_name.split()
        if len(command_parts) != n:
            continue
        if all(command_parts[i].startswith(args[i]) for i in range(n)):
            candidates.append(command_name)
    return candidates


class EntryPointWrapper:
    """Wrap up a command class already imported to make it look like a plugin."""

    def __init__(
        self, name: str, command_class: type[command.Command]
    ) -> None:
        self.name = name
        self.command_class = command_class

    def load(self, require: bool = False) -> type[command.Command]:
        return self.command_class


class CommandManager:
    """Discovers commands and handles lookup based on argv data.

    :param namespace: String containing the entrypoint namespace for the
        plugins to be loaded. For example, ``'cliff.formatter.list'``.
    :param convert_underscores: Whether cliff should convert underscores to
        spaces in entry_point commands.
    """

    def __init__(
        self, namespace: str, convert_underscores: bool = True
    ) -> None:
        self.commands: dict[str, EntryPointWrapper] = {}
        self._legacy: dict[str, str] = {}
        self.namespace = namespace
        self.convert_underscores = convert_underscores
        self.group_list: list[str] = []
        self._load_commands()

    def _load_commands(self) -> None:
        # NOTE(jamielennox): kept for compatibility.
        if self.namespace:
            self.load_commands(self.namespace)

    def load_commands(self, namespace: str) -> None:
        """Load all the commands from an entrypoint"""
        self.group_list.append(namespace)
        for ep in stevedore.ExtensionManager(namespace):
            LOG.debug('found command %r', ep.name)
            cmd_name = (
                ep.name.replace('_', ' ')
                if self.convert_underscores
                else ep.name
            )
            self.commands[cmd_name] = ep.entry_point

    def __iter__(
        self,
    ) -> collections.abc.Iterator[tuple[str, EntryPointWrapper]]:
        return iter(self.commands.items())

    def add_command(
        self, name: str, command_class: type[command.Command]
    ) -> None:
        self.commands[name] = EntryPointWrapper(name, command_class)

    def add_legacy_command(self, old_name: str, new_name: str) -> None:
        """Map an old command name to the new name.

        :param old_name: The old command name.
        :type old_name: str
        :param new_name: The new command name.
        :type new_name: str
        """
        self._legacy[old_name] = new_name

    def find_command(
        self, argv: list[str]
    ) -> tuple[type[command.Command], str, list[str]]:
        """Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        start = self._get_last_possible_command_index(argv)
        for i in range(start, 0, -1):
            name = ' '.join(argv[:i])
            search_args = argv[i:]
            # The legacy command handling may modify name, so remember
            # the value we actually found in argv so we can return it.
            return_name = name
            # Convert the legacy command name to its new name.
            if name in self._legacy:
                name = self._legacy[name]

            found = None
            if name in self.commands:
                found = name
            else:
                candidates = _get_commands_by_partial_name(
                    argv[:i], list(self.commands.keys())
                )
                if len(candidates) == 1:
                    found = candidates[0]
            if found:
                cmd_ep = self.commands[found]
                if hasattr(cmd_ep, 'resolve'):
                    cmd_factory = cmd_ep.resolve()
                else:
                    # NOTE(dhellmann): Some fake classes don't take
                    # require as an argument. Yay?
                    arg_spec = inspect.getfullargspec(cmd_ep.load)
                    if 'require' in arg_spec[0]:
                        cmd_factory = cmd_ep.load(require=False)
                    else:
                        cmd_factory = cmd_ep.load()
                return (cmd_factory, return_name, search_args)
        else:
            raise ValueError(f'Unknown command {argv!r}')

    def _get_last_possible_command_index(self, argv: list[str]) -> int:
        """Returns the index after the last argument
        in argv that can be a command word
        """
        for i, arg in enumerate(argv):
            if arg.startswith('-'):
                return i
        return len(argv)

    def add_command_group(self, group: ty.Optional[str] = None) -> None:
        """Adds another group of command entrypoints"""
        if group:
            self.load_commands(group)

    def get_command_groups(self) -> list[str]:
        """Returns a list of the loaded command groups"""
        return self.group_list

    def get_command_names(self, group: ty.Optional[str] = None) -> list[str]:
        """Returns a list of commands loaded for the specified group"""
        group_list: list[str] = []
        if group is not None:
            for ep in stevedore.ExtensionManager(group):
                cmd_name = (
                    ep.name.replace('_', ' ')
                    if self.convert_underscores
                    else ep.name
                )
                group_list.append(cmd_name)
            return group_list
        return list(self.commands.keys())
