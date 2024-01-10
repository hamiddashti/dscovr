#!/bin/bash

set -e

cleanup() {
  echo "Cleaning up..."
  rm -f "$FILENAME"
  rm -f MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5
}

trap 'cleanup' ERR

# Decompress the source code files
tar -xvf source_code.tar.gz

URL="$1"
#URL="https://opendap.larc.nasa.gov/opendap/DSCOVR/EPIC/L2_VESDR_02/2016/08/DSCOVR_EPIC_L2_VESDR_02_20160823141930_03.h5"
FILENAME=$(basename "$URL")
# Run the download script with the provided URL

./download.sh "$URL"

# Copy the land cover data which is needed for reprojection

cp /staging/dashtiahanga/dscovr/landuse/MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5 ./

# Activate python Env
ENVNAME=dscovr2
export ENVDIR=$ENVNAME
cp /staging/dashtiahanga/software/dscovr2.tar.gz ./

export PATH
mkdir $ENVDIR
tar -xzf $ENVNAME.tar.gz -C $ENVDIR

. $ENVDIR/bin/activate

mkdir outputs

python3 reproject.py $FILENAME

tar -cvf $FILENAME.tar.gz outputs

cleanup