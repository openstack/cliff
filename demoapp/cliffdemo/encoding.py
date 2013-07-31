# -*- encoding: utf-8 -*-

import logging

from cliff.lister import Lister


class Encoding(Lister):
    """Show some unicode text
    """

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        messages = [
            u'pi: π',
            u'GB18030:鼀丅㐀ٸཌྷᠧꌢ€',
        ]
        return (
            ('UTF-8', 'Unicode'),
            [(repr(t.encode('utf-8')), t)
             for t in messages],
        )
