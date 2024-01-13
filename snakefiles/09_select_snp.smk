#configfile: "config.yaml"
import os
samples_dir = config["samples_dir"]
output_dir = config["output_dir"]
reference_file = config["reference_genome"]

# samples = []
# for file in os.listdir(samples_dir):
#     if file.endswith("_1.fastq.gz"):
#         sample = file.replace("_clean_1.fastq.gz", "")
#         samples.append(sample)
rule select_snp:
    input:
        all_vcf=f"{output_dir}/vcf/all.vcf.gz",
        ref=f"{reference_file}"
    output:
        snp_vcf=f"{output_dir}/vcf/all.snp.vcf.gz"
    threads: 4
    log:
        "logs/select_snp.log"
    shell:
        """
        gatk SelectVariants -R {input.ref} -v {input.all_vcf} -selectType SNP -o {output.snp_vcf} > {log}
        """

rule all_select_snp:
    input:
        f"{output_dir}/vcf/all.snp.vcf.gz"