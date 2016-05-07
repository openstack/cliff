#!/usr/bin/env python

import mock
from six import StringIO
import os

from cliff.formatters import table


class args(object):
    def __init__(self, max_width=0):
        if max_width > 0:
            self.max_width = max_width
        else:
            # Envvar is only taken into account iff CLI parameter not given
            self.max_width = int(os.environ.get('CLIFF_MAX_TERM_WIDTH', 0))


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter(tw):
    tw.return_value = 80
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


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_cli_param(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    import argparse

    parser = argparse.ArgumentParser(description='Testing...')
    sf.add_argument_group(parser)
    parsed_args = parser.parse_args(['--max-width', '42'])
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    expected = '''\
+-------+--------------------------------+
| Field | Value                          |
+-------+--------------------------------+
| a     | A                              |
| b     | B                              |
| c     | C                              |
| d     | dddddddddddddddddddddddddddddd |
|       | dddddddddddddddddddddddddddddd |
|       | ddddddddddddddddd              |
+-------+--------------------------------+
'''
    output = StringIO()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '666'})
def test_table_formatter_cli_param_envvar_big(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    import argparse

    parser = argparse.ArgumentParser(description='Testing...')
    sf.add_argument_group(parser)
    parsed_args = parser.parse_args(['--max-width', '42'])
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    expected = '''\
+-------+--------------------------------+
| Field | Value                          |
+-------+--------------------------------+
| a     | A                              |
| b     | B                              |
| c     | C                              |
| d     | dddddddddddddddddddddddddddddd |
|       | dddddddddddddddddddddddddddddd |
|       | ddddddddddddddddd              |
+-------+--------------------------------+
'''
    output = StringIO()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '23'})
def test_table_formatter_cli_param_envvar_tiny(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    import argparse

    parser = argparse.ArgumentParser(description='Testing...')
    sf.add_argument_group(parser)
    parsed_args = parser.parse_args(['--max-width', '42'])
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    expected = '''\
+-------+--------------------------------+
| Field | Value                          |
+-------+--------------------------------+
| a     | A                              |
| b     | B                              |
| c     | C                              |
| d     | dddddddddddddddddddddddddddddd |
|       | dddddddddddddddddddddddddddddd |
|       | ddddddddddddddddd              |
+-------+--------------------------------+
'''
    output = StringIO()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_max_width(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    c = ('field_name', 'a_really_long_field_name')
    d = ('the value', 'a value significantly longer than the field')
    expected = '''\
+--------------------------+---------------------------------------------+
| Field                    | Value                                       |
+--------------------------+---------------------------------------------+
| field_name               | the value                                   |
| a_really_long_field_name | a value significantly longer than the field |
+--------------------------+---------------------------------------------+
'''
    output = StringIO()
    parsed_args = args()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize value column
    tw.return_value = 70
    expected = '''\
+--------------------------+-----------------------------------------+
| Field                    | Value                                   |
+--------------------------+-----------------------------------------+
| field_name               | the value                               |
| a_really_long_field_name | a value significantly longer than the   |
|                          | field                                   |
+--------------------------+-----------------------------------------+
'''
    output = StringIO()
    parsed_args = args()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize both columns
    tw.return_value = 50
    expected = '''\
+-----------------------+------------------------+
| Field                 | Value                  |
+-----------------------+------------------------+
| field_name            | the value              |
| a_really_long_field_n | a value significantly  |
| ame                   | longer than the field  |
+-----------------------+------------------------+
'''
    output = StringIO()
    parsed_args = args()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize all columns limited by min_width=16
    tw.return_value = 10
    expected = '''\
+------------------+------------------+
| Field            | Value            |
+------------------+------------------+
| field_name       | the value        |
| a_really_long_fi | a value          |
| eld_name         | significantly    |
|                  | longer than the  |
|                  | field            |
+------------------+------------------+
'''
    output = StringIO()
    parsed_args = args()
    sf.emit_one(c, d, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter(tw):
    tw.return_value = 80
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


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter_max_width(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # no resize
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize 1 column
    tw.return_value = 50
    expected = '''\
+----------------+-----------------+-------------+
| one            | two             | three       |
+----------------+-----------------+-------------+
| one one one    | two two two two | three three |
| one one        |                 |             |
+----------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 50

    # resize 2 columns
    tw.return_value = 45
    expected = '''\
+--------------+--------------+-------------+
| one          | two          | three       |
+--------------+--------------+-------------+
| one one one  | two two two  | three three |
| one one      | two          |             |
+--------------+--------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 45

    # resize all columns
    tw.return_value = 40
    expected = '''\
+------------+------------+------------+
| one        | two        | three      |
+------------+------------+------------+
| one one    | two two    | three      |
| one one    | two two    | three      |
| one        |            |            |
+------------+------------+------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 40

    # resize all columns limited by min_width=8
    tw.return_value = 10
    expected = '''\
+----------+----------+----------+
| one      | two      | three    |
+----------+----------+----------+
| one one  | two two  | three    |
| one one  | two two  | three    |
| one      |          |          |
+----------+----------+----------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    # 3 columns each 8 wide, plus table spacing and borders
    expected_width = 11 * 3 + 1
    assert len(actual.splitlines()[0]) == expected_width


# Force a wide terminal by overriding its width with envvar
@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '666'})
def test_table_list_formatter_max_width_and_envvar_max(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # no resize
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize 1 column
    tw.return_value = 50
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize 2 columns
    tw.return_value = 45
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize all columns
    tw.return_value = 40
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize all columns limited by min_width=8
    tw.return_value = 10
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


# Force a narrow terminal by overriding its width with envvar
@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '47'})
def test_table_list_formatter_max_width_and_envvar_mid(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # no resize
    expected = '''\
+---------------+---------------+-------------+
| one           | two           | three       |
+---------------+---------------+-------------+
| one one one   | two two two   | three three |
| one one       | two           |             |
+---------------+---------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual

    # resize 1 column
    tw.return_value = 50
    expected = '''\
+---------------+---------------+-------------+
| one           | two           | three       |
+---------------+---------------+-------------+
| one one one   | two two two   | three three |
| one one       | two           |             |
+---------------+---------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 47

    # resize 2 columns
    tw.return_value = 45
    expected = '''\
+---------------+---------------+-------------+
| one           | two           | three       |
+---------------+---------------+-------------+
| one one one   | two two two   | three three |
| one one       | two           |             |
+---------------+---------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 47

    # resize all columns
    tw.return_value = 40
    expected = '''\
+---------------+---------------+-------------+
| one           | two           | three       |
+---------------+---------------+-------------+
| one one one   | two two two   | three three |
| one one       | two           |             |
+---------------+---------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 47

    # resize all columns limited by min_width=8
    tw.return_value = 10
    expected = '''\
+---------------+---------------+-------------+
| one           | two           | three       |
+---------------+---------------+-------------+
| one one one   | two two two   | three three |
| one one       | two           |             |
+---------------+---------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 47


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '80'})
def test_table_list_formatter_env_maxwidth_noresize():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # no resize
    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '50'})
def test_table_list_formatter_env_maxwidth_resize_one():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # resize 1 column
    expected = '''\
+----------------+-----------------+-------------+
| one            | two             | three       |
+----------------+-----------------+-------------+
| one one one    | two two two two | three three |
| one one        |                 |             |
+----------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 50


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '45'})
def test_table_list_formatter_env_maxwidth_resize_two():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # resize 2 columns
    expected = '''\
+--------------+--------------+-------------+
| one          | two          | three       |
+--------------+--------------+-------------+
| one one one  | two two two  | three three |
| one one      | two          |             |
+--------------+--------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 45


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '40'})
def test_table_list_formatter_env_maxwidth_resize_all():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # resize all columns
    expected = '''\
+------------+------------+------------+
| one        | two        | three      |
+------------+------------+------------+
| one one    | two two    | three      |
| one one    | two two    | three      |
| one        |            |            |
+------------+------------+------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    assert len(actual.splitlines()[0]) == 40


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '8'})
def test_table_list_formatter_env_maxwidth_resize_all_tiny():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args()

    # resize all columns limited by min_width=8
    expected = '''\
+----------+----------+----------+
| one      | two      | three    |
+----------+----------+----------+
| one one  | two two  | three    |
| one one  | two two  | three    |
| one      |          |          |
+----------+----------+----------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual
    # 3 columns each 8 wide, plus table spacing and borders
    expected_width = 11 * 3 + 1
    assert len(actual.splitlines()[0]) == expected_width


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '42'})
def test_table_list_formatter_env_maxwidth_args_big():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args(666)

    expected = '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '42'})
def test_table_list_formatter_env_maxwidth_args_tiny():
    sf = table.TableFormatter()
    c = ('one', 'two', 'three')
    d1 = (
        'one one one one one',
        'two two two two',
        'three three')
    data = [d1]
    parsed_args = args(40)

    expected = '''\
+------------+------------+------------+
| one        | two        | three      |
+------------+------------+------------+
| one one    | two two    | three      |
| one one    | two two    | three      |
| one        |            |            |
+------------+------------+------------+
'''
    output = StringIO()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter_empty(tw):
    tw.return_value = 80
    sf = table.TableFormatter()
    c = ('a', 'b', 'c')
    data = []
    expected = '\n'
    output = StringIO()
    parsed_args = args()
    sf.emit_list(c, data, output, parsed_args)
    actual = output.getvalue()
    assert expected == actual


def test_field_widths():
    tf = table.TableFormatter
    assert {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 10
    } == tf._field_widths(
        ('a', 'b', 'c', 'd'),
        '+---+----+-----+------------+')


def test_field_widths_zero():
    tf = table.TableFormatter
    assert {
        'a': 0,
        'b': 0,
        'c': 0
    } == tf._field_widths(
        ('a', 'b', 'c'),
        '+--+-++')


def test_width_info():
    tf = table.TableFormatter
    assert (49, 4) == (tf._width_info(80, 10))
    assert (76, 76) == (tf._width_info(80, 1))
    assert (79, 0) == (tf._width_info(80, 0))
    assert (0, 0) == (tf._width_info(0, 80))
