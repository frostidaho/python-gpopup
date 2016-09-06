#!/bin/bash
# Get bash script directory http://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
data_dir="$(dirname "$DIR")/data"

runcmd() {
    echo "Running command:"
    echo -e "\t $@"
    eval "$@"
}

echo "The html table used in this example is sourced from:"
echo "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
echo "The table was cut and pasted from the page's source, but not cleaned up."
runcmd "gpopup-send --parser html $data_dir/wiki_gdp.html"
