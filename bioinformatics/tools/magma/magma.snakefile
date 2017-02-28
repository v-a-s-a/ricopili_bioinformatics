#!/usr/bin/env python

import os
from pkg_resources import resource_filename

AUTOSOMES = [str(x) for x in range(1, 23)]

intermediate_dir = os.path.join(config["output_dir"], "intermediate_results/")
log_dir = os.path.join(config["output_dir"], "logs/")

magma_bin = resource_filename(
    "bioinformatics.tools.region_annotator",
    "resources/magma_linux/magma")
ref_gene_loc_file = resource_filename(
    "bioinformatics.tools.region_annotator",
    "resources/magma_linux/reference_data/NCBI37.3.gene.loc")


rule all:
    input:
        os.path.join(config["output_dir"], "genomewide_test_results.genes.out")


rule make_snp_location_file:
    input:
        config["daner"]
    output:
        intermediate_dir + "snp.loc"
    shell:
        "cat {input} | awk '{{print $2, $1, $3}}'  > {output}"


rule annotate_summary_stats:
    input:
        intermediate_dir + "snp.loc"
    output:
        intermediate_dir + "annotate_summary_stats.genes.annot",
    log:
        output = log_dir + "annotate_summary_stats.stderr",
        magma = log_dir + "annotate_summary_stats.log"
    params:
        output_prefix = intermediate_dir + "annotate_summary_stats"
    shell:
        "({magma_bin}  --annotate "
        " --snp-loc {input} "
        " --gene-loc {config[ref_gene_loc]} "
        " --out {params.output_prefix}) 2> {log.output};"
        "mv {params.output_prefix}.log {log.magma}"


rule test_gene_sets:
    input:
        intermediate_dir + "annotate_summary_stats.genes.annot"
    output:
        intermediate_dir + "gene_results.batch{chrom}_chr.genes.out",
        intermediate_dir + "gene_results.batch{chrom}_chr.genes.raw",
    log:
        magma = log_dir + "gene_results.batch{chrom}_chr.log",
    params:
        batch_prefix = intermediate_dir + "gene_results"
    shell:
        "{magma_bin} --bfile {config[ref_1000g]} "
        " --batch {wildcards.chrom} chr "
        " --pval {config[daner]} "
        " N={config[study_sample_size]} "
        " --gene-annot {input} "
        " --out {params.batch_prefix}; "
        "mv {params.batch_prefix}.batch{wildcards.chrom}_chr.log {log.magma}"


rule merge_test_sets:
    input:
        expand(intermediate_dir + "gene_results.batch{chrom}_chr.genes.raw",
               chrom=AUTOSOMES)
    output:
        config["output_dir"] + "genomewide_test_results.genes.out",
        config["output_dir"] + "genomewide_test_results.genes.raw"
    log:
        magma = log_dir + "genomewide_test_results.log"
    params:
        batch_prefix = intermediate_dir + "gene_results",
        output_prefix = config["output_dir"] + "genomewide_test_results"
    shell:
        "{magma_bin} --merge {params.batch_prefix} "
        " --out {params.output_prefix};"
        "mv {params.output_prefix}.log {log.magma}"
