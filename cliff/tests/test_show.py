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

import weakref

from cliff import show

import mock


class FauxFormatter(object):

    def __init__(self):
        self.args = []
        self.obj = weakref.proxy(self)

    def emit_one(self, columns, data, stdout, args):
        self.args.append((columns, data))


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


def test_formatter_args():
    app = mock.Mock()
    test_show = ExerciseShowOne(app, [])

    parsed_args = mock.Mock()
    parsed_args.columns = ('Col1', 'Col2')
    parsed_args.formatter = 'test'

    test_show.run(parsed_args)
    f = test_show._formatter_plugins['test']
    assert len(f.args) == 1
    args = f.args[0]
    assert args[0] == list(parsed_args.columns)
    data = list(args[1])
    assert data == [('a', 'A'), ('b', 'B')]


def test_dict2columns():
    app = mock.Mock()
    test_show = ExerciseShowOne(app, [])
    d = {'a': 'A', 'b': 'B', 'c': 'C'}
    expected = [('a', 'b', 'c'), ('A', 'B', 'C')]
    actual = list(test_show.dict2columns(d))
    assert expected == actual


def test_no_exist_column():
    test_show = ExerciseShowOne(mock.Mock(), [])
    parsed_args = mock.Mock()
    parsed_args.columns = ('no_exist_column',)
    parsed_args.formatter = 'test'
    with mock.patch.object(test_show, 'take_action') as mock_take_action:
        mock_take_action.return_value = (('Col1', 'Col2', 'Col3'), [])
        try:
            test_show.run(parsed_args)
        except ValueError:
            pass
        else:
            assert False, 'Should have had an exception'
