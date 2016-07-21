from cliff import columns


class FauxColumn(columns.FormattableColumn):

    def human_readable(self):
        return u'I made this string myself: {}'.format(self._value)


def test_faux_column_machine():
    c = FauxColumn(['list', 'of', 'values'])
    assert c.machine_readable() == ['list', 'of', 'values']


def test_faux_column_human():
    c = FauxColumn(['list', 'of', 'values'])
    assert c.human_readable() == \
        u"I made this string myself: ['list', 'of', 'values']"
