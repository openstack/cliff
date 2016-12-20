#!/usr/bin/env bash

# Client constraint file contains this client version pin that is in conflict
# with installing the client from source. We should remove the version pin in
# the constraints file before applying it for from-source installation.
# The script also has a secondary purpose to install certain special
# dependencies directly from git.

# Wrapper for pip install that always uses constraints.
function pip_install() {
    pip install -c"$localfile" -U "$@"
}

# Grab the library from git using either zuul-cloner or pip.  The former is
# there to a take advantage of the setup done by the gate infrastructure
# and honour any/all Depends-On headers in the commit message
function install_from_git() {
    ZUUL_CLONER=/usr/zuul-env/bin/zuul-cloner
    GIT_HOST=git.openstack.org
    PROJ=$1
    EGG=$2

    edit-constraints "$localfile" -- "$EGG"
    if [ -x "$ZUUL_CLONER" ]; then
        SRC_DIR="$VIRTUAL_ENV/src"
        mkdir -p "$SRC_DIR"
        cd "$SRC_DIR" >/dev/null
        ZUUL_CACHE_DIR=${ZUUL_CACHE_DIR:-/opt/git} $ZUUL_CLONER \
            --branch "$BRANCH_NAME" \
            "git://$GIT_HOST" "$PROJ"
        pip_install -e "$PROJ/."
        cd - >/dev/null
    else
        pip_install -e"git+https://$GIT_HOST/$PROJ@$BRANCH_NAME#egg=${EGG}"
    fi
}



CONSTRAINTS_FILE="$1"
shift 1

# This script will either complete with a return code of 0 or the return code
# of whatever failed.
set -e

# NOTE(tonyb): Place this in the tox environment's log dir so it will get
# published to logs.openstack.org for easy debugging.
mkdir -p "$VIRTUAL_ENV/log/"
localfile="$VIRTUAL_ENV/log/upper-constraints.txt"

if [[ "$CONSTRAINTS_FILE" != http* ]]; then
    CONSTRAINTS_FILE="file://$CONSTRAINTS_FILE"
fi
# NOTE(tonyb): need to add curl to bindep.txt if the project supports bindep
curl "$CONSTRAINTS_FILE" --insecure --progress-bar --output "$localfile"

pip_install openstack-requirements

# This is the main purpose of the script: Allow local installation of
# the current repo. It is listed in constraints file and thus any
# install will be constrained and we need to unconstrain it.
edit-constraints "$localfile" -- "$CLIENT_NAME"

declare -a passthrough_args
while [ $# -gt 0 ] ; do
    case "$1" in
    # If we have any special os:<repo_name:<egg_name> deps then process them
    os:*)
        declare -a pkg_spec
        IFS=: pkg_spec=($1)
        install_from_git "${pkg_spec[1]}" "${pkg_spec[2]}"
    ;;
    # Otherwise just pass the other deps through to the constrained pip install
    *)
        passthrough_args+=("$1")
    ;;
    esac
    shift 1
done

# If *only* had special args then then isn't any need to run pip.
if [ -n "$passthrough_args" ] ; then
    pip_install "${passthrough_args[@]}"
fi
