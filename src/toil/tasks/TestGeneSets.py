#!/usr/bin/env python

from toil.job import Job
import subprocess as sp

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
        local_log = "{prefix}.batch{chrm}_chr.log".format(prefix=results_prefix,
                                                          chrm=self.chromosome)

        fileStore.logToMaster("Writing batch log to: {}".format(local_log))

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

