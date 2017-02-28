#!/usr/bin/env python

import bioinformatics.Tool as Tool
from pkg_resources import resource_filename


class RegionAnnotator(Tool):

    def __init__(self, subparser, context):

        region_annotator_parser = subparser.add_parser(
            "region_annotator",
            help="https://github.com/ivankosmos/RegionAnnotator")
        region_annotator_parser.add_argument("--daner", action="store", dest="daner")

        Tool.__init__(
            self,
            snakefile=resource_filename(
                "bioinformatics.tools.region_annotator",
                "region_annotator.snakefile"),
            config=None,
            context=context,
            log_handler=None)
