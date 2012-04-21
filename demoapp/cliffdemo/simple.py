
from cliff.command import Command


class Simple(Command):
    "A simple command that prints a message."

    def run(self, parsed_args):
        print 'hi!'
