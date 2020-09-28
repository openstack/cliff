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

"""Overrides of standard argparse behavior."""

import argparse
import warnings


class _ArgumentContainerMixIn(object):

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


class ArgumentParser(_ArgumentContainerMixIn, argparse.ArgumentParser):

    pass


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


class _ArgumentGroup(_ArgumentContainerMixIn, argparse._ArgumentGroup):
    pass


class _MutuallyExclusiveGroup(_ArgumentContainerMixIn,
                              argparse._MutuallyExclusiveGroup):
    pass


class SmartHelpFormatter(argparse.HelpFormatter):
    """Smart help formatter to output raw help message if help contain \n.

    Some command help messages maybe have multiple line content, the built-in
    argparse.HelpFormatter wrap and split the content according to width, and
    ignore \n in the raw help message, it merge multiple line content in one
    line to output, that looks messy. SmartHelpFormatter keep the raw help
    message format if it contain \n, and wrap long line like HelpFormatter
    behavior.
    """

    def _split_lines(self, text, width):
        lines = text.splitlines() if '\n' in text else [text]
        wrap_lines = []
        for each_line in lines:
            wrap_lines.extend(
                super(SmartHelpFormatter, self)._split_lines(each_line, width)
            )
        return wrap_lines
