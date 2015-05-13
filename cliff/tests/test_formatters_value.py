#!/usr/bin/env python
from six import StringIO

from cliff.formatters import value


def test_value_formatter():
    sf = value.ValueFormatter()
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', '"no escape me"')
    expected = 'A\nB\nC\n"no escape me"\n'
    output = StringIO()
    sf.emit_one(c, d, output, None)
    actual = output.getvalue()
    assert expected == actual


def test_value_list_formatter():
    sf = value.ValueFormatter()
    c = ('a', 'b', 'c')
    d1 = ('A', 'B', 'C')
    d2 = ('D', 'E', 'F')
    data = [d1, d2]
    expected = 'A B C\nD E F\n'
    output = StringIO()
    sf.emit_list(c, data, output, None)
    actual = output.getvalue()
    assert expected == actual
