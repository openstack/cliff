import logging

from cliff.command import Command


class Simple(Command):
    "A simple command that prints a message."

    log = logging.getLogger(__name__)

    def run(self, parsed_args):
        self.log.debug('debugging')
        self.log.info('hi!')
