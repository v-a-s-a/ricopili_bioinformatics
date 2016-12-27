
from setuptools import setup, find_packages

setup(name='ricopili_bioinformatics',
      version='0.1',
      description='Prototype for snakemake-based Ricopili postimputation pipeline.',
      url='https://github.com/vtrubets/ricopili_bioinformatics',
      author='Vasa Trubetskoy',
      author_email='',
      license='MIT',
      packages=find_packages(),
      install_requires=['requests'],
      scripts=['src/snakemake/postimputation'],
      zip_safe=False)
