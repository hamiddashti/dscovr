#!/bin/bash
rm source_code.tar.gz
tar -cvf source_code.tar.gz reproject.py utils.py download.sh 
condor_submit submit_file.sub 

