#!/usr/bin/env python
"""
Wrapping MAGMA into a toil pipeline.
"""

from toil.job import Job
from tasks.AnnotateSummaryStats import AnnotateSummaryStats
from tasks.MakeSnpLocationFile import MakeSnpLocationFile
from tasks.TestGeneSets import TestGeneSets
from tasks.MergeTestSets import MergeTestSets

import argparse


def run_magma_pipeline(toil_options, sample_size, daner_file, output_dir):
    """
    Initial target: MAGMA analysis using summary statistics
    """

    BROAD_GIT_ROOT = "/home/unix/vassily/projects/pgc/ricopili_extension/ricopili_bioinformatics/"
    MAGMA_BINARY = BROAD_GIT_ROOT + "resources/magma_linux/magma"
    REF_1000G = "/psych/ripke/share/vasa/magma_ref/g1000_eur"
    REF_GENE_LOC = BROAD_GIT_ROOT + "resources/magma_macOS/reference_data/NCBI37.3.gene.loc"

    # define jobs
    make_snp_location_file_job = MakeSnpLocationFile(daner_file=daner_file)
    annotate_summary_stats_job = AnnotateSummaryStats(magma_bin=MAGMA_BINARY,
                                                      snp_loc_file=make_snp_location_file_job.rv(),
                                                      gene_loc_ref=REF_GENE_LOC)
    test_gene_sets_jobs = [TestGeneSets(chromosome=str(chrm),
                                        magma_bin=MAGMA_BINARY,
                                        sample_size=sample_size,
                                        annotated_file=annotate_summary_stats_job.rv(),
                                        daner_file=daner_file,
                                        reference_data=REF_1000G) for chrm in range(22, 23)]
    merge_gene_sets_job = MergeTestSets(magma_bin=MAGMA_BINARY,
                                        batch_results=[x.rv() for x in test_gene_sets_jobs],
                                        output_dir=output_dir)

    # specify dependencies among jobs
    make_snp_location_file_job.addChild(annotate_summary_stats_job)
    for job in test_gene_sets_jobs:
        annotate_summary_stats_job.addChild(job)
    annotate_summary_stats_job.addFollowOn(merge_gene_sets_job)

    # execute workflow
    Job.Runner.startToil(make_snp_location_file_job, toil_options)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file-store",
                        action="store",
                        dest="file_store",
                        default="./toil_file_store/",
                        help="The location for the toil file store.")
    parser.add_argument("--daner-file",
                        action="store",
                        dest="daner_file",
                        help="""The location of the Daner file containing summary
                        statistics""")
    parser.add_argument("--sample-size",
                        action="store",
                        dest="sample_size",
                        help="""The sample size of the study in which the
                        summary statisticswere generated.""")
    parser.add_argument("--backend",
                        action="store",
                        dest="backend",
                        choices=["singleMachine", "gridEngine"],
                        help="""The backend which toil will execute jobs on. the
                        'singleMachine' option means that the entire MAGMA workflow
                        will be executed locally. The 'gridEngine' option means
                        that jobs will be submitted to a cluster running SGE/OGE/UGE
                        (such as the Broad's UGER).""")
    parser.add_argument("--output-dir",
                        action="store",
                        dest="output_dir",
                        help="""The directory to output .raw, .out and .log files
                        from the MAGMA analysis.""")
    args = parser.parse_args()

    toil_options = Job.Runner.getDefaultOptions(args.file_store)
    toil_options.clean = 'always'
    toil_options.logLevel = 'INFO'

    run_magma_pipeline(toil_options,
                       sample_size=args.sample_size,
                       daner_file=args.daner_file,
                       output_dir=args.output_dir)
