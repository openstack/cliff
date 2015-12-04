#!/usr/bin/env python

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


@mock.patch('cliff.utils.ioctl')
def test_utils_terminal_width_ioctl(mock_ioctl):
    if hasattr(os, 'get_terminal_size'):
        raise nose.SkipTest('only needed for python 3.2 and before')
    mock_ioctl.return_value = struct.pack('hhhh', 57, 101, 0, 0)
    width = utils.terminal_width(sys.stdout)
    assert width == 101

    mock_ioctl.side_effect = IOError()
    width = utils.terminal_width(sys.stdout)
    assert width is None
