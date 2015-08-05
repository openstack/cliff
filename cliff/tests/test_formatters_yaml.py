#!/usr/bin/env python
from six import StringIO
import yaml

from cliff.formatters import yaml_format

import mock


def test_yaml_format_one():
    sf = yaml_format.YAMLFormatter()
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', '"escape me"')
    expected = {
        'a': 'A',
        'b': 'B',
        'c': 'C',
        'd': '"escape me"'
    }
    output = StringIO()
    args = mock.Mock()
    sf.emit_one(c, d, output, args)
    actual = yaml.safe_load(output.getvalue())
    assert expected == actual


def test_yaml_format_list():
    sf = yaml_format.YAMLFormatter()
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
    output = StringIO()
    args = mock.Mock()
    sf.add_argument_group(args)
    sf.emit_list(c, d, output, args)
    actual = yaml.safe_load(output.getvalue())
    assert expected == actual
