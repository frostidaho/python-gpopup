#!/bin/bash
# Get bash script directory http://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
data_dir="$(dirname "$DIR")/data"

runcmd() {
    echo "Running command:"
    echo -e "\t $@"
    eval "$@"
}

echo "Information about prices for hot cheesy garbage"
runcmd "gpopup-send --position northeast $data_dir/pizza.json"

