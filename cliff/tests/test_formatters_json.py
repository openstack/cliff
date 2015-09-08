#!/usr/bin/env python
from six import StringIO
import json

from cliff.formatters import json_format

import mock


def test_json_format_one():
    sf = json_format.JSONFormatter()
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', '"escape me"')
    expected = {
        'a': 'A',
        'b': 'B',
        'c': 'C',
        'd': '"escape me"'
    }
    args = mock.Mock()
    sf.add_argument_group(args)

    args.noindent = True
    output = StringIO()
    sf.emit_one(c, d, output, args)
    value = output.getvalue()
    print(len(value.splitlines()))
    assert 1 == len(value.splitlines())
    actual = json.loads(value)
    assert expected == actual

    args.noindent = False
    output = StringIO()
    sf.emit_one(c, d, output, args)
    value = output.getvalue()
    assert 6 == len(value.splitlines())
    actual = json.loads(value)
    assert expected == actual


def test_json_format_list():
    sf = json_format.JSONFormatter()
    c = ('a', 'b', 'c')
    d = (
        ('A1', 'B1', 'C1'),
        ('A2', 'B2', 'C2'),
        ('A3', 'B3', 'C3')
    )
    expected = [
        {'a': 'A1', 'b': 'B1', 'c': 'C1'},
        {'a': 'A2', 'b': 'B2', 'c': 'C2'},
        {'a': 'A3', 'b': 'B3', 'c': 'C3'}
    ]
    args = mock.Mock()
    sf.add_argument_group(args)

    args.noindent = True
    output = StringIO()
    sf.emit_list(c, d, output, args)
    value = output.getvalue()
    assert 1 == len(value.splitlines())
    actual = json.loads(value)
    assert expected == actual

    args.noindent = False
    output = StringIO()
    sf.emit_list(c, d, output, args)
    value = output.getvalue()
    assert 17 == len(value.splitlines())
    actual = json.loads(value)
    assert expected == actual
