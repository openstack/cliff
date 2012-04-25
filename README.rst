=======================================================
 cliff -- Command Line Interface Formulation Framework
=======================================================

cliff is a framework for building command line programs. It uses
setuptools entry points to provide subcommands, output formatters, and
other extensions.

To do
=====

- Should commands have an explicit API for checking whether the user
  can invoke them?
- example show app
- change API for list app to expect a sequence of dictionaries?
- unicode output for python 2 (incompatible with csv?)
- json formatter(s)
- pprint formatter(s)
- pretty but non-table formatter(s)
- shell script formatter(s)? (properties as variable names)
- create a few example commands that use a sqlite database to show how
  to manage transactions
- switch setup/teardown functions in app to use some sort of context
  manager?
- switch to distutils2 and the extensions package?
  - http://docs.python.org/dev/packaging/setupcfg.html
  - http://pypi.python.org/pypi/extensions
