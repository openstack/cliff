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

import typing as ty
import unittest

from cliff import columns


class FauxColumn(columns.FormattableColumn[ty.Union[str, list[str]]]):
    def human_readable(self):
        return f'I made this string myself: {self._value}'


class TestColumns(unittest.TestCase):
    def test_machine_readable(self):
        c = FauxColumn(['list', 'of', 'values'])
        self.assertEqual(['list', 'of', 'values'], c.machine_readable())

    def test_human_readable(self):
        c = FauxColumn(['list', 'of', 'values'])
        self.assertEqual(
            "I made this string myself: ['list', 'of', 'values']",
            c.human_readable(),
        )

    def test_str(self):
        c = FauxColumn(['list', 'of', 'values'])
        self.assertEqual(
            "I made this string myself: ['list', 'of', 'values']",
            str(c),
        )

    def test_repr(self):
        c = FauxColumn(['list', 'of', 'values'])
        self.assertEqual(
            "FauxColumn(['list', 'of', 'values'])",
            repr(c),
        )

    def test_sorting(self):
        cols = [
            FauxColumn('foo'),
            FauxColumn('bar'),
            FauxColumn('baz'),
            FauxColumn('foo'),
        ]
        cols.sort()
        self.assertEqual(
            ['bar', 'baz', 'foo', 'foo'],
            [c.machine_readable() for c in cols],
        )
