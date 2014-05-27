#!/usr/bin/env python

import weakref

from cliff.show import ShowOne

import mock


class FauxFormatter(object):

    def __init__(self):
        self.args = []
        self.obj = weakref.proxy(self)

    def emit_one(self, columns, data, stdout, args):
        self.args.append((columns, data))


class ExerciseShowOne(ShowOne):

    def _load_formatter_plugins(self):
        return {
            'test': FauxFormatter(),
        }
        return

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
