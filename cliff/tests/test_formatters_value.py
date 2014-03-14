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
