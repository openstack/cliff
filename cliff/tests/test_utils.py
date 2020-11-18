#!/usr/bin/env python
#
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

import os
import sys
from unittest import mock

from cliff.tests import base
from cliff import utils


class TestTerminalWidth(base.TestBase):

    def test(self):
        width = utils.terminal_width(sys.stdout)
        # Results are specific to the execution environment, so only assert
        # that no error is raised.
        if width is not None:
            self.assertIsInstance(width, int)

    @mock.patch('cliff.utils.os')
    def test_get_terminal_size(self, mock_os):
        ts = os.terminal_size((10, 5))
        mock_os.get_terminal_size.return_value = ts
        width = utils.terminal_width(sys.stdout)
        self.assertEqual(10, width)
        mock_os.get_terminal_size.side_effect = OSError()
        width = utils.terminal_width(sys.stdout)
        self.assertIs(None, width)
