
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
      package_data={
          "bioinformatics.config":
          ["cluster_config.yaml"],
          "bioinformatics.tools.magma":
          ["magma.snakefile",
           "resources/magma_linux/magma",
           "resources/magma_linux/reference_data/NCBI37.3.gene.loc"],
          "bioinformatics.tools.region_annotator":
          ["region_annotator.snakefile",
           "resources/RegionAnnotator-1.6.1/inputGene/gencode.genes.txt",
           "resources/RegionAnnotator-1.6.1/inputReference/*",
           "resources/RegionAnnotator-1.6.1/RegionAnnotator-1.6.1.jar"]},
      zip_safe=False)
