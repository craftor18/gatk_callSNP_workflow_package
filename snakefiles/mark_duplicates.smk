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

rule mark_duplicates:
    input:
        bam=f"{output_dir}/sorted_reads/{{sample}}.bam"
    output:
        marked_bam=f"{output_dir}/marked_duplicates/{{sample}}.bam",
        metrics=f"{output_dir}/marked_duplicates/{{sample}}.metrics"
    threads: 4
    log:
        "logs/mark_duplicates/{sample}.log"
    shell:
        """
        gatk MarkDuplicates  -I {input.bam} -O {output.marked_bam} -M {output.metrics} > {log}
        """

rule all_mark_duplicates:
    input:
        expand(f"{output_dir}/marked_duplicates/{{sample}}.bam", sample=samples)
