#!/bin/bash

#URL="https://opendap.larc.nasa.gov/opendap/DSCOVR/EPIC/L2_VESDR_02/2016/08/DSCOVR_EPIC_L2_VESDR_02_20160823141930_03.h5"

URL="$1"
TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6ImhhbWlkZGFzaHRpIiwiZXhwIjoxNzA1Nzc0Njk3LCJpYXQiOjE3MDA1OTA2OTcsImlzcyI6IkVhcnRoZGF0YSBMb2dpbiJ9.k-lXQuz5jFdHt7P-ywfQvTNFwT7XKgttcIuOekDckcY6fDMQfaHZbxJGcMnv3SQk_pgX-CQg2lN2sTo7AshhA7YRkJafVo2TuUYE848ppwdxB7cXgOrBcnJUisK3od1woFJFBtXMBjfLP0v0uQCeChRiGAVDTMYVhApi2vmEHDoyyleDiPJ8TUYXWUq2P-VQgfePv879dBJcj2-90tWXNC91cfX5ujwB2KBZLyE7PGXPVzPGB-W4iV3aONVhsn9qNxmxjlW4fmQFTh93hNiKJUQvEVtCxxwGHZNVIPtXvzbwdOSd9qf71DFVYvWKXvSKQ0_fZNL8NyJ9MonjdMi2-g

mkdir my_output
#destination="/staging/dashtiahanga/"
destination="./"
download_dir=my_output/

#wget --verbose --header "Authorization: Bearer $TOKEN" --recursive --level=inf --no-parent --reject "index.html*" --execute robots=off -P "$download_dir" "$URL"

retries=3
for ((i=0; i<$retries; i++)); do
    wget --verbose --header "Authorization: Bearer $TOKEN" --recursive --level=inf --no-parent --reject "index.html*" --execute robots=off -P "$download_dir" "$URL"
    if [ $? -eq 0 ]; then
        break  # Successful download, exit loop
    fi
    sleep 5  # Wait before retrying
done

file_to_move=$(find "$download_dir" -name "*.h5" -type f -print | tail -n 1)

mv "$file_to_move" "$destination"

#tar -czf my_output.tar.gz my_output/

rm -r "$download_dir"
