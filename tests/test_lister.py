#!/usr/bin/env python

from cliff.command import Command
from cliff.commandmanager import CommandManager
from cliff.formatters.base import ListFormatter
from cliff.lister import Lister

import mock


class FauxFormatter(object):

    def __init__(self):
        self.args = []

    def emit_list(self, columns, data, stdout, args):
        self.args.append((columns, data))

class ExerciseLister(Lister):

	def load_formatter_plugins(self):
		self.formatters = {
			'test': FauxFormatter(),
			}
		return

	def take_action(self, parsed_args):
		return (
			parsed_args.columns,
			[('a', 'A'), ('b', 'B')],
			)


#    def run(self, parsed_args):
#        self.formatter = self.formatters[parsed_args.formatter]
#        column_names, data = self.take_action(parsed_args)
#        self.produce_output(parsed_args, column_names, data)
#        return 0

def test_formatter_args():
    app = mock.Mock()
    test_lister = ExerciseLister(app, [])

    parsed_args = mock.Mock()
    parsed_args.columns = ('Col1', 'Col2')
    parsed_args.formatter = 'test'

    test_lister.run(parsed_args)
    f = test_lister.formatters['test']
    assert len(f.args) == 1
    args = f.args[0]
    assert args[0] == list(parsed_args.columns)
    data = list(args[1])
    assert data == [['a', 'A'], ['b', 'B']]

