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

rule haplotype_caller:
    input:
        bam=f"{output_dir}/marked_duplicates/{{sample}}.bam",
        bai=f"{output_dir}/marked_duplicates/{{sample}}.bam.bai",
        ref=f"{reference_file}"
    output:
        gvcf=f"{output_dir}/gvcf/{{sample}}.g.vcf.gz"
    threads: 4
    log:
        "logs/haplotype_caller/{sample}.log"
    shell:
        """
        gatk HaplotypeCaller -ERC GVCF --pcr-indel-model CONSERVATIVE -I {input.bam} -O {output.gvcf} -R {input.ref} > {log}
        """

rule all_haplotype_caller:
    input:
        expand(f"{output_dir}/gvcf/{{sample}}.g.vcf.gz", sample=samples)
