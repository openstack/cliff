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

from io import StringIO
import yaml

from unittest import mock

from cliff.formatters import yaml_format
from cliff.tests import base
from cliff.tests import test_columns


class _toDict:
    def __init__(self, **kwargs):
        self._data = kwargs

    def toDict(self):
        return self._data


class _to_Dict:
    def __init__(self, **kwargs):
        self._data = kwargs

    def to_dict(self):
        return self._data


class TestYAMLFormatter(base.TestBase):
    def test_format_one(self):
        sf = yaml_format.YAMLFormatter()
        c = ('a', 'b', 'c', 'd')
        d = ('A', 'B', 'C', '"escape me"')
        expected = {'a': 'A', 'b': 'B', 'c': 'C', 'd': '"escape me"'}
        output = StringIO()
        args = mock.Mock()
        sf.emit_one(c, d, output, args)
        actual = yaml.safe_load(output.getvalue())
        self.assertEqual(expected, actual)

    def test_formattablecolumn_one(self):
        sf = yaml_format.YAMLFormatter()
        c = ('a', 'b', 'c', 'd')
        d = ('A', 'B', 'C', test_columns.FauxColumn(['the', 'value']))
        expected = {
            'a': 'A',
            'b': 'B',
            'c': 'C',
            'd': ['the', 'value'],
        }
        args = mock.Mock()
        sf.add_argument_group(args)

        args.noindent = True
        output = StringIO()
        sf.emit_one(c, d, output, args)
        value = output.getvalue()
        print(len(value.splitlines()))
        actual = yaml.safe_load(output.getvalue())
        self.assertEqual(expected, actual)

    def test_list(self):
        sf = yaml_format.YAMLFormatter()
        c = ('a', 'b', 'c')
        d = (('A1', 'B1', 'C1'), ('A2', 'B2', 'C2'), ('A3', 'B3', 'C3'))
        expected = [
            {'a': 'A1', 'b': 'B1', 'c': 'C1'},
            {'a': 'A2', 'b': 'B2', 'c': 'C2'},
            {'a': 'A3', 'b': 'B3', 'c': 'C3'},
        ]
        output = StringIO()
        args = mock.Mock()
        sf.add_argument_group(args)
        sf.emit_list(c, d, output, args)
        actual = yaml.safe_load(output.getvalue())
        self.assertEqual(expected, actual)

    def test_formattablecolumn_list(self):
        sf = yaml_format.YAMLFormatter()
        c = ('a', 'b', 'c')
        d = (('A1', 'B1', test_columns.FauxColumn(['the', 'value'])),)
        expected = [
            {'a': 'A1', 'b': 'B1', 'c': ['the', 'value']},
        ]
        args = mock.Mock()
        sf.add_argument_group(args)

        args.noindent = True
        output = StringIO()
        sf.emit_list(c, d, output, args)
        actual = yaml.safe_load(output.getvalue())
        self.assertEqual(expected, actual)

    def test_one_custom_object(self):
        sf = yaml_format.YAMLFormatter()
        c = ('a', 'b', 'toDict', 'to_dict')
        d = ('A', 'B', _toDict(spam="ham"), _to_Dict(ham="eggs"))
        expected = {
            'a': 'A',
            'b': 'B',
            'toDict': {"spam": "ham"},
            'to_dict': {"ham": "eggs"},
        }
        output = StringIO()
        args = mock.Mock()
        sf.emit_one(c, d, output, args)
        actual = yaml.safe_load(output.getvalue())
        self.assertEqual(expected, actual)

    def test_list_custom_object(self):
        sf = yaml_format.YAMLFormatter()
        c = ('a', 'toDict', 'to_dict')
        d = (
            ('A1', _toDict(B=1), _to_Dict(C=1)),
            ('A2', _toDict(B=2), _to_Dict(C=2)),
            ('A3', _toDict(B=3), _to_Dict(C=3)),
        )
        expected = [
            {'a': 'A1', 'toDict': {'B': 1}, 'to_dict': {'C': 1}},
            {'a': 'A2', 'toDict': {'B': 2}, 'to_dict': {'C': 2}},
            {'a': 'A3', 'toDict': {'B': 3}, 'to_dict': {'C': 3}},
        ]
        output = StringIO()
        args = mock.Mock()
        sf.add_argument_group(args)
        sf.emit_list(c, d, output, args)
        actual = yaml.safe_load(output.getvalue())
        self.assertEqual(expected, actual)
