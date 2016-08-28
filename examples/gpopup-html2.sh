#!/bin/sh
runcmd() {
    echo "Running command:"
    echo -e "\t $@"
    eval "$@"
}

runcmd 'gpopup-send --parser html table_ex2.html table_ex2_no_headers.html'
# runcmd 'gpopup-send --parser html table_ex2_no_headers.html'

