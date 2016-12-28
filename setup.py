
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
      package_data={"src": ["snakemake/config.yaml",
                            "snakemake/broad_uger_config.yaml",
                            "snakemake/Snakefile"],
                    "resources": ["magma_linux/magma",
                                  "magma_linux/reference_data/NCBI37.3.gene.loc"]},
      zip_safe=False)
