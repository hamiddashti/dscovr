#!/bin/bash

# Specify the directory where the tar.gz files are located
source_directory="../data/2016/08/"

# Change to the source directory
cd "$source_directory" || exit

# Iterate through all tar.gz files
for file in *.tar.gz; do
    # Extract the base name (excluding extension) to create the directory name
    dir_name="${file%.tar.gz}"

    # Create the directory if it doesn't exist
    mkdir -p "$dir_name"

    # Untar the file into the created directory
    tar -xf "$file" -C "$dir_name"

    echo "Extracted $file into $dir_name/"
done
