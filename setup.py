
from setuptools import setup, find_packages

setup(name="ricopili_bioinformatics",
      version="0.1",
      description="Prototype for snakemake-based Ricopili postimputation pipeline.",
      url="https://github.com/vtrubets/ricopili_bioinformatics",
      author="Vasa Trubetskoy",
      author_email='',
      license="MIT",
      packages=["ricopili_bioinformatics", "resources", "src"],
      install_requires=["snakemake"],
      scripts=["src/snakemake/postimputation"],
      package_data={"src": ["snakemake/config.yaml"],
                    "src": ["snakemake/broad_uger_config.yaml"],
                    "resources": ["magma_linux/magma"],
                    "resources": ["resources/magma_linux/reference_data/NCBI37.3.gene.loc"],
                    "src": ["snakemake/Snakefile"]},
      zip_safe=False)
