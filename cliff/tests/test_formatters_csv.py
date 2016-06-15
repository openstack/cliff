#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mock
import argparse
import six

from cliff.formatters import commaseparated
from cliff.tests import test_columns


def test_commaseparated_list_formatter():
    sf = commaseparated.CSVLister()
    c = ('a', 'b', 'c')
    d1 = ('A', 'B', 'C')
    d2 = ('D', 'E', 'F')
    data = [d1, d2]
    expected = 'a,b,c\nA,B,C\nD,E,F\n'
    output = six.StringIO()
    parsed_args = mock.Mock()
    parsed_args.quote_mode = 'none'
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


def test_commaseparated_list_formatter_quoted():
    sf = commaseparated.CSVLister()
    c = ('a', 'b', 'c')
    d1 = ('A', 'B', 'C')
    d2 = ('D', 'E', 'F')
    data = [d1, d2]
    expected = '"a","b","c"\n"A","B","C"\n"D","E","F"\n'
    output = six.StringIO()
    # Parse arguments as if passed on the command-line
    parser = argparse.ArgumentParser(description='Testing...')
    sf.add_argument_group(parser)
    parsed_args = parser.parse_args(['--quote', 'all'])
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


def test_commaseparated_list_formatter_formattable_column():
    sf = commaseparated.CSVLister()
    c = ('a', 'b', 'c')
    d1 = ('A', 'B', test_columns.FauxColumn(['the', 'value']))
    data = [d1]
    expected = 'a,b,c\nA,B,[\'the\'\\, \'value\']\n'
    output = six.StringIO()
    parsed_args = mock.Mock()
    parsed_args.quote_mode = 'none'
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


def test_commaseparated_list_formatter_unicode():
    sf = commaseparated.CSVLister()
    c = (u'a', u'b', u'c')
    d1 = (u'A', u'B', u'C')
    happy = u'高兴'
    d2 = (u'D', u'E', happy)
    data = [d1, d2]
    expected = u'a,b,c\nA,B,C\nD,E,%s\n' % happy
    output = six.StringIO()
    parsed_args = mock.Mock()
    parsed_args.quote_mode = 'none'
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    if six.PY2:
        actual = actual.decode('utf-8')
    assert expected == actual
