#!/usr/bin/env python
"""
Wrapping MAGMA into a toil pipeline.
"""

from toil.job import Job
import subprocess as sp


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

            return snp_loc_file


class AnnotateSummaryStats(Job):
    """
    Annotate summary statistics with gene membership. Reference data provided
    by MAGMA.

    Example command:
    $magma_bin  --annotate
                --snp-loc ${snp_loc_file}
                --gene-loc "magma_v1.05b_static/reference_data/NCBI37.3.gene.loc"
                --out ${annotation_file}
    """
    def __init__(self, snp_loc_file, magma_bin, gene_loc_ref):
        Job.__init__(self, memory="100M", cores=1, disk="100M")
        self.snp_loc_file = snp_loc_file
        self.magma_bin = magma_bin
        self.gene_loc_ref = gene_loc_ref

    def run(self, fileStore):
        fileStore.logToMaster("Annotating summary statistics with gene membership.")
        local_annotated_file = fileStore.getLocalTempFile()

        cmd = [self.magma_bin, "--annotate",
               "--snp-loc", fileStore.readGlobalFile(self.snp_loc_file),
               "--gene-loc", self.gene_loc_ref,
               "--out", local_annotated_file]

        sp.call(cmd)

        # push the annotated file into the global file store
        return fileStore.writeGlobalFile(local_annotated_file)


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
    def __init__(self, chromosome, magma_bin, sample_size, annotated_file, daner_file, reference_data):
        Job.__init__(self, memory="100M", cores=1, disk="100M")
        self.chromosome = chromosome
        self.magma_bin = magma_bin
        self.sample_size = sample_size
        self.annotated_file = annotated_file
        self.daner_file = daner_file
        self.reference_data = reference_data

    def run(self, fileStore):
        fileStore.logToMaster("Testing genes on chromosome {}".format(self.chromosome))

        results_prefix = fileStore.getLocalTempFile()

        cmd = [self.magma_bin,
               "--bfile", self.reference_data,
               "--batch", self.chromosome,
               "--pval", self.daner_file,
               "N={}".format(self.sample_size),
               "--gene-annot", "${annot_file}.genes.annot",
               "--out", results_prefix]

         sp.run(cmd)

         return 

class MergeTestSets(Job):
    """
    Merge gene set tests into single results file.

    Example Command:
    ${magma_bin} --merge ${results_prefix} --out ${results_prefix}
    """
    def __init__(self, magma_bin):
        Job.__init__(self, memory="100M", cores=1, disk="100M")
        self.magma_bin = magma_bin

    def run(self, fileStore):
        fileStore.logToMaster("Merging test sets.")


def run_magma_pipeline(toil_options):
    """
    Initial target: MAGMA analysis using summary statistics
    """

    MAGMA_BINARY = "/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/resources/magma_macOS/magma"

    # define jobs
    make_snp_location_file_job = MakeSnpLocationFile(daner_file="/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/test/resources/pgc_scz_chr22_subset.daner")
    annotate_summary_stats_job = AnnotateSummaryStats(magma_bin=MAGMA_BINARY,
                                                      snp_loc_file=make_snp_location_file_job.rv(),
                                                      gene_loc_ref="/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/resources/magma_macOS/reference_data/NCBI37.3.gene.loc")
     test_gene_sets_jobs = [TestGeneSets(chromosome=chrm, magma_bin=MAGMA_BINARY, ) for chrm in range(22, 23)]
    # merge_gene_sets_job = MergeTestSets(magma_bin=MAGMA_BINARY)

    # specify dependencies
    make_snp_location_file_job.addChild(annotate_summary_stats_job, )
    # for job in test_gene_sets_jobs:
    #     annotate_summary_stats_job.addChild(job)
    # annotate_summary_stats_job.addFollowOn(merge_gene_sets_job)

    # execute workflow
    Job.Runner.startToil(make_snp_location_file_job, toil_options)


if __name__ == "__main__":
    toil_options = Job.Runner.getDefaultOptions('./test_file_store')
    # toil_options.clean = 'always'
    toil_options.clean = 'never'
    toil_options.logLevel = 'INFO'
    run_magma_pipeline(toil_options)
