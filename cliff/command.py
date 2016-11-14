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

from cliff import argparse


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    """Base class for command plugins.

    :param app: Application instance invoking the command.
    :paramtype app: cliff.app.App

    """

    deprecated = False

    _description = ''

    def __init__(self, app, app_args, cmd_name=None):
        self.app = app
        self.app_args = app_args
        self.cmd_name = cmd_name
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

    def get_parser(self, prog_name):
        """Return an :class:`argparse.ArgumentParser`.
        """
        parser = argparse.ArgumentParser(
            description=self.get_description(),
            prog=prog_name,
        )
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
        return self.take_action(parsed_args) or 0
