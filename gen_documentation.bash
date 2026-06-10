#!/bin/bash
# generate documentation with working links
# Derek Fujimoto
# Nov 2024

# note: requires handsdown (https://github.com/vemel/handsdown)

# generate the documentation
cd ucndata
handsdown -o ../docs --theme readthedocs

# fix the broken links
cd ../docs
for file in *;
do
    if [ -f "$file" ];  then

        # remove private method sections (leading _) and their TOC entries
        python3 - "$file" <<'PYEOF'
import re, sys
filename = sys.argv[1]
with open(filename) as f:
    lines = f.readlines()
result = []
skip = False
for line in lines:
    s = line.rstrip('\n')
    if re.match(r'^### \S+\._', s):       # start of a private method section
        skip = True
    elif re.match(r'^#{1,3} ', s):         # any heading ends the skip
        skip = False
    if not skip and not re.match(r'^\s*- \[.*\._', s):  # also drop TOC entries
        result.append(line)
with open(filename, 'w') as f:
    f.writelines(result)
PYEOF

        # replace bad empty parentheses in link anchors only (not in code examples)
        sed -E -i 's/\(#([^)]+)\(\)\)/(#\1)/g' $file

        # replace broken table of contents links
        name=$(basename $file .md)
        sed -i "s/#${name}()/#${name}/" $file

        # replace bad code links
        sed -i "s+../../+../ucndata/+" $file
    fi
done