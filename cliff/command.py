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

import abc
import argparse
import inspect
import types
import sys
import typing as ty

from stevedore import extension

from cliff import _argparse

if sys.version_info < (3, 10):
    # Python 3.9 and older
    from importlib_metadata import packages_distributions
else:
    # Python 3.10 and later
    from importlib.metadata import packages_distributions  # type: ignore

if ty.TYPE_CHECKING:
    from . import app as _app

_T = ty.TypeVar('_T')
_dists_by_mods = None


def _get_distributions_by_modules() -> dict[str, str]:
    """Return dict mapping module name to distribution names.

    The python package name (the name used for importing) and the
    distribution name (the name used with pip and PyPI) do not
    always match. We want to report which distribution caused the
    command to be installed, so we need to look up the values.
    """
    global _dists_by_mods
    if _dists_by_mods is None:
        # There can be multiple distribution in the case of namespace packages
        # so we'll just grab the first one
        _dists_by_mods = {k: v[0] for k, v in packages_distributions().items()}
    return _dists_by_mods


def _get_distribution_for_module(
    module: ty.Optional[types.ModuleType],
) -> ty.Optional[str]:
    "Return the distribution containing the module."
    dist_name = None
    if module:
        pkg_name = module.__name__.partition('.')[0]
        dist_name = _get_distributions_by_modules().get(pkg_name)
    return dist_name


class Command(metaclass=abc.ABCMeta):
    """Base class for command plugins.

    When the command is instantiated, it loads extensions from a
    namespace based on the parent application namespace and the
    command name::

        app.namespace + '.' + cmd_name.replace(' ', '_')

    :param app: Application instance invoking the command.
    :param app_args: Parsed arguments from options associated with the
        application instance..
    :param cmd_name: The name of the command.
    """

    app_dist_name: ty.Optional[str]

    deprecated = False
    conflict_handler = 'ignore'

    _description = ''
    _epilog = None

    def __init__(
        self,
        app: '_app.App',
        app_args: ty.Optional[argparse.Namespace],
        cmd_name: ty.Optional[str] = None,
    ) -> None:
        self.app = app
        self.app_args = app_args
        self.cmd_name = cmd_name
        self._load_hooks()

    def _load_hooks(self) -> None:
        # Look for command extensions
        if self.cmd_name:
            namespace = '{}.{}'.format(
                self.app.command_manager.namespace,
                self.cmd_name.replace(' ', '_'),
            )
            self._hooks = extension.ExtensionManager(
                namespace=namespace,
                invoke_on_load=True,
                invoke_kwds={
                    'command': self,
                },
            )
        else:
            # Setting _hooks to an empty list allows iteration without
            # checking if there are hooks every time.
            self._hooks = []
        return

    def get_description(self) -> str:
        """Return the command description.

        The default is to use the first line of the class' docstring
        as the description. Set the ``_description`` class attribute
        to a one-line description of a command to use a different
        value. This is useful for enabling translations, for example,
        with ``_description`` set to a string wrapped with a gettext
        translation marker.

        """
        # NOTE(dhellmann): We need the trailing "or ''" because under
        # Python 2.7 the default for the docstring is None instead of
        # an empty string, and we always want this method to return a
        # string.
        desc = self._description or inspect.getdoc(self.__class__) or ''
        # The base class command description isn't useful for any
        # real commands, so ignore that value.
        if desc == inspect.getdoc(Command):
            desc = ''
        return desc

    def get_epilog(self) -> str:
        """Return the command epilog."""
        # replace a None in self._epilog with an empty string
        parts = [self._epilog or '']
        hook_epilogs = [
            e for h in self._hooks if (e := h.obj.get_epilog()) is not None
        ]
        parts.extend(hook_epilogs)
        app_dist_name = getattr(
            self,
            'app_dist_name',
            _get_distribution_for_module(inspect.getmodule(self.app)),
        )
        dist_name = _get_distribution_for_module(inspect.getmodule(self))
        if dist_name and dist_name != app_dist_name:
            parts.append(
                f'This command is provided by the {dist_name} plugin.'
            )
        return '\n\n'.join(parts)

    def get_parser(self, prog_name: str) -> _argparse.ArgumentParser:
        """Return an :class:`argparse.ArgumentParser`."""
        parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=_argparse.SmartHelpFormatter,
            conflict_handler=self.conflict_handler,
        )
        for hook in self._hooks:
            hook.obj.get_parser(parser)
        return parser

    @abc.abstractmethod
    def take_action(self, parsed_args: argparse.Namespace) -> ty.Any:
        """Override to do something useful.

        The returned value will be returned by the program.
        """

    def run(self, parsed_args: argparse.Namespace) -> int:
        """Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        Developers creating new command base classes (such as
        :class:`Lister` and :class:`ShowOne`) should override this
        method to wrap :meth:`take_action`.

        Return the value returned by :meth:`take_action` or 0.
        """
        parsed_args = self._run_before_hooks(parsed_args)
        return_code = self.take_action(parsed_args) or 0
        return_code = self._run_after_hooks(parsed_args, return_code)
        return return_code

    def _run_before_hooks(
        self, parsed_args: argparse.Namespace
    ) -> argparse.Namespace:
        """Calls before() method of the hooks.

        This method is intended to be called from the run() method before
        take_action() is called.

        This method should only be overridden by developers creating new
        command base classes and only if it is necessary to have different
        hook processing behavior.
        """
        for hook in self._hooks:
            ret = hook.obj.before(parsed_args)
            # If the return is None do not change parsed_args, otherwise
            # set up to pass it to the next hook
            if ret is not None:
                parsed_args = ret
        return parsed_args

    def _run_after_hooks(
        self, parsed_args: argparse.Namespace, return_code: _T
    ) -> _T:
        """Calls after() method of the hooks.

        This method is intended to be called from the run() method after
        take_action() is called.

        This method should only be overridden by developers creating new
        command base classes and only if it is necessary to have different
        hook processing behavior.
        """
        for hook in self._hooks:
            ret = hook.obj.after(parsed_args, return_code)
            # If the return is None do not change return_code, otherwise
            # set up to pass it to the next hook
            if ret is not None:
                return_code = ret
        return return_code
