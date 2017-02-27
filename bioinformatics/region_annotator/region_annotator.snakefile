import os
from pkg_resources import resource_filename

gene_data_file = resource_filename(
    "bioinformatics.region_annotator",
    "resources/RegionAnnotator-1.6.1/inputGene/gencode.genes.txt")
reference_directory = resource_filename(
    "bioinformatics.region_annotator",
    "resources/RegionAnnotator-1.6.1/inputReference/")
region_annotator_jar = resource_filename(
    "bioinformatics.region_annotator",
    "resources/RegionAnnotator-1.6.1/RegionAnnotator-1.6.1.jar")


final_output = os.path.join(config["output_dir"], "region_annotator_output.xlsx")


rule all:
    input:
        final_output


rule load_gene_data:
    input:
        gene_data_file
    output:
        touch(os.path.join(config["output_dir"], "load_gene_data.done"))
    shell:
        "java -jar {region_annotator_jar} -input {input} -gene -iformat TSV -db {config[output_dir]}"


rule load_reference_data:
    input:
        reference_directory
    output:
        touch(os.path.join(config["output_dir"], "load_reference_data.done"))
    shell:
        "java -jar {region_annotator_jar} -input {input} -reference -iformat TSV -db {config[output_dir]}"


rule annotate_regions:
    input:
        config["daner"],
        rules.load_reference_data.output,
        rules.load_gene_data.output
    output:
        final_output
    shell:
        "java -jar {region_annotator_jar} -input {input} -output {output} -iformat TSV -db {config[output_dir]}"
