#!/bin/bash
BASE_URL="https://opendap.larc.nasa.gov/opendap/DSCOVR/EPIC/L2_VESDR_02/2016/"
NEW_BASE_URL="https://asdc.larc.nasa.gov/data/DSCOVR/EPIC/L2_VESDR_02/2016/"
OUTPUT_DIR="file_lists"
ALL_FILES_OUTPUT_FILE="${OUTPUT_DIR}/all_files.txt"
# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"
# Loop through each month (01 to 12)
for month in {01..12}; do
    MONTH_URL="${BASE_URL}${month}/contents.html"
    OUTPUT_FILE="${OUTPUT_DIR}/file_list_${month}.txt"
    # Download the HTML content for the specific month
    file_list=($(curl -s "$MONTH_URL" | grep -oP '(?<=href=")[^"]+(?=")' | grep -oP '[^/]+\.h5' | awk '!a[$0]++' | sed "s|^|$BASE_URL${month}/|"))
    # Write the file names with the new base URL to the output file
    for file in "${file_list[@]}"; do
        new_file="${file//$BASE_URL/$NEW_BASE_URL}"
        echo "$new_file" >> "$OUTPUT_FILE"
        echo "$new_file" >> "$ALL_FILES_OUTPUT_FILE"
    done
    echo "File list for month $month saved to $OUTPUT_FILE"
done
# Count the total number of files
TOTAL_FILES=$(cat "$OUTPUT_DIR"/*.txt | wc -l)
echo "Total number of files in all file lists: $TOTAL_FILES"
