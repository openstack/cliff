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
import inspect

import six
from stevedore import extension

from cliff import _argparse

_dists_by_mods = None


def _get_distributions_by_modules():
    """Return dict mapping module name to distribution names.

    The python package name (the name used for importing) and the
    distribution name (the name used with pip and PyPI) do not
    always match. We want to report which distribution caused the
    command to be installed, so we need to look up the values.

    """
    import pkg_resources
    global _dists_by_mods
    if _dists_by_mods is None:
        results = {}
        for dist in pkg_resources.working_set:
            try:
                mod_names = dist.get_metadata('top_level.txt').strip()
            except Exception:
                # Could not retrieve metadata. Either the file is not
                # present or we cannot read it. Ignore the
                # distribution.
                pass
            else:
                # Distributions may include multiple top-level
                # packages (see setuptools for an example).
                for mod_name in mod_names.splitlines():
                    results[mod_name] = dist.project_name
        _dists_by_mods = results
    return _dists_by_mods


def _get_distribution_for_module(module):
    "Return the distribution containing the module."
    dist_name = None
    if module:
        pkg_name = module.__name__.partition('.')[0]
        dist_name = _get_distributions_by_modules().get(pkg_name)
    return dist_name


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    """Base class for command plugins.

    When the command is instantiated, it loads extensions from a
    namespace based on the parent application namespace and the
    command name::

        app.namespace + '.' + cmd_name.replace(' ', '_')

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App

    """

    deprecated = False

    _description = ''
    _epilog = None

    def __init__(self, app, app_args, cmd_name=None):
        self.app = app
        self.app_args = app_args
        self.cmd_name = cmd_name
        self._load_hooks()

    def _load_hooks(self):
        # Look for command extensions
        if self.app and self.cmd_name:
            namespace = '{}.{}'.format(
                self.app.command_manager.namespace,
                self.cmd_name.replace(' ', '_')
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

    def get_description(self):
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

    def get_epilog(self):
        """Return the command epilog."""
        # replace a None in self._epilog with an empty string
        parts = [self._epilog or '']
        hook_epilogs = filter(
            None,
            (h.obj.get_epilog() for h in self._hooks),
        )
        parts.extend(hook_epilogs)
        app_dist_name = getattr(
            self, 'app_dist_name', _get_distribution_for_module(
                inspect.getmodule(self.app)
            )
        )
        dist_name = _get_distribution_for_module(inspect.getmodule(self))
        if dist_name and dist_name != app_dist_name:
            parts.append(
                'This command is provided by the %s plugin.' %
                (dist_name,)
            )
        return '\n\n'.join(parts)

    def get_parser(self, prog_name):
        """Return an :class:`argparse.ArgumentParser`.
        """
        parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=_argparse.SmartHelpFormatter,
            conflict_handler='ignore',
        )
        for hook in self._hooks:
            hook.obj.get_parser(parser)
        return parser

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Override to do something useful.

        The returned value will be returned by the program.
        """

    def run(self, parsed_args):
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

    def _run_before_hooks(self, parsed_args):
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

    def _run_after_hooks(self, parsed_args, return_code):
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
