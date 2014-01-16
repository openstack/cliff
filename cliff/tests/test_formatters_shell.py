#!/usr/bin/env python
from six import StringIO

from cliff.formatters import shell

import mock


def test_shell_formatter():
    sf = shell.ShellFormatter()
    c = ('a', 'b', 'c')
    d = ('A', 'B', 'C')
    expected = 'a="A"\nb="B"\n'
    output = StringIO()
    args = mock.Mock()
    args.variables = ['a', 'b']
    args.prefix = ''
    sf.emit_one(c, d, output, args)
    actual = output.getvalue()
    assert expected == actual
