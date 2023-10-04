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

rule genotype_gvcfs:
    input:
        combined_gvcf=f"{output_dir}/combined.g.vcf.gz",
        ref=f"{reference_file}"
    output:
        vcf=f"{output_dir}/vcf/combined.vcf"
    threads: 8
    log:
        "logs/genotype_gvcfs.log"
    shell:
        """
        gatk GenotypeGVCFs -R {input.ref} -V {input.combined_gvcf} -O {output.vcf} > {log}
        """

rule all_genotype_gvcfs:
    input:
        f"{output_dir}/vcf/combined.vcf"
