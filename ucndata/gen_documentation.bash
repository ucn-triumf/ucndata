#!/bin/bash
# generate documentation with working links
# Derek Fujimoto
# Nov 2024

# note: requires handsdown (https://github.com/vemel/handsdown)

# generate the documentation
cd ucndata
handsdown -o ../docs

# fix the broken links
cd ../docs
for file in *;
do
    if [ -f "$file" ];  then
        sed -i 's/()././' $file
    fi
done