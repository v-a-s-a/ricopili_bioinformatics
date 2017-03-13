#!/usr/bin/env python

from bioinformatics.Tool import Tool
from pkg_resources import resource_filename


class Magma(Tool):

    @staticmethod
    def magma_simple_logger(log_dict):
        """
        Print the basic execution of the pipeline.
        """
        if log_dict["level"] == "job_info":
            if log_dict["name"] == "make_snp_location_file":
                print("\tCreating SNP location file")
            elif log_dict["name"] == "annotate_summary_stats":
                print("\tAnnotating summary statistics with gene-membership")
            elif log_dict["name"] == "test_gene_sets":
                print("\tTesting genes on chr{chrom}".format(chrom=log_dict["wildcards"]["chrom"]))
            elif log_dict["name"] == "merge_test_sets":
                print("\tMerging test results")
            else:
                pass

    def __init__(self, subparser):

        magma_parser = subparser.add_parser(
            "magma",
            help="Multi-marker Analysis of GenoMic Annotation")
        magma_parser.add_argument("--daner", action="store", dest="daner")
        magma_parser.add_argument("--ref-1000g", action="store",
                                  dest="ref_1000g")
        magma_parser.add_argument("--sample-size", action="store",
                                  dest="study_sample_size")
        magma_parser.add_argument("--ref-gene-loc", action="store",
                                  dest="ref_gene_loc",
                                  default=resource_filename(
                                      "bioinformatics.tools.magma",
                                      "resources/magma_linux/reference_data/NCBI37.3.gene.loc"))

        Tool.__init__(
            self,
            snakefile=resource_filename(
                "bioinformatics.tools.magma",
                "magma.snakefile"),
            log_handler=None)
