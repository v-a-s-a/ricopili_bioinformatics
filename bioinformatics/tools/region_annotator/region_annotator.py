#!/usr/bin/env python

from bioinformatics.Tool import Tool
from pkg_resources import resource_filename


class RegionAnnotator(Tool):

    def __init__(self, subparser):

        region_annotator_parser = subparser.add_parser(
            "region_annotator",
            help="https://github.com/ivankosmos/RegionAnnotator")
        region_annotator_parser.add_argument(
            "--daner-clump", action="store",
            dest="daner", help="The daner clump file output by ricopili common variant analysis.")

        super().__init__(
            snakefile=resource_filename(
                "bioinformatics.tools.region_annotator",
                "region_annotator.snakefile"),
            log_handler=None)
