#
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


from cliff import app
from cliff.interactive import InteractiveApp
from cliff.tests import base
from cliff.tests import utils


class TestInteractive(base.TestBase):
    def make_interactive_app(self, errexit, *command_names):
        fake_command_manager = [(x, None) for x in command_names]
        return InteractiveApp(
            app.App(
                'foo', '1.0', utils.TestCommandManager(utils.TEST_NAMESPACE)
            ),
            fake_command_manager,  # type: ignore
            stdin=None,
            stdout=None,
            errexit=errexit,
        )

    def _test_completedefault(self, expecteds, line, begidx):
        command_names = set(
            ['show file', 'show folder', 'show  long', 'list all']
        )
        app = self.make_interactive_app(False, *command_names)
        observeds = app.completedefault(None, line, begidx, None)
        self.assertEqual(set(expecteds), set(observeds))
        self.assertTrue(
            set([line[:begidx] + x for x in observeds]) <= command_names
        )

    def test_empty_text_completedefault(self):
        # line = 'show ' + begidx = 5 implies text = ''
        self._test_completedefault(['file', 'folder', ' long'], 'show ', 5)

    def test_nonempty_text_completedefault2(self):
        # line = 'show f' + begidx = 6 implies text = 'f'
        self._test_completedefault(['file', 'folder'], 'show f', 5)

    def test_long_completedefault(self):
        self._test_completedefault(['long'], 'show  ', 6)

    def test_no_completedefault(self):
        self._test_completedefault([], 'taz ', 4)

    def test_no_errexit(self):
        command_names = set(['show file', 'show folder', 'list all'])
        app = self.make_interactive_app(False, *command_names)
        self.assertFalse(app.errexit)

    def test_errexit(self):
        command_names = set(['show file', 'show folder', 'list all'])
        app = self.make_interactive_app(True, *command_names)
        self.assertTrue(app.errexit)
