#!/usr/bin/env python
from six import StringIO

from cliff.formatters import shell

import mock


def test_shell_formatter():
    sf = shell.ShellFormatter()
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', '"escape me"')
    expected = 'a="A"\nb="B"\nd="\\"escape me\\""\n'
    output = StringIO()
    args = mock.Mock()
    args.variables = ['a', 'b', 'd']
    args.prefix = ''
    sf.emit_one(c, d, output, args)
    actual = output.getvalue()
    assert expected == actual
