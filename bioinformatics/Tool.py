#!/usr/bin/env python

import yaml
import os
from snakemake import snakemake
from pkg_resources import resource_filename


class Tool():
    """
    A wrapped tool.
    """

    def __init__(self, snakefile, log_handler):
        self.snakefile = snakefile
        self.log_handler = log_handler

    def execute(self, execution_mode, context, config):
        """
        Execute the tool workflow
        """

        if not os.path.exists(os.path.join(config["output_dir"], '.config')):
            os.makedirs(os.path.join(config["output_dir"], '.config'))
        config_file = os.path.join(config["output_dir"], ".config/config.yaml")
        with open(config_file, 'w') as config_conn:
            yaml.dump(config, config_conn, default_flow_style=True)

        base_api_call = {"snakefile": self.snakefile,
                         "log_handler": self.log_handler,
                         "config": config,
                         "configfile": config_file,
                         "latency_wait": 60,
                         "cluster_config": resource_filename(
                             "bioinformatics.config",
                             "cluster_config.yaml")}

        if execution_mode == "local":
            # API call is already appropriately set
            pass
        elif execution_mode == "drmaa":
            base_api_call["drmaa"] = ""
        elif execution_mode == "qsub":
            base_api_call["cluster"] = "qsub"

        if context == "broad" and execution_mode == "drmaa":
            os.system("eval `/broad/software/dotkit/init -b`; use UGER")
            base_api_call["drmaa"] += " -l h_vmem={cluster.h_vmem} "
            base_api_call["nodes"] = 22
        elif context == "lisa" and execution_mode == "drmaa":
            base_api_call["drmaa"] += " -l mem={cluster.h_vmem} "
            base_api_call["drmaa"] += " -l walltime={cluster.walltime}"
            base_api_call["nodes"] = 1
            # os.environ["DRMAA_LIBRARY_PATH"] = "/usr/lib/pbs-drmaa/lib/libdrmaa.so.1.0.10"
        elif execution_mode == "local":
            pass
        else:
            raise Exception("Your requested cluster environment and submission "
                            "mode combination is not currently supported")

        # execute workflow
        print("Executing Ricopili bioinformatics")
        returncode = snakemake(**base_api_call)
        if returncode == 1:
            print("done")
