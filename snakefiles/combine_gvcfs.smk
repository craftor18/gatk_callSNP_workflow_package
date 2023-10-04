#onfigfile: "config.yaml"
import os
samples_dir = config["samples_dir"]
output_dir = config["output_dir"]
reference_file = config["reference_genome"]

samples = []
for file in os.listdir(samples_dir):
    if file.endswith("_1.fastq.gz"):
        sample = file.replace("_clean_1.fastq.gz", "")
        samples.append(sample)

def get_gvcf_list(wildcards):
    return " ".join([f"-V {output_dir}/gvcf/{sample}.g.vcf" for sample in samples])

rule combine_gvcfs:
    input:
        gvcfs=expand(f"{output_dir}/gvcf/{{sample}}.g.vcf", sample=samples),
        ref=f"{reference_file}"
    output:
        combined_gvcf=f"{output_dir}/combined.g.vcf"
    threads: 8
    log:
        "logs/combine_gvcfs.log"
    params:
        gvcf_list=get_gvcf_list
    shell:
        """
        gatk CombineGVCFs -R {input.ref} {params.gvcf_list} -O {output.combined_gvcf} > {log}
        """

rule all_combine_gvcfs:
    input:
        f"{output_dir}/combined.g.vcf"
