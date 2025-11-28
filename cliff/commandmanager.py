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
import importlib.metadata
import logging
from typing import TypeAlias
import warnings

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
    """An entrypoint-like object.

    Wrap up a command class already imported to make it look like a plugin.
    """

    def __init__(
        self, name: str, command_class: type[command.Command]
    ) -> None:
        self.name = name
        self.command_class = command_class

    def load(self) -> type[command.Command]:
        return self.command_class

    @property
    def value(self) -> str:
        # fake entry point target for logging purposes
        return ':'.join(
            [self.command_class.__module__, self.command_class.__name__]
        )


EntryPointT: TypeAlias = EntryPointWrapper | importlib.metadata.EntryPoint


class CommandManager:
    """Discovers commands and handles lookup based on argv data.

    :param namespace: **DEPRECATED** String containing the entrypoint namespace
        for the plugins to be loaded from by default. For example,
        ``'cliff.formatter.list'``. :meth:`CommandManager.load_commands` should
        be preferred.
    :param convert_underscores: Whether cliff should convert underscores to
        spaces in entry_point commands.
    :param ignored_modules: A list of module names to ignore when loading
        commands. This will be matched partial, so be as specific as needed.
    """

    def __init__(
        self,
        namespace: str | None = None,
        convert_underscores: bool = True,
        *,
        ignored_modules: collections.abc.Iterable[str] | None = None,
    ) -> None:
        if namespace:
            # TODO(stephenfin): Remove this functionality in 5.0.0 and make
            # convert_underscores a kwarg-only argument
            warnings.warn(
                f'Initialising {self.__class__!r} with a namespace is '
                f'deprecated for removal. Prefer loading commands from a '
                f'given namespace with load_commands instead',
                DeprecationWarning,
            )

        self.namespace = namespace
        self.convert_underscores = convert_underscores
        self.ignored_modules = ignored_modules or ()

        self.commands: dict[str, EntryPointT] = {}
        self._legacy: dict[str, str] = {}
        self.group_list: list[str] = []
        self._load_commands()

    def _load_commands(self) -> None:
        # NOTE(jamielennox): kept for compatibility.
        # TODO(stephenfin): We can remove this when we remove the 'namespace'
        # argument
        if self.namespace:
            self.load_commands(self.namespace)

    @staticmethod
    def _is_module_ignored(
        module_name: str, ignored_modules: collections.abc.Iterable[str]
    ) -> bool:
        # given module_name = 'foo.bar.baz:wow', we expect to match any of
        # the following ignores: foo.bar.baz:wow, foo.bar.baz, foo.bar, foo
        while True:
            if module_name in ignored_modules:
                return True

            split_index = max(module_name.rfind(':'), module_name.rfind('.'))
            if split_index == -1:
                break

            module_name = module_name[:split_index]

        return False

    def load_commands(self, namespace: str) -> None:
        """Load all the commands from an entrypoint

        :param namespace: The namespace to load commands from.
        :returns: None
        """
        self.group_list.append(namespace)
        em: stevedore.ExtensionManager[command.Command]
        # note that we don't invoke stevedore's conflict resolver functionality
        # because that is namespace specific and we care about conflicts
        # regardless of the namespace
        em = stevedore.ExtensionManager(namespace)
        for ext in em:
            LOG.debug('found command %r', ext.name)

            if self._is_module_ignored(ext.module_name, self.ignored_modules):
                LOG.debug(
                    'extension found in ignored module %r: skipping',
                    ext.module_name,
                )
                continue

            cmd_name = (
                ext.name.replace('_', ' ')
                if self.convert_underscores
                else ext.name
            )

            if cmd_name in self.commands:
                # Attention, programmers: If you arrived here attempting to
                # resolve a warning in your application then you have a command
                # with the same name either defined more than once in the same
                # application (a typo?) or in multiple packages (for example,
                # a package that adds plugins to your applications). The latter
                # can often happen if you e.g. move a command from a plugin to
                # the core application. In this situation, you should add the
                # old location to 'ignored_modules' and the plugin will now be
                # ignored.
                LOG.warning(
                    'found duplicate implementations of the %(name)r command '
                    'in the following modules: %(modules)s: this is likely '
                    'programmer error and should be reported as a bug to the '
                    'relevant project(s)',
                    {
                        'name': cmd_name,
                        'modules': ', '.join(
                            [
                                self.commands[cmd_name].value,
                                ext.entry_point.value,
                            ]
                        ),
                    },
                )

            self.commands[cmd_name] = ext.entry_point

    def __iter__(
        self,
    ) -> collections.abc.Iterator[tuple[str, EntryPointT]]:
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

    def add_command_group(self, group: str | None = None) -> None:
        """Adds another group of command entrypoints"""
        if group:
            self.load_commands(group)

    def get_command_groups(self) -> list[str]:
        """Returns a list of the loaded command groups"""
        return self.group_list

    def get_command_names(self, group: str | None = None) -> list[str]:
        """Returns a list of commands loaded for the specified group"""
        group_list: list[str] = []
        if group is not None:
            em: stevedore.ExtensionManager[command.Command]
            em = stevedore.ExtensionManager(group)
            for ep in em:
                cmd_name = (
                    ep.name.replace('_', ' ')
                    if self.convert_underscores
                    else ep.name
                )
                group_list.append(cmd_name)
            return group_list
        return list(self.commands.keys())
