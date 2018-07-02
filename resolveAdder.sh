#!/bin/bash

export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting/"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

python3.6 resolveAdder.py $@

