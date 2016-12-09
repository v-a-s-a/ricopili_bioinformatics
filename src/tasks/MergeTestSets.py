#!/usr/bin/env python

from toil.job import Job
import subprocess as sp

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
        for batch in self.batch_results:
            local_raw = "{dir}/magma.batch{batch}_chr.genes.raw".format(dir=local_dir, batch=batch['chrm'])
            local_out = "{dir}/magma.batch{batch}_chr.genes.out".format(dir=local_dir, batch=batch['chrm'])
            local_log = "{dir}/magma.batch{batch}_chr.log".format(dir=local_dir, batch=batch['chrm'])

            # copy/link down gene test files for merging
            fileStore.readGlobalFile(batch['raw_file_id'], userPath=local_raw)
            fileStore.readGlobalFile(batch['out_file_id'], userPath=local_out)
            fileStore.readGlobalFile(batch['log_file_id'], userPath=local_log)

        cmd = [self.magma_bin,
               "--merge", local_dir + "/magma",
               "--out", local_dir + "/merge"]

        sp.call(cmd)

        global_merged_raw = fileStore.writeGlobalFile(local_dir + "/merge.genes.raw")
        global_merged_out = fileStore.writeGlobalFile(local_dir + "/merge.genes.out")
        global_merged_log = fileStore.writeGlobalFile(local_dir + "/merge.log")

        return {"raw_file_id": global_merged_raw,
                "out_file_id": global_merged_out,
                "log_file_id": global_merged_log}


