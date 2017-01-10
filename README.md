# MAGMA

Currently, MAGMA is wrapped into the postimputation tool. It uses Snakemake to specify and execute the MAGMA pipeline.

## Installation

The postimputation tool can 

    pip install git+https://github.com/vtrubets/ricopili_bioinformatics.git

I would recommend installing into a python virtual environment such as `virtualev` or `conda`.

## Running MAGMA

Running is simple. On the LISA cluster, you should start a long-running interactive session and execute the following command:

    postimputation --mode drmaa \
                   --cluster-env lisa \
                   --output-dir "/path/to/output/directory/" \
                   magma \
                   --daner "/path/to/input.daner" \
                   --ref-1000g "/path/to/1000G_reference_file_prefix" \
                   --sample-size 20000
                   
Each option is fairly straightforward. Options are split into generic `postimputation` options, followed by `magma` specific options:
  * The `--mode` option specifies the execution mode. You can run MAGMA in a few contexts: a DRMAA compatible cluster, a less   capable "qsub" compatible cluster or a local machine.
  * The `--cluster-env` option specifies whether you are running on LISA or the Broad's UGER. This sets some environment variables and cluster options.
  * The `--output-dir` option specifies an output directory in which intermediate and final files are stored.
  * The `magma` action tells the `postimputation` tool that you wish to run the MAGMA subpipeline. MAGMGA specific options follow. 
  * The `--daner` option points to the daner-formated GWAS results file.
  * The `--ref-1000g` option specifies the path+prefix of the 1000 Genomes reference data that MAGMA provides for download on their site. See the Reference Data section on the [MAGMA website](http://ctg.cncr.nl/software/magma).
  * The `--sample-size` option specifies the sample size of the GWAS study from which the daner-formatted input file was produced.
  
The output directory currently contains many intermediate files in addition to the file output. The final output file can be found at `/path/to/output/directory/merged_results.*`.

If you are running on the Broad's UGER, the `--cluster-env` option should be set to `broad`.


