#configfile: "config.yaml"
import os
samples_dir = config["samples_dir"]
output_dir = config["output_dir"]
reference_file = config["reference_genome"]

samples = []
for file in os.listdir(samples_dir):
    if file.endswith("_1.fastq.gz"):
        sample = file.replace("_clean_1.fastq.gz", "")
        samples.append(sample)

rule index_bam:
    input:
        bam=f"{output_dir}/marked_duplicates/{{sample}}.bam"
    output:
        bai=f"{output_dir}/marked_duplicates/{{sample}}.bam.bai"
    threads: 1
    log:
        "logs/index_bam/{sample}.log"
    shell:
        """
        samtools index {input.bam} {output.bai} > {log}
        """

rule all_index_bam:
    input:
        expand(f"{output_dir}/marked_duplicates/{{sample}}.bam.bai", sample=samples)
