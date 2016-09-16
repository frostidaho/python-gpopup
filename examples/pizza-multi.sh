#!/bin/sh
set -e -E # -e --> exit on err; -E --> print error trace
exdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
gpopup-client --timeout 1.5 --start-server-maybe $exdir/data/pizza_multi.json
sleep 2
gpopup-client --kill-server
