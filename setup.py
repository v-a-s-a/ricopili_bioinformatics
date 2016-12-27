
from setuptools import setup, find_packages

setup(name="ricopili_bioinformatics",
      version="0.1",
      description="Prototype for snakemake-based Ricopili postimputation pipeline.",
      url="https://github.com/vtrubets/ricopili_bioinformatics",
      author="Vasa Trubetskoy",
      author_email='',
      license="MIT",
      packages=find_packages(),
      install_requires=["snakemake"],
      scripts=["src/snakemake/postimputation"],
      package_data={"snakemake_config": "src/snakemake/config.yaml",
                    "cluster_config": "src/snakemake/broad_uger_config.yaml",
                    "magma_binary": "resources/magma_linux/magma",
                    "gene_loc_ref": "resources/magma_linux/reference_data/"
                                    "NCBI37.3.gene.loc",
                    "snakefile": "src/snakemake/Snakefile"},
      zip_safe=False)
