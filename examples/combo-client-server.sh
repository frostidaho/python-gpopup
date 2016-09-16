#!/bin/sh
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Starting gpopup-server"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
gpopup-server --force-bind &
notification_id=$(cat data/wiki_gdp.json data/pizza.json | jq '.' --slurp | gpopup-client - | jq '.notification_id')
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
nid_2=$(gpopup-client  ./data/pizza.json ./data/wiki_gdp.json | jq '.notification_id')
sleep 1
echo "Showing original window"
gpopup-client --show -id $notification_id
sleep 1
echo "Destroying original window"
gpopup-client --destroy -id $notification_id
sleep 1
echo "Destroying most recently created window"
# FIXME gpopup-client --destroy $nid_2
# Need to get rid of decrementing the notification_id
gpopup-client --destroy
sleep 1
echo "Killing the server"
gpopup-client --kill-server
