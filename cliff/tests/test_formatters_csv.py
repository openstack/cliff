#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock

import six

from cliff.formatters import commaseparated


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
