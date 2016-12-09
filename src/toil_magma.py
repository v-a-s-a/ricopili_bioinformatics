#!/usr/bin/env python
"""
Wrapping MAGMA into a toil pipeline.
"""

from toil.job import Job
from tasks.AnnotateSummaryStats import AnnotateSummaryStats
from tasks.MakeSnpLocationFile import MakeSnpLocationFile
from tasks.TestGeneSets import TestGeneSets
from tasks.MergeTestSets import MergeTestSets

def run_magma_pipeline(toil_options):
    """
    Initial target: MAGMA analysis using summary statistics
    """

    BROAD_GIT_ROOT = "/home/unix/vassily/projects/pgc/ricopili_extension/ricopili_bioinformatics/"
    MAGMA_BINARY = BROAD_GIT_ROOT + "resources/magma_linux/magma"
    REF_1000G = "/psych/ripke/share/vasa/magma_ref/g1000_eur"
    REF_GENE_LOC = BROAD_GIT_ROOT + "resources/magma_macOS/reference_data/NCBI37.3.gene.loc"
    DANER_FILE = BROAD_GIT_ROOT + "test/resources/pgc_scz_chr22_subset.daner"
    SAMPLE_SIZE = "2000"

    # define jobs
    make_snp_location_file_job = MakeSnpLocationFile(daner_file=DANER_FILE)
    annotate_summary_stats_job = AnnotateSummaryStats(magma_bin=MAGMA_BINARY,
                                                      snp_loc_file=make_snp_location_file_job.rv(),
                                                      gene_loc_ref=REF_GENE_LOC)
    test_gene_sets_jobs = [TestGeneSets(chromosome=str(chrm),
                                        magma_bin=MAGMA_BINARY,
                                        sample_size=SAMPLE_SIZE,
                                        annotated_file=annotate_summary_stats_job.rv(),
                                        daner_file=DANER_FILE,
                                        reference_data=REF_1000G) for chrm in range(22, 23)]
    merge_gene_sets_job = MergeTestSets(magma_bin=MAGMA_BINARY, batch_results=[x.rv() for x in test_gene_sets_jobs])

    # specify dependencies among jobs
    make_snp_location_file_job.addChild(annotate_summary_stats_job)
    for job in test_gene_sets_jobs:
        annotate_summary_stats_job.addChild(job)
    annotate_summary_stats_job.addFollowOn(merge_gene_sets_job)

    # execute workflow
    Job.Runner.startToil(make_snp_location_file_job, toil_options)


if __name__ == "__main__":
    toil_options = Job.Runner.getDefaultOptions('./test_file_store')
    toil_options.clean = 'always'
    toil_options.clean = 'never'
    toil_options.cleanWorkDir = 'never'
    toil_options.workDir = '/home/unix/vassily/projects/pgc/ricopili_extension/toil_testing/toil_temp/'
    toil_options.logLevel = 'INFO'
    run_magma_pipeline(toil_options)
