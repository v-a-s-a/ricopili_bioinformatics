#!/usr/bin/env python

from toil.job import Job

class MakeSnpLocationFile(Job):
    """
    Toil job to create the SNP location file.

    Wrapping the following command line:
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

