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
        fileStore.logToMaster("Creating temporary SNP Location file.")

        # write a local file and copy to the global filestore upon completion
        snp_loc_file = fileStore.getLocalTempFile()

        with open(snp_loc_file, 'w') as snp_loc_conn:

            with open(self.daner_file, 'r') as daner_conn:
                for line in daner_conn:
                    line = line.strip().split()
                    snp_loc_conn.write('\t'.join((line[1], line[0], line[2])) + '\n')

        global_snp_loc_file = fileStore.writeGlobalFile(snp_loc_file)

        fileStore.logToMaster(fileStore.readGlobalFileStream(global_snp_loc_file).next())

        fileStore.logToMaster("Global SNP loc file at: {}".format(fileStore.readGlobalFile(global_snp_loc_file)))

        return global_snp_loc_file


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

        local_dir = fileStore.getLocalTempDir()
        local_snp_loc = local_dir + 'snp.loc'
        local_out_prefix = "{temp_dir}/magma".format(temp_dir=local_dir)

        cmd = [self.magma_bin, "--annotate",
               "--snp-loc", fileStore.readGlobalFile(self.snp_loc_file, userPath=local_snp_loc),
               "--gene-loc", self.gene_loc_ref,
               "--out", local_out_prefix]

        sp.call(cmd)

        global_annot = fileStore.writeGlobalFile(local_out_prefix + ".genes.annot")

        fileStore.logToMaster("Writing gene annotation file to: {}".format(global_annot))

        # push the annotated file into the global file store
        return global_annot


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

        results_prefix = "{temp_dir}/magma".format(temp_dir=fileStore.getLocalTempDir())
        local_raw = "{prefix}.batch{chrm}_chr.genes.raw".format(prefix=results_prefix,
                                                                chrm=self.chromosome)
        local_out = "{prefix}.batch{chrm}_chr.genes.out".format(prefix=results_prefix,
                                                                chrm=self.chromosome)
        local_log = "{prefix}.batch{chrm}_chr.genes.".format(prefix=results_prefix,
                                                             chrm=self.chromosome)

        cmd = [self.magma_bin,
               "--bfile", self.reference_data,
               "--batch", self.chromosome, "chr",
               "--pval", self.daner_file,
               "N={}".format(self.sample_size),
               "--gene-annot", fileStore.readGlobalFile(self.annotated_file),
               "--out", results_prefix]

        sp.call(cmd)

        fileStore.logToMaster("writing output to : {}".format(local_raw))

        global_raw = fileStore.writeGlobalFile(local_raw)
        global_out = fileStore.writeGlobalFile(local_out)
        global_log = fileStore.writeGlobalFile(local_log)

        return {"chrm": self.chromosome,
                "raw_file_id": global_raw,
                "out_file_id": global_out,
                "log_file_id": global_log}


class MergeTestSets(Job):
    """
    Merge gene set tests into single results file.

    Example Command:
    ${magma_bin} --merge ${results_prefix} --out ${results_prefix}
    """
    def __init__(self, magma_bin, batch_results):
        Job.__init__(self, memory="100M", cores=1, disk="100M")
        self.magma_bin = magma_bin
        # list of dicts containing file IDs from all gene tests
        self.batch_results = batch_results

    def run(self, fileStore):
        fileStore.logToMaster("Merging test sets.")

        # copy down inputs and store outputs locally
        local_dir = fileStore.getLocalTempDir()
        local_raw = "{dir}magma.batch{batch}_chr.raw"
        local_out = "{dir}magma.batch{batch}_chr.out"
        local_log = "{dir}magma.batch{batch}_chr.log"

        # copy down gene test files for merging
        for result in self.batch_resultsbatch_results:
            fileStore.readGlobalFile(local_raw.format(dir=local_dir, batch=result['chrm']))
            fileStore.readGlobalFile(local_out.format(dir=local_dir, batch=result['chrm']))
            fileStore.readGlobalFile(local_log.format(dir=local_dir, batch=result['chrm']))

        cmd = [self.magma_bin,
               "--merge", local_dir + "magma",
               "--out", local_dir + "merge"]

        sp.call(cmd)

        global_merged_raw = fileStore.writeGlobalFile(local_dir + "merge.genes.raw")
        global_merged_out = fileStore.writeGlobalFile(local_dir + "merge.genes.out")
        global_merged_log = fileStore.writeGlobalFile(local_log + "merge.log")

        return {"raw_file_id": global_merged_raw,
                "out_file_id": global_merged_out,
                "log_file_id": global_merged_log}


def run_magma_pipeline(toil_options):
    """
    Initial target: MAGMA analysis using summary statistics
    """

    MAGMA_BINARY = "/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/resources/magma_macOS/magma"
    REF_1000G = "/Users/vasya/Projects/ripkelab/ricopili/magma_reference_data/g1000_eur"
    REF_GENE_LOC = "/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/resources/magma_macOS/reference_data/NCBI37.3.gene.loc"
    DANER_FILE = "/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/test/resources/pgc_scz_chr22_subset.daner"
    SAMPLE_SIZE = "2000"

    # define jobs
    make_snp_location_file_job = MakeSnpLocationFile(daner_file="/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/test/resources/pgc_scz_chr22_subset.daner")
    annotate_summary_stats_job = AnnotateSummaryStats(magma_bin=MAGMA_BINARY,
                                                      snp_loc_file=make_snp_location_file_job.rv(),
                                                      gene_loc_ref=REF_GENE_LOC)
    test_gene_sets_jobs = [TestGeneSets(chromosome=str(chrm),
                                        magma_bin=MAGMA_BINARY,
                                        sample_size=SAMPLE_SIZE,
                                        annotated_file=make_snp_location_file_job.rv(),
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
    # toil_options.clean = 'always'
    toil_options.clean = 'never'
    toil_options.cleanWorkDir = 'never'
    toil_options.workDir = '/Users/vasya/Projects/ripkelab/ricopili/ricopili_bioinfomatics/src/toil_temp/'
    toil_options.logLevel = 'INFO'
    run_magma_pipeline(toil_options)
