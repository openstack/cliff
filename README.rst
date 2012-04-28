=======================================================
 cliff -- Command Line Interface Formulation Framework
=======================================================

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

Documentation
=============

Documentation for cliff is hosted on readthedocs.org at http://readthedocs.org/docs/cliff/en/latest/

To do
=====

- Should commands have an explicit API for checking whether the user
  can invoke them?
- change API for list app to expect a sequence of dictionaries?
- unicode output for python 2 (incompatible with csv?)
- json formatter(s)
- pprint formatter(s)
- shell script formatter for show commands
- create a few example commands that use a sqlite database to show how
  to manage transactions
- switch setup/teardown functions in app to use some sort of context
  manager?
- interactive shell mode
