#!/usr/bin/env python
"""
Wrapping MAGMA into a toil pipeline.
"""

from toil.job import Job


def make_snp_location_file(memory="100M", cores=1, disk="100M"):
    """
    zcat $daner | awk '{print $2, $1, $3}'  > ${snp_loc_file}
    """
    pass


def annotate_summary_stats(memory="100M", cores=1, disk="100M"):
    """
    Annotate summary statistics with gene membership. Reference data provided
    by MAGMA.

    Example command:
    $magma_bin  --annotate
                --snp-loc ${snp_loc_file}
                --gene-loc "magma_v1.05b_static/reference_data/NCBI37.3.gene.loc"
                --out $annot_file
    """
    pass


def test_gene_sets(memory="100M", cores=1, disk="100M"):
    """
    Test gene sets. Parallelized by chromosome here. It is possible for finer
    grained batching.

    Example command:
    $magma_bin  --bfile ${ref_dat}
                --batch ${SGE_TASK_ID} chr
                --pval ${ricopili_daner}
                N=${study_sample_size}
                --gene-annot ${annot_file}.genes.annot
                --gene-settings snp-min-maf=0.05
                --out "${results_prefix}"
    """
    pass


def merge_test_sets(memory="100M", cores=1, disk="100M"):
    """
    Merge gene set tests into single results file.

    Example Command:
    ${magma_bin} --merge ${results_prefix} --out ${results_prefix}
    """
    pass


def run_magma_pipeline(toil_options):
    """
    Initial target: MAGMA analysis using summary statistics
    """
    make_snp_location_file_job = Job.wrapJobFn(make_snp_location_file)
    annotate_summary_stats_job = make_snp_location_file_job.addChildFn(
        make_snp_location_file)
    test_gene_sets_job = annotate_summary_stats_job.addChildFn(test_gene_sets)
    merge_test_sets_job = test_gene_sets_job.addChildFn(merge_test_sets)
    Job.Runner.startToil(make_snp_location_file_job, toil_options)


if __name__ == "__main__":
    toil_options = Job.Runner.getDefaultOptions('./test_file_store')
    toil_options.clean = 'always'
    run_magma_pipeline(toil_options)
