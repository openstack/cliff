#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

PROJECT = 'cliffdemo'

# Change docs/sphinx/conf.py too!
VERSION = '0.1'

try:
    long_description = open('README.rst').read()
except OSError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,
    description='Demo app for cliff',
    long_description=long_description,
    author='Doug Hellmann',
    author_email='doug.hellmann@gmail.com',
    url='https://github.com/openstack/cliff',
    download_url='https://github.com/openstack/cliff/tarball/master',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],
    platforms=['Any'],
    scripts=[],
    provides=[],
    install_requires=['cliff'],
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['cliffdemo = cliffdemo.main:main'],
        'cliff.demo': [
            'simple = cliffdemo.simple:Simple',
            'two_part = cliffdemo.simple:Simple',
            'error = cliffdemo.simple:Error',
            'list files = cliffdemo.list:Files',
            'files = cliffdemo.list:Files',
            'file = cliffdemo.show:File',
            'show file = cliffdemo.show:File',
            'unicode = cliffdemo.encoding:Encoding',
            'hooked = cliffdemo.hook:Hooked',
        ],
        'cliff.demo.hooked': [
            'sample-hook = cliffdemo.hook:Hook',
        ],
    },
    zip_safe=False,
)
