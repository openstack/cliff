#!/usr/bin/env python
from six import StringIO

from cliff.formatters import table


class args(object):
    def __init__(self, max_width=0):
        self.max_width = max_width


def test_table_formatter():
    sf = table.TableFormatter()
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'test\rcarriage\r\nreturn')
    expected = '''\
+-------+---------------+
| Field | Value         |
+-------+---------------+
| a     | A             |
| b     | B             |
| c     | C             |
| d     | test carriage |
|       | return        |
+-------+---------------+
'''
    output = StringIO()
    parsed_args = args()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


def test_table_list_formatter():
    sf = table.TableFormatter()
    c = ('a', 'b', 'c')
    d1 = ('A', 'B', 'C')
    d2 = ('D', 'E', 'test\rcarriage\r\nreturn')
    data = [d1, d2]
    expected = '''\
+---+---+---------------+
| a | b | c             |
+---+---+---------------+
| A | B | C             |
| D | E | test carriage |
|   |   | return        |
+---+---+---------------+
'''
    output = StringIO()
    parsed_args = args()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
