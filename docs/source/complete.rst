====================
 Command Completion
====================

A generic command completion command is available to generate a
bash-completion script.  Currently, the command will generate a script
for bash versions 3 or 4.  There is also a mode that generates only
data that can be used in your own script.  The command completion script
is generated based on the commands and options that you have specified
in cliff.

Usage
=====

In order for your command to support command completions, you need to
add the `cliff.complete.CompleteCommand` class to your command manager.

::

    self.command_manager.add_command('complete', cliff.complete.CompleteCommand)

When you run the command, it will generate a bash-completion script:

::

    (.venv)$ mycmd complete
    _mycmd()
    {
      local cur prev words
      COMPREPLY=()
      _get_comp_words_by_ref -n : cur prev words
    
      # Command data:
      cmds='agent aggregate backup'
      cmds_agent='--name'
    ...
      if [ -z "${completed}" ] ; then
        COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )
      else
        COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )
      fi
      return 0
    }
    complete -F _mycmd mycmd

