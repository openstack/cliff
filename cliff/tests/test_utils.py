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
import struct
import sys

import mock
import nose

from cliff import utils


def test_utils_terminal_width():
    width = utils.terminal_width(sys.stdout)
    # Results are specific to the execution environment, so only assert
    # that no error is raised.
    assert width is None or isinstance(width, int)


@mock.patch('cliff.utils.os')
def test_utils_terminal_width_get_terminal_size(mock_os):
    if not hasattr(os, 'get_terminal_size'):
        raise nose.SkipTest('only needed for python 3.3 onwards')
    ts = os.terminal_size((10, 5))
    mock_os.get_terminal_size.return_value = ts
    width = utils.terminal_width(sys.stdout)
    assert width == 10

    mock_os.get_terminal_size.side_effect = OSError()
    width = utils.terminal_width(sys.stdout)
    assert width is None


@mock.patch('fcntl.ioctl')
def test_utils_terminal_width_ioctl(mock_ioctl):
    if hasattr(os, 'get_terminal_size'):
        raise nose.SkipTest('only needed for python 3.2 and before')
    mock_ioctl.return_value = struct.pack('hhhh', 57, 101, 0, 0)
    width = utils.terminal_width(sys.stdout)
    assert width == 101

    mock_ioctl.side_effect = IOError()
    width = utils.terminal_width(sys.stdout)
    assert width is None


@mock.patch('cliff.utils.ctypes')
@mock.patch('sys.platform', 'win32')
def test_utils_terminal_width_windows(mock_ctypes):
    if hasattr(os, 'get_terminal_size'):
        raise nose.SkipTest('only needed for python 3.2 and before')

    mock_ctypes.create_string_buffer.return_value.raw = struct.pack(
        'hhhhHhhhhhh', 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    mock_ctypes.windll.kernel32.GetStdHandle.return_value = -11
    mock_ctypes.windll.kernel32.GetConsoleScreenBufferInfo.return_value = 1

    width = utils.terminal_width(sys.stdout)
    assert width == 101

    mock_ctypes.windll.kernel32.GetConsoleScreenBufferInfo.return_value = 0

    width = utils.terminal_width(sys.stdout)
    assert width is None

    width = utils.terminal_width('foo')
    assert width is None
