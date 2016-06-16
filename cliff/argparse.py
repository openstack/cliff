"""Special argparse module that allows to bypass abbrev mode."""

from __future__ import absolute_import
from argparse import *  # noqa
import sys


if sys.version_info < (3, 5):
    class ArgumentParser(ArgumentParser):  # noqa
        def __init__(self, *args, **kwargs):
            self.allow_abbrev = kwargs.pop("allow_abbrev", True)
            super(ArgumentParser, self).__init__(*args, **kwargs)

        def _get_option_tuples(self, option_string):
            if self.allow_abbrev:
                return super(ArgumentParser, self)._get_option_tuples(
                    option_string)
            return ()
