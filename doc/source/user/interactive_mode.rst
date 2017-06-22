==================
 Interactive Mode
==================

In addition to running single commands from the command line, cliff
supports an interactive mode in which the user is presented with a
separate command shell. All of the command plugins available from the
command line are automatically configured as commands within the
shell.

Refer to the cmd2_ documentation for more details about features of
the shell.

.. _cmd2: http://packages.python.org/cmd2/index.html

Example
=======

The ``cliffdemo`` application enters interactive mode if no command is
specified on the command line.

::

    (.venv)$ cliffdemo
    (cliffdemo) help
    
    Shell commands (type help <topic>):
    ===================================
    cmdenvironment  edit  hi       l   list  pause  r    save  shell      show
    ed              help  history  li  load  py     run  set   shortcuts
    
    Undocumented commands:
    ======================
    EOF  eof  exit  q  quit
    
    Application commands (type help <topic>):
    =========================================
    files  help  simple  file  error  two part

To obtain instructions for a built-in or application command, use the
``help`` command:

::
    
    (cliffdemo) help simple
    usage: simple [-h]
    
    A simple command that prints a message.
    
    optional arguments:
      -h, --help  Show help message and exit.

The commands can be run, including options and arguments, as on the
regular command line:

::
    
    (cliffdemo) simple
    sending greeting
    hi!
    (cliffdemo) files
    +----------------------+-------+
    |         Name         |  Size |
    +----------------------+-------+
    | .git                 |   578 |
    | .gitignore           |   268 |
    | .tox                 |   238 |
    | .venv                |   204 |
    | announce.rst         |  1015 |
    | announce.rst~        |   708 |
    | cliff                |   884 |
    | cliff.egg-info       |   340 |
    | cliffdemo.log        |  2193 |
    | cliffdemo.log.1      | 10225 |
    | demoapp              |   408 |
    | dist                 |   136 |
    | distribute_setup.py  | 15285 |
    | distribute_setup.pyc | 15196 |
    | docs                 |   238 |
    | LICENSE              | 11358 |
    | Makefile             |   376 |
    | Makefile~            |    94 |
    | MANIFEST.in          |   186 |
    | MANIFEST.in~         |   344 |
    | README.rst           |  1063 |
    | setup.py             |  5855 |
    | setup.py~            |  8128 |
    | tests                |   204 |
    | tox.ini              |    76 |
    | tox.ini~             |   421 |
    +----------------------+-------+
    (cliffdemo) 
