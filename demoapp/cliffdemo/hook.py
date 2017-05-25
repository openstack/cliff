# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from cliff.command import Command
from cliff.hooks import CommandHook


class Hooked(Command):
    "A command to demonstrate how the hooks work"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.app.stdout.write('this command has an extension\n')


class Hook(CommandHook):
    """Hook sample for the 'hooked' command.

    This would normally be provided by a separate package from the
    main application, but is included in the demo app for simplicity.

    """

    def get_parser(self, parser):
        print('sample hook get_parser()')
        parser.add_argument('--added-by-hook')
        return parser

    def get_epilog(self):
        return 'extension epilog text'

    def before(self, parsed_args):
        self.cmd.app.stdout.write('before\n')

    def after(self, parsed_args, return_code):
        self.cmd.app.stdout.write('after\n')
