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

import argparse
import weakref

from unittest import mock

from cliff.formatters import base as base_formatters
from cliff import show
from cliff.tests import base


class FauxFormatter(base_formatters.SingleFormatter):
    def __init__(self):
        self.args = []
        self.obj = weakref.proxy(self)

    def add_argument_group(self, parser: argparse.ArgumentParser) -> None:
        return None

    def emit_one(self, columns, data, stdout, args):
        self.args.append((columns, data, stdout, args))


class ExerciseShowOne(show.ShowOne):
    def _load_formatter_plugins(self):
        return {
            'test': FauxFormatter(),
        }

    def take_action(self, parsed_args):
        return (
            parsed_args.columns,
            [('a', 'A'), ('b', 'B')],
        )


class TestShow(base.TestBase):
    def test_formatter_args(self):
        app = mock.Mock()
        test_show = ExerciseShowOne(app, None)

        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'

        test_show.run(parsed_args)
        f = test_show._formatter_plugins['test']
        assert isinstance(f, FauxFormatter)
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(list(parsed_args.columns), args[0])
        data = list(args[1])
        self.assertEqual([('a', 'A'), ('b', 'B')], data)
        self.assertIs(app.stdout, args[2])
        self.assertIs(parsed_args, args[3])

    def test_select_fields(self):
        test_show = ExerciseShowOne(mock.Mock(), None)
        parsed_args = mock.Mock()
        parsed_args.columns = ('STATUS', ' RESOURCE_NAME ')
        parsed_args.formatter = 'test'
        with mock.patch.object(test_show, 'take_action') as mock_take_action:
            mock_take_action.return_value = (
                ('Resource Name', 'Status', 'Region'),
                ('demo', 'ACTIVE', 'RegionOne'),
            )
            test_show.run(parsed_args)

        f = test_show._formatter_plugins['test']
        assert isinstance(f, FauxFormatter)
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(['Resource Name', 'Status'], args[0])
        self.assertEqual(['demo', 'ACTIVE'], list(args[1]))

    def test_dict2columns(self):
        app = mock.Mock()
        test_show = ExerciseShowOne(app, None)
        d = {'a': 'A', 'b': 'B', 'c': 'C'}
        expected = [('a', 'b', 'c'), ('A', 'B', 'C')]
        actual = list(test_show.dict2columns(d))
        self.assertEqual(expected, actual)

    def test_no_exist_column(self):
        test_show = ExerciseShowOne(mock.Mock(), None)
        parsed_args = mock.Mock()
        parsed_args.columns = ('no_exist_column',)
        parsed_args.formatter = 'test'
        with mock.patch.object(test_show, 'take_action') as mock_take_action:
            mock_take_action.return_value = (('Col1', 'Col2', 'Col3'), [])
            with self.assertRaises(ValueError):
                test_show.run(parsed_args)


class FauxListFormatter(base_formatters.ListFormatter):
    def __init__(self):
        self.args = []
        self.obj = weakref.proxy(self)

    def add_argument_group(self, parser: argparse.ArgumentParser) -> None:
        return None

    def emit_list(self, columns, data, stdout, args):
        self.args.append((columns, data, stdout, args))


class ExerciseShowOneWithDetails(show.ShowOneWithDetails):
    columns: tuple[str, ...] = ('Field', 'Value', 'Description')
    data: list[tuple[str, ...]] = [
        ('Resource Name', 'demo', 'Resource name'),
        ('Status', 'ACTIVE', 'Current resource status'),
        ('Region', 'RegionOne', 'Resource region'),
    ]

    def _load_formatter_plugins(self):
        return {
            'test': FauxListFormatter(),
        }

    def take_action(self, parsed_args):
        return (self.columns, iter(self.data))


class TestShowOneWithDetails(base.TestBase):
    def setUp(self):
        super().setUp()
        self.app = mock.Mock()
        self.cmd = ExerciseShowOneWithDetails(self.app, None)
        self.parsed_args = mock.Mock()
        self.parsed_args.columns = []
        self.parsed_args.formatter = 'test'

    def test_formatter_configuration(self):
        self.assertEqual('cliff.formatter.list', self.cmd.formatter_namespace)
        self.assertEqual('table', self.cmd.formatter_default)

    def test_formatter_args(self):
        self.cmd.run(self.parsed_args)

        f = self.cmd._formatter_plugins['test']
        assert isinstance(f, FauxListFormatter)
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(self.cmd.columns, args[0])
        self.assertEqual(self.cmd.data, list(args[1]))
        self.assertIs(self.app.stdout, args[2])
        self.assertIs(self.parsed_args, args[3])

    def test_select_fields(self):
        self.parsed_args.columns = ('STATUS', ' RESOURCE_NAME ')
        self.cmd.run(self.parsed_args)

        f = self.cmd._formatter_plugins['test']
        assert isinstance(f, FauxListFormatter)
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(self.cmd.columns, args[0])
        self.assertEqual(self.cmd.data[:2], list(args[1]))

    def test_cannot_select_output_column(self):
        self.parsed_args.columns = ('Description',)
        with self.assertRaisesRegex(ValueError, 'No recognized column names'):
            self.cmd.run(self.parsed_args)

    def test_empty_data(self):
        self.cmd.data = []
        self.cmd.run(self.parsed_args)

        f = self.cmd._formatter_plugins['test']
        assert isinstance(f, FauxListFormatter)
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(self.cmd.columns, args[0])
        self.assertEqual([], list(args[1]))

    def test_empty_data_with_selection(self):
        self.cmd.data = []
        self.parsed_args.columns = ('Status',)
        with self.assertRaisesRegex(ValueError, 'No recognized column names'):
            self.cmd.run(self.parsed_args)

    def test_additional_columns(self):
        self.cmd.columns = (*self.cmd.columns, 'Source')
        self.cmd.data = [(*row, 'API') for row in self.cmd.data]
        self.parsed_args.columns = ('Status',)
        self.cmd.run(self.parsed_args)

        f = self.cmd._formatter_plugins['test']
        assert isinstance(f, FauxListFormatter)
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(self.cmd.columns, args[0])
        self.assertEqual([self.cmd.data[1]], list(args[1]))
