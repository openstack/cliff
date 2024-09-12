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

import unittest

from cliff import _argparse


class TestArgparse(unittest.TestCase):
    def test_argument_parser(self):
        _argparse.ArgumentParser(conflict_handler='ignore')

    def test_argument_parser_add_group(self):
        parser = _argparse.ArgumentParser(conflict_handler='ignore')
        parser.add_argument_group()

    def test_argument_parser_add_mutually_exclusive_group(self):
        parser = _argparse.ArgumentParser(conflict_handler='ignore')
        parser.add_mutually_exclusive_group()

    def test_argument_parser_add_nested_group(self):
        parser = _argparse.ArgumentParser(conflict_handler='ignore')
        group = parser.add_argument_group()
        group.add_argument_group()

    def test_argument_parser_add_nested_mutually_exclusive_group(self):
        parser = _argparse.ArgumentParser(conflict_handler='ignore')
        group = parser.add_argument_group()
        group.add_mutually_exclusive_group()

    def test_argument_parser_add_mx_nested_group(self):
        parser = _argparse.ArgumentParser(conflict_handler='ignore')
        group = parser.add_mutually_exclusive_group()
        group.add_argument_group()

    def test_argument_parser_add_mx_nested_mutually_exclusive_group(self):
        parser = _argparse.ArgumentParser(conflict_handler='ignore')
        group = parser.add_mutually_exclusive_group()
        group.add_mutually_exclusive_group()
