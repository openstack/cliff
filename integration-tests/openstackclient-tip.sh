#!/bin/sh -x

set -e

envdir=$1

# The source for the client library is checked out by pip because of
# the deps listed in tox.ini, so we just need to move into that
# directory.
cd $envdir/src/openstackclient/

pip install -r test-requirements.txt

# Force a known hash seed value to avoid sorting errors from tox
# giving us a random one.
export PYTHONHASHSEED=0

python setup.py testr
