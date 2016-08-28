#!/bin/sh
runcmd() {
    echo "Running command:"
    echo -e "\t $@"
    eval "$@"
}

runcmd 'gpopup-send --parser html table_ex.html'
runcmd 'gpopup-send --parser html table_ex.html table_ex.html'
runcmd 'cat table_ex.html | gpopup-send --parser html -'

