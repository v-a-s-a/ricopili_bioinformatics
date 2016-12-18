#!/usr/bin/env bash

python ./src/toil/toil_magma.py \
        --daner-file /psych/ripke/share/vasa/daner_PGC_SCZ49_1000G-frq.sh2_mds10.gz \
        --sample-size 2000 \
        --backend gridEngine \
        --output-dir /home/unix/vassily/projects/pgc/ricopili_extension/toil_testing/toil_output/ \
        --file-store /psych/ripke/share/vasa/toil_testing/toil_file_store/ 
