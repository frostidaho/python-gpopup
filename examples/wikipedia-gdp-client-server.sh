#!/bin/sh
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Starting gpopup-server"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
gpopup-server --force-bind &
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Starting gpopup-client using data from wiki_gdp.json"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
cat data/wiki_gdp.json | gpopup-client --parser json -
sleep 3
echo "Killing the server"
gpopup-client --kill-server
