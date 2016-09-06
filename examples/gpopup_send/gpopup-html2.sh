#!/bin/bash
# Get bash script directory http://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
data_dir="$(dirname "$DIR")/data"

runcmd() {
    echo "Running command:"
    echo -e "\t $@"
    eval "$@"
}

runcmd "gpopup-send --parser html --position north $data_dir/table_ex2.html" &
runcmd "gpopup-send --parser html --position center $data_dir/table_ex2_no_headers.html"


