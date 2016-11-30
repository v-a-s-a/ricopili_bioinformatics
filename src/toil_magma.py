#!/usr/bin/env python
"""
Wrapping MAGMA into a toil pipeline.
"""

from toil.job import Job


class MakeSnpLocationFile(Job):
    """
    Job to create the SNP location file.

    Example command:
    zcat $daner | awk '{print $2, $1, $3}'  > ${snp_loc_file}
    """
    def __init__(self, daner_file):
        Job.__init__(self, memory="100M", cores=1, disk="100M")
        self.daner_file = daner_file

    def run(self, fileStore):
        with fileStore.writeGlobalFileStream() as (snp_loc_conn, snp_loc_file):

            with open(self.daner_file) as daner_conn:
                for line in daner_conn:
                    line = line.strip().split()
                    snp_loc_conn.write('\t'.join((line[1], line[0], line[2])) + '\n')

            fileStore.logToMaster("Creating SNP Location file at: {}".format(snp_loc_file))


class AnnotateSummaryStats(Job):
    """
    Annotate summary statistics with gene membership. Reference data provided
    by MAGMA.

    Example command:
    $magma_bin  --annotate
                --snp-loc ${snp_loc_file}
                --gene-loc "magma_v1.05b_static/reference_data/NCBI37.3.gene.loc"
                --out $annot_file
    """
    def __init__(self):
        Job.__init__(self, memory="100M", cores=1, disk="100M")

    def run(self, fileStore):
        fileStore.logToMaster("Annotating summary statistics with gene membership.")


class TestGeneSets(Job):
    """
    Test gene sets split into chromosome batches.

    Example command:
    $magma_bin  --bfile ${ref_dat}
                --batch ${SGE_TASK_ID} chr
                --pval ${ricopili_daner}
                N=${study_sample_size}
                --gene-annot ${annot_file}.genes.annot
                --gene-settings snp-min-maf=0.05
                --out "${results_prefix}"
    """
    def __init__(self, chromosome):
        Job.__init__(self, memory="100M", cores=1, disk="100M")
        self.chromosome = chromosome

    def run(self, fileStore):
        fileStore.logToMaster("Testing genes on chromosome {}".format(self.chromosome))


class MergeTestSets(Job):
    """
    Merge gene set tests into single results file.

    Example Command:
    ${magma_bin} --merge ${results_prefix} --out ${results_prefix}
    """
    def __init__(self):
        Job.__init__(self, memory="100M", cores=1, disk="100M")

    def run(self, fileStore):
        fileStore.logToMaster("Merging test sets.")


def run_magma_pipeline(toil_options):
    """
    Initial target: MAGMA analysis using summary statistics
    """

    # define jobs
    make_snp_location_file_job = MakeSnpLocationFile(daner_file="/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/test/resources/pgc_scz_chr22_subset.daner")
    annotate_summary_stats_job = AnnotateSummaryStats()
    test_gene_sets_jobs = [TestGeneSets(chromosome) for chromosome in range(22, 23)]
    merge_gene_sets_job = MergeTestSets()

    # specify dependencies
    make_snp_location_file_job.addChild(annotate_summary_stats_job)
    for job in test_gene_sets_jobs:
        annotate_summary_stats_job.addChild(job)
    annotate_summary_stats_job.addFollowOn(merge_gene_sets_job)

    # execute workflow
    Job.Runner.startToil(make_snp_location_file_job, toil_options)


if __name__ == "__main__":
    toil_options = Job.Runner.getDefaultOptions('./test_file_store')
    toil_options.clean = 'never'
    toil_options.logLevel = 'INFO'
    run_magma_pipeline(toil_options)
