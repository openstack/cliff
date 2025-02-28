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
import typing as ty

from cliff import _argparse
from cliff import command


class CommandHook(metaclass=abc.ABCMeta):
    """Base class for command hooks.

    Hook methods are executed in the following order:

    1. :meth:`get_epilog`
    2. :meth:`get_parser`
    3. :meth:`before`
    4. :meth:`after`

    :param command: Command instance being invoked
    """

    def __init__(self, command: command.Command):
        self.cmd = command

    @abc.abstractmethod
    def get_parser(
        self, parser: _argparse.ArgumentParser
    ) -> ty.Optional[_argparse.ArgumentParser]:
        """Modify the command :class:`argparse.ArgumentParser`.

        The provided parser is modified in-place, and the return value is not
        used.

        :param parser: An existing ArgumentParser instance to be modified.
        :returns: ArgumentParser or None
        """
        return parser

    @abc.abstractmethod
    def get_epilog(self) -> ty.Optional[str]:
        """Return text to add to the command help epilog.

        :returns: An epilog string or None.
        """
        return ''

    @abc.abstractmethod
    def before(self, parsed_args: argparse.Namespace) -> argparse.Namespace:
        """Called before the command's take_action() method.

        :param parsed_args: The arguments to the command.
        :returns: argparse.Namespace
        """
        return parsed_args

    @abc.abstractmethod
    def after(self, parsed_args: argparse.Namespace, return_code: int) -> int:
        """Called after the command's take_action() method.

        :param parsed_args: The arguments to the command.
        :param return_code: The value returned from take_action().
        :paramtype return_code: int
        :returns: int
        """
        return return_code
