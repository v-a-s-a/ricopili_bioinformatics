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
formatted_input = os.path.join(config["output_dir"], "formated_input.daner")


rule all:
    input:
        final_output

rule format_input_daner:
    input:
        config["daner"]
    output:
        formatted_input
    run:
        with open(output[0], 'w') as output_conn, open(input[0]) as input_conn:
            header = next(input_conn).split()
            header_index = {field: index for index, field in enumerate(header)}
            BP_index = header_index["BP"]

            new_header = header
            new_header[BP_index] = "BP1"
            new_header.insert(BP_index + 1, "BP2")

            output_conn.write('\t'.join(new_header) + '\n')
            for line in input_conn:
                line = line.split()
                line.insert(BP_index + 1, line[BP_index])
                output_conn.write('\t'.join(line) + '\n')


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
        formatted_input,
        rules.load_reference_data.output,
        rules.load_gene_data.output
    output:
        final_output
    shell:
        "java -jar {region_annotator_jar} -input {input[0]} -output {output} -iformat TSV -db {config[output_dir]}"
