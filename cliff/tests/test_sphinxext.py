# Copyright (C) 2017, Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import textwrap

from cliff import sphinxext
from cliff.tests import base


class TestSphinxExtension(base.TestBase):

    def test_empty_help(self):
        """Handle positional and optional actions without help messages."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', action='store')
        parser.add_argument('--language', dest='lang')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world [--language LANG] name

        .. option:: --language <LANG>

        .. option:: name
        """).lstrip(), output)

    def test_nonempty_help(self):
        """Handle positional and optional actions with help messages."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--language', dest='lang',
                            help='greeting language')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world [--language LANG] name

        .. option:: --language <LANG>

            greeting language

        .. option:: name

            user name
        """).lstrip(), output)

    def test_flag(self):
        """Handle a boolean argparse action."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--translate', action='store_true',
                            help='translate to local language')

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world [--translate] name

        .. option:: --translate

            translate to local language

        .. option:: name

            user name
        """).lstrip(), output)

    def test_supressed(self):
        """Handle a supressed action."""
        parser = argparse.ArgumentParser(prog='hello-world', add_help=False)
        parser.add_argument('name', help='user name')
        parser.add_argument('--variable', help=argparse.SUPPRESS)

        output = '\n'.join(sphinxext._format_parser(parser))
        self.assertEqual(textwrap.dedent("""
        .. program:: hello-world
        .. code-block:: shell

            hello-world name


        .. option:: name

            user name
        """).lstrip(), output)
