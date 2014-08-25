#!/bin/sh -x

set -e

envdir=$1

# Manually download the source from PyPI and build it with the --editable flag.
# This gives us access to run the tests.
pip install --pre --no-deps --no-install --no-clean --no-use-wheel python-openstackclient

# This is where the source will end up after pip is done downloading and building it
srcdir=$envdir/build/python-openstackclient/
cd $srcdir

# Install the source safely
pip install --no-clean -ve .

# Install the test requirements
pip install --no-clean -r $srcdir/test-requirements.txt

# Force a known hash seed value to avoid sorting errors from tox
# giving us a random one.
export PYTHONHASHSEED=0

# Run testr
python setup.py testr
