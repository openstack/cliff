
from cliff.command import Command


class Simple(Command):

    def run(self, parsed_args):
        print 'hi!'
