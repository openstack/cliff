#!/usr/bin/env python
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import mock
from six import StringIO
import os
import argparse

from cliff.formatters import table
from cliff.tests import test_columns


class args(object):
    def __init__(self, max_width=0):
        if max_width > 0:
            self.max_width = max_width
        else:
            # Envvar is only taken into account iff CLI parameter not given
            self.max_width = int(os.environ.get('CLIFF_MAX_TERM_WIDTH', 0))


def _table_tester_helper(tags, data, extra_args=None):
    """Get table output as a string, formatted according to
    CLI arguments, environment variables and terminal size

    tags - tuple of strings for data tags (column headers or fields)
    data - tuple of strings for single data row
         - list of tuples of strings for multiple rows of data
    extra_args - an instance of class args
               - a list of strings for CLI arguments
    """
    sf = table.TableFormatter()

    if extra_args is None:
        # Default to no CLI arguments
        parsed_args = args()
    elif type(extra_args) == args:
        # Use the given CLI arguments
        parsed_args = extra_args
    else:
        # Parse arguments as if passed on the command-line
        parser = argparse.ArgumentParser(description='Testing...')
        sf.add_argument_group(parser)
        parsed_args = parser.parse_args(extra_args)

    output = StringIO()
    emitter = sf.emit_list if type(data) is list else sf.emit_one
    emitter(tags, data, output, parsed_args)
    return output.getvalue()


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter(tw):
    tw.return_value = 80
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
    assert expected == _table_tester_helper(c, d)


# Multi-line output when width is restricted to 42 columns
expected_ml_val = '''\
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

# Multi-line output when width is restricted to 80 columns
expected_ml_80_val = '''\
+-------+----------------------------------------------------------------------+
| Field | Value                                                                |
+-------+----------------------------------------------------------------------+
| a     | A                                                                    |
| b     | B                                                                    |
| c     | C                                                                    |
| d     | dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd |
|       | ddddddddd                                                            |
+-------+----------------------------------------------------------------------+
'''  # noqa

# Single-line output, for when no line length restriction apply
expected_sl_val = '''\
+-------+-------------------------------------------------------------------------------+
| Field | Value                                                                         |
+-------+-------------------------------------------------------------------------------+
| a     | A                                                                             |
| b     | B                                                                             |
| c     | C                                                                             |
| d     | ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd |
+-------+-------------------------------------------------------------------------------+
'''  # noqa


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_no_cli_param(tw):
    tw.return_value = 80
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    assert expected_ml_80_val == _table_tester_helper(c, d, extra_args=args())


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_cli_param(tw):
    tw.return_value = 80
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    assert (expected_ml_val ==
            _table_tester_helper(c, d, extra_args=['--max-width', '42']))


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_no_cli_param_unlimited_tw(tw):
    tw.return_value = 0
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    # output should not be wrapped to multiple lines
    assert expected_sl_val == _table_tester_helper(c, d, extra_args=args())


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_cli_param_unlimited_tw(tw):
    tw.return_value = 0
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    assert (expected_ml_val ==
            _table_tester_helper(c, d, extra_args=['--max-width', '42']))


@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '666'})
def test_table_formatter_cli_param_envvar_big(tw):
    tw.return_value = 80
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    assert (expected_ml_val ==
            _table_tester_helper(c, d, extra_args=['--max-width', '42']))


@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '23'})
def test_table_formatter_cli_param_envvar_tiny(tw):
    tw.return_value = 80
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', 'd' * 77)
    assert (expected_ml_val ==
            _table_tester_helper(c, d, extra_args=['--max-width', '42']))


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_max_width(tw):
    tw.return_value = 80
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
    assert expected == _table_tester_helper(c, d)

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
    assert expected == _table_tester_helper(c, d)

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
    assert expected == _table_tester_helper(c, d)

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
    assert expected == _table_tester_helper(c, d)


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter(tw):
    tw.return_value = 80
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
    assert expected == _table_tester_helper(c, data)


@mock.patch('cliff.utils.terminal_width')
def test_table_formatter_formattable_column(tw):
    tw.return_value = 0
    c = ('a', 'b', 'c', 'd')
    d = ('A', 'B', 'C', test_columns.FauxColumn(['the', 'value']))
    expected = '''\
+-------+---------------------------------------------+
| Field | Value                                       |
+-------+---------------------------------------------+
| a     | A                                           |
| b     | B                                           |
| c     | C                                           |
| d     | I made this string myself: ['the', 'value'] |
+-------+---------------------------------------------+
'''
    assert expected == _table_tester_helper(c, d)


_col_names = ('one', 'two', 'three')
_col_data = [(
    'one one one one one',
    'two two two two',
    'three three')]

_expected_mv = {
    80: '''\
+---------------------+-----------------+-------------+
| one                 | two             | three       |
+---------------------+-----------------+-------------+
| one one one one one | two two two two | three three |
+---------------------+-----------------+-------------+
''',

    50: '''\
+----------------+-----------------+-------------+
| one            | two             | three       |
+----------------+-----------------+-------------+
| one one one    | two two two two | three three |
| one one        |                 |             |
+----------------+-----------------+-------------+
''',

    47: '''\
+---------------+---------------+-------------+
| one           | two           | three       |
+---------------+---------------+-------------+
| one one one   | two two two   | three three |
| one one       | two           |             |
+---------------+---------------+-------------+
''',

    45: '''\
+--------------+--------------+-------------+
| one          | two          | three       |
+--------------+--------------+-------------+
| one one one  | two two two  | three three |
| one one      | two          |             |
+--------------+--------------+-------------+
''',

    40: '''\
+------------+------------+------------+
| one        | two        | three      |
+------------+------------+------------+
| one one    | two two    | three      |
| one one    | two two    | three      |
| one        |            |            |
+------------+------------+------------+
''',

    10: '''\
+----------+----------+----------+
| one      | two      | three    |
+----------+----------+----------+
| one one  | two two  | three    |
| one one  | two two  | three    |
| one      |          |          |
+----------+----------+----------+
''',
}


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter_formattable_column(tw):
    tw.return_value = 80
    c = ('a', 'b', 'c')
    d1 = ('A', 'B', test_columns.FauxColumn(['the', 'value']))
    data = [d1]
    expected = '''\
+---+---+---------------------------------------------+
| a | b | c                                           |
+---+---+---------------------------------------------+
| A | B | I made this string myself: ['the', 'value'] |
+---+---+---------------------------------------------+
'''
    assert expected == _table_tester_helper(c, data)


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter_max_width(tw):
    # no resize
    l = tw.return_value = 80
    assert _expected_mv[l] == _table_tester_helper(_col_names, _col_data)

    # resize 1 column
    l = tw.return_value = 50
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[l] == actual
    assert len(actual.splitlines()[0]) == l

    # resize 2 columns
    l = tw.return_value = 45
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[l] == actual
    assert len(actual.splitlines()[0]) == l

    # resize all columns
    l = tw.return_value = 40
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[l] == actual
    assert len(actual.splitlines()[0]) == l

    # resize all columns limited by min_width=8
    l = tw.return_value = 10
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[l] == actual
    # 3 columns each 8 wide, plus table spacing and borders
    expected_width = 11 * 3 + 1
    assert len(actual.splitlines()[0]) == expected_width


# Force a wide terminal by overriding its width with envvar
@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '666'})
def test_table_list_formatter_max_width_and_envvar_max(tw):
    # no resize
    tw.return_value = 80
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data)

    # resize 1 column
    tw.return_value = 50
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data)

    # resize 2 columns
    tw.return_value = 45
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data)

    # resize all columns
    tw.return_value = 40
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data)

    # resize all columns limited by min_width=8
    tw.return_value = 10
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data)


# Force a narrow terminal by overriding its width with envvar
@mock.patch('cliff.utils.terminal_width')
@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '47'})
def test_table_list_formatter_max_width_and_envvar_mid(tw):
    # no resize
    tw.return_value = 80
    assert _expected_mv[47] == _table_tester_helper(_col_names, _col_data)

    # resize 1 column
    tw.return_value = 50
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[47] == actual
    assert len(actual.splitlines()[0]) == 47

    # resize 2 columns
    tw.return_value = 45
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[47] == actual
    assert len(actual.splitlines()[0]) == 47

    # resize all columns
    tw.return_value = 40
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[47] == actual
    assert len(actual.splitlines()[0]) == 47

    # resize all columns limited by min_width=8
    tw.return_value = 10
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[47] == actual
    assert len(actual.splitlines()[0]) == 47


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '80'})
def test_table_list_formatter_env_maxwidth_noresize():
    # no resize
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data)


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '50'})
def test_table_list_formatter_env_maxwidth_resize_one():
    # resize 1 column
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[50] == actual
    assert len(actual.splitlines()[0]) == 50


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '45'})
def test_table_list_formatter_env_maxwidth_resize_two():
    # resize 2 columns
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[45] == actual
    assert len(actual.splitlines()[0]) == 45


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '40'})
def test_table_list_formatter_env_maxwidth_resize_all():
    # resize all columns
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[40] == actual
    assert len(actual.splitlines()[0]) == 40


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '8'})
def test_table_list_formatter_env_maxwidth_resize_all_tiny():
    # resize all columns limited by min_width=8
    actual = _table_tester_helper(_col_names, _col_data)
    assert _expected_mv[10] == actual
    # 3 columns each 8 wide, plus table spacing and borders
    expected_width = 11 * 3 + 1
    assert len(actual.splitlines()[0]) == expected_width


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '42'})
def test_table_list_formatter_env_maxwidth_args_big():
    assert _expected_mv[80] == _table_tester_helper(_col_names, _col_data,
                                                    extra_args=args(666))


@mock.patch.dict(os.environ, {'CLIFF_MAX_TERM_WIDTH': '42'})
def test_table_list_formatter_env_maxwidth_args_tiny():
    assert _expected_mv[40] == _table_tester_helper(_col_names, _col_data,
                                                    extra_args=args(40))


@mock.patch('cliff.utils.terminal_width')
def test_table_list_formatter_empty(tw):
    tw.return_value = 80
    c = ('a', 'b', 'c')
    data = []
    expected = '\n'
    assert expected == _table_tester_helper(c, data)


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
