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

"""Special argparse module that allows to bypass abbrev mode."""

from __future__ import absolute_import
from argparse import *  # noqa
import argparse
import sys
import warnings


class ArgumentParser(argparse.ArgumentParser):

    if sys.version_info < (3, 5):
        def __init__(self, *args, **kwargs):
            self.allow_abbrev = kwargs.pop("allow_abbrev", True)
            super(ArgumentParser, self).__init__(*args, **kwargs)

        def _get_option_tuples(self, option_string):
            if self.allow_abbrev:
                return super(ArgumentParser, self)._get_option_tuples(
                    option_string)
            return ()

    # NOTE(dhellmann): We have to override the methods for creating
    # groups to return our objects that know how to deal with the
    # special conflict handler.

    def add_argument_group(self, *args, **kwargs):
        group = _ArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        return group

    def add_mutually_exclusive_group(self, **kwargs):
        group = _MutuallyExclusiveGroup(self, **kwargs)
        self._mutually_exclusive_groups.append(group)
        return group

    def _handle_conflict_ignore(self, action, conflicting_actions):
        _handle_conflict_ignore(
            self,
            self._option_string_actions,
            action,
            conflicting_actions,
        )


def _handle_conflict_ignore(container, option_string_actions,
                            new_action, conflicting_actions):

    # Remember the option strings the new action starts with so we can
    # restore them as part of error reporting if we need to.
    original_option_strings = new_action.option_strings

    # Remove all of the conflicting option strings from the new action
    # and report an error if none are left at the end.
    for option_string, action in conflicting_actions:

        # remove the conflicting option from the new action
        new_action.option_strings.remove(option_string)
        warnings.warn(
            ('Ignoring option string {} for new action '
             'because it conflicts with an existing option.').format(
                 option_string))

        # if the option now has no option string, remove it from the
        # container holding it
        if not new_action.option_strings:
            new_action.option_strings = original_option_strings
            raise argparse.ArgumentError(
                new_action,
                ('Cannot resolve conflicting option string, '
                 'all names conflict.'),
            )


class _ArgumentGroup(argparse._ArgumentGroup):

    def _handle_conflict_ignore(self, action, conflicting_actions):
        _handle_conflict_ignore(
            self,
            self._option_string_actions,
            action,
            conflicting_actions,
        )


class _MutuallyExclusiveGroup(argparse._MutuallyExclusiveGroup):

    def _handle_conflict_ignore(self, action, conflicting_actions):
        _handle_conflict_ignore(
            self,
            self._option_string_actions,
            action,
            conflicting_actions,
        )
