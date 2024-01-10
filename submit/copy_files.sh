#!/bin/bash

source_dir="/staging/dashtiahanga/dscovr/reprojected/"
destination_dir="/home/dashtiahanga/dscovr/data/"

# Check if the source directory exists
if [ ! -d "$source_dir" ]; then
    echo "Source directory does not exist."
    exit 1
fi

# Check if the destination directory exists
if [ ! -d "$destination_dir" ]; then
    echo "Destination directory does not exist."
    exit 1
fi

# Move files from source to destination
for file in "$source_dir"/*; do
    filename=$(basename "$file")
    destination_path="$destination_dir/$filename"

    # Check if the file already exists in the destination
    if [ -e "$destination_path" ]; then
        echo "Warning: File '$filename' already exists in the destination."
    else
        mv "$file" "$destination_dir"
        echo "File '$filename' moved to '$destination_dir'."
    fi
done

