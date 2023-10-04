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

rule bwa_map:
    input:
        fastq1=f"{samples_dir}/{{sample}}_clean_1.fastq.gz",
        fastq2=f"{samples_dir}/{{sample}}_clean_2.fastq.gz",
        ref=f"{reference_file}"
    output:
        sam=f"{output_dir}/mapped_reads/{{sample}}.sam"
    threads: 8
    log:
        "logs/bwa_map/{sample}.log"
    shell:
        """
        bwa-mem2 mem -R '@RG\\tID:{wildcards.sample}\\tLB:{wildcards.sample}\\tPL:illumina\\tSM:{wildcards.sample}' {input.ref} {input.fastq1} {input.fastq2} -o {output.sam} > {log}
        """

rule all_bwa_map:
    input:
        expand(f"{output_dir}/mapped_reads/{{sample}}.sam", sample=samples)
