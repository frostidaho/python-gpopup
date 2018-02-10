#!/bin/bash
set -e -E # -e --> exit on err; -E --> print error trace
exdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
datdir="$exdir/data"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Starting gpopup-server"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
gpopup-server --force-bind &
notification_id=$(cat $datdir/wiki_gdp.json $datdir/pizza.json | jq '.' --slurp | gpopup-client - | jq '.notification_id')
echo "Created a window with notification_id $notification_id"
sleep 3
echo "Moving the window"
gpopup-client --position northeast --move
sleep 0.5
gpopup-client --position southeast --move
sleep 0.5
gpopup-client --position southwest --move
sleep 0.5
gpopup-client --position northwest --move
sleep 0.5
echo "Hiding the window"
gpopup-client --hide
sleep 0.5
echo "Creating a new window - by passing filenames directly"
nid_2=$(gpopup-client  $datdir/opera.json $datdir/pizza.json | jq '.notification_id')
sleep 1
echo "Showing original window"
gpopup-client --show -id $notification_id
sleep 1
echo "Destroying original window"
gpopup-client --destroy -id $notification_id
sleep 1
echo "Destroying most recently created window"
gpopup-client --destroy -id $nid_2 # Could just leave off the id, since it
# was the last created window.
sleep 1
echo "Killing the server"
gpopup-client --kill-server
