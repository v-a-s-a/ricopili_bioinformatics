
from setuptools import setup, find_packages

setup(name="ricopili_bioinformatics",
      version="0.1",
      description="Prototype for snakemake-based Ricopili bioinformatics pipeline.",
      url="https://github.com/vtrubets/ricopili_bioinformatics",
      author="Vassily Trubetskoy",
      author_email='',
      license="MIT",
      packages=find_packages(),
      install_requires=["snakemake", "pyyaml"],
      scripts=["bioinformatics/bioinformatics"],
      package_data={"bioinformatics.ricopili_magma":
         ["cluster_config.yaml",
          "Snakefile",
          "resources/magma_linux/magma",
          "resources/magma_linux/reference_data/NCBI37.3.gene.loc"]},
      zip_safe=False)
