import logging
import os
import stat

from cliff.lister import Lister


class Files(Lister):
    "Show a list of files in the current directory."

    log = logging.getLogger(__name__)

    def get_data(self, parsed_args):
        return (('Name', 'Size'),
                ((n, os.stat(n).st_size) for n in os.listdir('.'))
                )
