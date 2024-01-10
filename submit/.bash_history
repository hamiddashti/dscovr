ls
tar -xvf source_code.tar.gz
ls
URL="https://opendap.larc.nasa.gov/opendap/DSCOVR/EPIC/L2_VESDR_02/2016/08/DSCOVR_EPIC_L2_VESDR_02_20160823152458_03.h5"
FILENAME=$(basename "$URL")
echo FILENAME
echo $FILENAME
vim download.sh 
URL="https://asdc.larc.nasa.gov/data/DSCOVR/EPIC/L2_VESDR_02/2016/08/DSCOVR_EPIC_L2_VESDR_02_20160823152458_03.h5"
FILENAME=$(basename "$URL")
echo $FILENAME
echp $URL
echo $URL
./download.sh "$URL"
ls
cp /staging/dashtiahanga/dscovr/landuse/MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5 ./
ls
ENVNAME=dscovr2
export ENVDIR=$ENVNAME
cp /staging/dashtiahanga/software/dscovr2.tar.gz ./
ls
export PATH
mkdir $ENVDIR
tar -xzf $ENVNAME.tar.gz -C $ENVDIR
. $ENVDIR/bin/activate
mkdir outputs
python3 reproject.py $FILENAME
ls
ls outputs/
tar -cvf $FILENAME.tar.gz outputs
rm $FILENAME
rm MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5
ls
cleanup() {   echo "Cleaning up...";   rm -f "$FILENAME";   rm -f MCDLCHKM.V2010_01.REGIONALbio.10018m.BlocksOP.h5; }
trap 'cleanup' ERR
cleanup
./download.sh 
echo $URL
./download.sh "$URL"
ls
cleanup
ls
exit()
exit
