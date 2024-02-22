# Specify the directory where the files are
dir="/home/hamid/dscovr/data/EC/Ameriflux"

# Loop over all zip files in the specified directory that contain "unconf"
for file in "$dir"/*Unconf*
do
  # Unzip the file
  unzip "$file" -d "$dir"
done
