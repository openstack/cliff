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

from cliff import _argparse
from cliff import command


class CommandHook(metaclass=abc.ABCMeta):
    """Base class for command hooks.

    :param app: Command instance being invoked
    :paramtype app: cliff.command.Command

    """

    def __init__(self, command: command.Command):
        self.cmd = command

    @abc.abstractmethod
    def get_parser(
        self, parser: _argparse.ArgumentParser
    ) -> _argparse.ArgumentParser:
        """Return an :class:`argparse.ArgumentParser`.

        :param parser: An existing ArgumentParser instance to be modified.
        :paramtype parser: ArgumentParser
        :returns: ArgumentParser
        """
        return parser

    @abc.abstractmethod
    def get_epilog(self) -> str:
        "Return text to add to the command help epilog."
        return ''

    @abc.abstractmethod
    def before(self, parsed_args: argparse.Namespace) -> argparse.Namespace:
        """Called before the command's take_action() method.

        :param parsed_args: The arguments to the command.
        :paramtype parsed_args: argparse.Namespace
        :returns: argparse.Namespace
        """
        return parsed_args

    @abc.abstractmethod
    def after(self, parsed_args: argparse.Namespace, return_code: int) -> int:
        """Called after the command's take_action() method.

        :param parsed_args: The arguments to the command.
        :paramtype parsed_args: argparse.Namespace
        :param return_code: The value returned from take_action().
        :paramtype return_code: int
        :returns: int
        """
        return return_code
