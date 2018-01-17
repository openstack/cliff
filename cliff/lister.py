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

"""Application base class for providing a list of data as output.
"""
import abc
import operator
import six

from . import display


@six.add_metaclass(abc.ABCMeta)
class Lister(display.DisplayCommandBase):
    """Command base class for providing a list of data as output.
    """

    @property
    def formatter_namespace(self):
        return 'cliff.formatter.list'

    @property
    def formatter_default(self):
        return 'table'

    @property
    def need_sort_by_cliff(self):
        """Whether sort procedure is performed by cliff itself.

        Should be overridden (return False) when there is a need to implement
        custom sorting procedure or data is already sorted."""
        return True

    @abc.abstractmethod
    def take_action(self, parsed_args):
        """Return a tuple containing the column names and an iterable
        containing the data to be listed.
        """

    def get_parser(self, prog_name):
        parser = super(Lister, self).get_parser(prog_name)
        group = self._formatter_group
        group.add_argument(
            '--sort-column',
            action='append',
            default=[],
            dest='sort_columns',
            metavar='SORT_COLUMN',
            help=("specify the column(s) to sort the data (columns specified "
                  "first have a priority, non-existing columns are ignored), "
                  "can be repeated")
        )
        return parser

    def produce_output(self, parsed_args, column_names, data):
        if parsed_args.sort_columns and self.need_sort_by_cliff:
            indexes = [column_names.index(c) for c in parsed_args.sort_columns
                       if c in column_names]
            if indexes:
                data = sorted(data, key=operator.itemgetter(*indexes))
        (columns_to_include, selector) = self._generate_columns_and_selector(
            parsed_args, column_names)
        if selector:
            # Generator expression to only return the parts of a row
            # of data that the user has expressed interest in
            # seeing. We have to convert the compress() output to a
            # list so the table formatter can ask for its length.
            data = (list(self._compress_iterable(row, selector))
                    for row in data)
        self.formatter.emit_list(columns_to_include,
                                 data,
                                 self.app.stdout,
                                 parsed_args,
                                 )
        return 0
