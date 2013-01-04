=================
 Running demoapp
=================

Setup
-----

First, you need to create a virtual environment and activate it.

::

  $ pip install virtualenv
  $ virtualenv .venv
  $ . .venv/bin/activate
  (.venv)$ 

Next, install ``cliff`` in the environment.

::

  (.venv)$ python setup.py install

Now, install the demo application into the virtual environment.

::

  (.venv)$ cd demoapp
  (.venv)$ python setup.py install

Usage
-----

With cliff and the demo setup up, you can now play with it.

To see a list of commands available, run::

  (.venv)$ cliffdemo --help

One of the available commands is "simple" and running it

::

  (.venv)$ cliffdemo simple

produces the following

::

  sending greeting
  hi!


To see help for an individual command, include the command name on the
command line::

  (.venv)$ cliffdemo files --help

Cleaning Up
-----------

Finally, when done, deactivate your virtual environment::

  (.venv)$ deactivate
  $
