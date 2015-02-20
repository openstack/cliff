# -*- encoding: utf-8 -*-

from cliff.interactive import InteractiveApp


class FakeApp(object):
    NAME = 'Fake'


def make_interactive_app(*command_names):
    fake_command_manager = [(x, None) for x in command_names]
    return InteractiveApp(FakeApp, fake_command_manager,
                          stdin=None, stdout=None)


def _test_completenames(expecteds, prefix):
    app = make_interactive_app('hips', 'hippo', 'nonmatching')
    assert set(app.completenames(prefix)) == set(expecteds)


def test_cmd2_completenames():
    # cmd2.Cmd define do_help method
    _test_completenames(['help'], 'he')


def test_cliff_completenames():
    _test_completenames(['hips', 'hippo'], 'hip')


def test_no_completenames():
    _test_completenames([], 'taz')


def test_both_completenames():
    # cmd2.Cmd define do_hi and do_history methods
    _test_completenames(['hi', 'history', 'hips', 'hippo'], 'hi')


def _test_completedefault(expecteds, line, begidx):
    command_names = set(['show file', 'show folder', 'show  long', 'list all'])
    app = make_interactive_app(*command_names)
    observeds = app.completedefault(None, line, begidx, None)
    assert set(observeds) == set(expecteds)
    assert set([line[:begidx] + x for x in observeds]) <= command_names


def test_empty_text_completedefault():
    # line = 'show ' + begidx = 5 implies text = ''
    _test_completedefault(['file', 'folder', ' long'], 'show ', 5)


def test_nonempty_text_completedefault2():
    # line = 'show f' + begidx = 6 implies text = 'f'
    _test_completedefault(['file', 'folder'], 'show f', 5)


def test_long_completedefault():
    _test_completedefault(['long'], 'show  ', 6)


def test_no_completedefault():
    _test_completedefault([], 'taz ', 4)
