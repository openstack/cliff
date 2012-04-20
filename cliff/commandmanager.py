"""Discover and lookup command plugins.
"""

import argparse
import logging

import pkg_resources


LOG = logging.getLogger(__name__)


class CommandManager(object):
    """Discovers commands and handles lookup based on argv data.
    """
    def __init__(self, namespace):
        self.commands = {}
        self.namespace = namespace
        self._load_commands()

    def _load_commands(self):
        for ep in pkg_resources.iter_entry_points(self.namespace):
            LOG.debug('found command %r', ep.name)
            self.commands[ep.name] = ep
        return

    def find_command(self, argv):
        """Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        orig_args = argv[:]
        name = ''
        while argv:
            if argv[0].startswith('-'):
                raise ValueError('Invalid command %r' % argv[0])
            next_val = argv.pop(0)
            name = '%s_%s' % (name, next_val) if name else next_val
            if name in self.commands:
                cmd_ep = self.commands[name]
                cmd_factory = cmd_ep.load()
                cmd = cmd_factory()
                return (cmd, argv)
        else:
            raise ValueError('Did not find command processor for %r' %
                             (orig_args,))
