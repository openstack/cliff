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

import weakref

from unittest import mock

from cliff import lister
from cliff.tests import base


class FauxFormatter:
    def __init__(self):
        self.args = []
        self.obj = weakref.proxy(self)

    def emit_list(self, columns, data, stdout, args):
        self.args.append((columns, data))


class ExerciseLister(lister.Lister):
    data = [('a', 'A'), ('b', 'B'), ('c', 'A')]

    def _load_formatter_plugins(self):
        return {
            'test': FauxFormatter(),
        }

    def take_action(self, parsed_args):
        return (parsed_args.columns, self.data)


class ExerciseListerCustomSort(ExerciseLister):
    need_sort_by_cliff = False


class ExerciseListerNullValues(ExerciseLister):
    data = ExerciseLister.data + [(None, None)]


class ExerciseListerDifferentTypes(ExerciseLister):
    data = ExerciseLister.data + [(1, 0)]


class TestLister(base.TestBase):
    def test_formatter_args(self):
        app = mock.Mock()
        test_lister = ExerciseLister(app, [])

        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = []

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        self.assertEqual(1, len(f.args))
        args = f.args[0]
        self.assertEqual(list(parsed_args.columns), args[0])
        data = list(args[1])
        self.assertEqual([['a', 'A'], ['b', 'B'], ['c', 'A']], data)

    def test_filter_by_columns_invalid(self):
        test_lister = ExerciseLister(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('no_exist_column',)
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = []
        with mock.patch.object(test_lister, 'take_action') as mock_take_action:
            mock_take_action.return_value = (('Col1', 'Col2', 'Col3'), [])
            self.assertRaises(
                ValueError,
                test_lister.run,
                parsed_args,
            )

    def test_filter_by_columns_normalized(self):
        test_lister = ExerciseLister(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('col1', 'COL2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = []

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual([['a', 'A'], ['b', 'B'], ['c', 'A']], data)

    def test_sort_by_column_cliff_side_procedure(self):
        test_lister = ExerciseLister(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['Col2', 'Col1']

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual([['a', 'A'], ['c', 'A'], ['b', 'B']], data)

    def test_sort_by_column_reverse_order(self):
        test_lister = ExerciseLister(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['Col2', 'Col1']
        parsed_args.sort_direction = 'desc'

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual([['b', 'B'], ['c', 'A'], ['a', 'A']], data)

    def test_sort_by_column_data_already_sorted(self):
        test_lister = ExerciseListerCustomSort(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['Col2', 'Col1']

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual([['a', 'A'], ['b', 'B'], ['c', 'A']], data)

    def test_sort_by_column_with_null(self):
        test_lister = ExerciseListerNullValues(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['Col2', 'Col1']

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual(
            [['a', 'A'], ['c', 'A'], ['b', 'B'], [None, None]], data
        )

    def test_sort_by_column_with_different_types(self):
        test_lister = ExerciseListerDifferentTypes(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['Col2', 'Col1']

        with mock.patch.object(lister.Lister, 'log') as mock_log:
            test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        # The output should be unchanged
        self.assertEqual([['a', 'A'], ['b', 'B'], ['c', 'A'], [1, 0]], data)
        # but we should have logged a warning
        mock_log.warning.assert_has_calls(
            [
                mock.call(
                    "Could not sort on field '%s'; unsortable types", col
                )
                for col in parsed_args.sort_columns
            ]
        )

    def test_sort_by_non_displayed_column(self):
        test_lister = ExerciseLister(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1',)
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['Col2']

        with mock.patch.object(test_lister, 'take_action') as mock_take_action:
            mock_take_action.return_value = (
                ('Col1', 'Col2'),
                [['a', 'A'], ['b', 'B'], ['c', 'A']],
            )
            test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual([['a'], ['c'], ['b']], data)

    def test_sort_by_non_existing_column(self):
        test_lister = ExerciseLister(mock.Mock(), [])
        parsed_args = mock.Mock()
        parsed_args.columns = ('Col1', 'Col2')
        parsed_args.formatter = 'test'
        parsed_args.sort_columns = ['no_exist_column']

        test_lister.run(parsed_args)

        f = test_lister._formatter_plugins['test']
        args = f.args[0]
        data = list(args[1])
        self.assertEqual([['a', 'A'], ['b', 'B'], ['c', 'A']], data)
