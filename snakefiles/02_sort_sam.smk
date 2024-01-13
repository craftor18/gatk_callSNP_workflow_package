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

rule sort_sam:
    input:
        sam=f"{output_dir}/mapped_reads/{{sample}}.sam"
    output:
        sorted_bam=f"{output_dir}/sorted_reads/{{sample}}.bam"
    threads: 4
    log:
        "logs/sort_sam/{sample}.log"
    shell:
        """
        gatk SortSam --TMP_DIR tmp/ -SO coordinate -I {input.sam} -O {output.sorted_bam} > {log}
        """

rule all_sort_sam:
    input:
        expand(f"{output_dir}/sorted_reads/{{sample}}.bam", sample=samples)
