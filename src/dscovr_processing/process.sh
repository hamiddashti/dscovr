#!/bin/bash

set -e

URL="$1"

# Run the download script with the provided URL
./download.sh "$URL"


ENVNAME=dscovr2
export ENVDIR=$ENVNAME

cp /staging/dashtiahanga/software/dscovr2.tar.gz ./
# tar -xzvf dscovr.tar.gz

# Activate the environment
export PATH
mkdir $ENVDIR
tar -xzf $ENVNAME.tar.gz -C $ENVDIR
. $ENVDIR/bin/activate

python3 hello.py