#!/usr/bin/env python

from toil.job import Job
import subprocess as sp


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
        Job.__init__(self, memory="1G", cores=1, disk="100M")
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
