# ricopili_bioinformatics
Test bed for extending Ricopili with external bioinformatics tooling.

# MAGMA

## Installation

I would recommend using a virtual environment. Either `virtualev`, its relatives, or `conda`.

    pip install git+https://github.com/vtrubets/ricopili_bioinformatics.git

## Running on LISA

Running is simple:

    postimputation --mode drmaa \
                   --cluster-env lisa \
                   --daner "/path/to/input.daner" \
                   --output-dir "/path/to/output/directory/" \
                   --ref-1000g "/path/to/1000G_reference_file_prefix" \
                   --sample-size 20000
                   
Each option is fairly straightforward:
  * The `--mode` option specifies the execution mode. You can run MAGMA in a few contexts: a DRMAA compatible cluster, a less   capable "qsub" compatible cluster or a local machine.
  * The `--cluster-env` option specifies whether you are running on LISA or the Broad's UGER. This sets some environment variables and cluster options.
  * The `--daner` option points to the daner-formated GWAS results file.
  * The `--output-dir` option specifies an output directory in which intermediate and final files are stored.
  * The `--ref-1000g` option specifies the path+prefix of the 1000 Genomes reference data that MAGMA provides for download on their site. See the Reference Data section on the [MAGMA website](http://ctg.cncr.nl/software/magma).
  * The `--sample-size` option specifies the sample size of the GWAS study from which the daner-formatted input file was produced.
  
The output directory currently contains many intermediate files in addition to the file output. The final output file can be found at `/path/to/output/directory/merged_results.*`.



