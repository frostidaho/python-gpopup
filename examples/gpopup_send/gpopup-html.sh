#!/bin/bash
# Get bash script directory http://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
data_dir="$(dirname "$DIR")/data"

runcmd() {
    echo "Running command:"
    echo -e "\t $@"
    eval "$@"
}

runcmd "gpopup-send --position northwest $data_dir/table_ex.html" &
runcmd "gpopup-send --position north $data_dir/table_ex.html $data_dir/table_ex.html" &
runcmd "cat $data_dir/table_ex.html | gpopup-send --position northeast -"

