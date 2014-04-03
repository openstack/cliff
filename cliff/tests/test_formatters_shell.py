#!/usr/bin/env python
from six import StringIO, text_type

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


def test_shell_formatter_with_non_string_values():
    sf = shell.ShellFormatter()
    c = ('a', 'b', 'c', 'd', 'e')
    d = (True, False, 100, '"esc"', text_type('"esc"'))
    expected = 'a="True"\nb="False"\nc="100"\nd="\\"esc\\""\ne="\\"esc\\""\n'
    output = StringIO()
    args = mock.Mock()
    args.variables = ['a', 'b', 'c', 'd', 'e']
    args.prefix = ''
    sf.emit_one(c, d, output, args)
    actual = output.getvalue()
    assert expected == actual
