#!/bin/bash
set -e -E # -e --> exit on err; -E --> print error trace
exdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Starting gpopup-server"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
gpopup-server --force-bind &
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Starting gpopup-client using data from wiki_gdp.json"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
cat $exdir/data/wiki_gdp.json | gpopup-client -
sleep 1.5
echo "Killing the server"
gpopup-client --kill-server
