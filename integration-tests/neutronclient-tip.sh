#!/bin/sh -x

set -e

envdir=$1

# The source for the client library is checked out by pip because of
# the deps listed in tox.ini, so we just need to move into that
# directory.
cd $envdir/src/neutronclient/

pip install -r test-requirements.txt

python setup.py testr
