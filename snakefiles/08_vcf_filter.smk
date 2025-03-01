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

rule vcf_filter_marked:
    input:
        raw_vcf=f"{output_dir}/vcf/combined.vcf.gz"
    output:
        filtered_vcf=f"{output_dir}/vcf/combined_filteredMarked.vcf.gz"
    threads: 4
    log:
        "logs/vcf_filter_marked.log"
    shell:
        """
        gatk VariantFiltration --filter-expression 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0' --filter-name Filter -V {input.raw_vcf} -O {output.filtered_vcf} > {log}
        """
rule vcf_filter_select:
    input:
        marked_vcf=f"{output_dir}/vcf/combined_filteredMarked.vcf.gz",
        ref=f"{reference_file}"
    output:
        select_vcf=f"{output_dir}/vcf/combined_filtered.vcf.gz"
    threads: 4
    log:
        "logs/vcf_filter_select.log"
    shell:
        """
        gatk VariantFiltration -R {input.ref} -V {input.marked_vcf} --filter-expression "QD < 2.0 || FS > 60.0 || MQ < 40.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0" --filter-name "SNP_FILTER" -O {output.select_vcf} > {log}
        """
rule vcftools_filter:
    input:
        gatk_vcf=f"{output_dir}/vcf/combined_filtered.vcf.gz",
        ref=f"{reference_file}"
    output:
        vcftools_vcf=f"{output_dir}/vcf/all.vcf.gz"
    threads: 4
    log:
        "logs/vcf_filter_select.log"
    shell:
        """
        vcftools --gzvcf {input.gatk_vcf} --recode --recode-INFO-all --stdout --maf 0.05  --max-missing 1  --minDP 2  --maxDP 1000 --minQ 30 --minGQ 0 --min-alleles 2  --max-alleles 2  | bgzip - > {output.vcftools_vcf}
        tabix {output.vcftools_vcf}
        """
rule all_vcf_filter:
    input:
        f"{output_dir}/vcf/combined_filteredMarked.vcf.gz",
        f"{output_dir}/vcf/combined_filtered.vcf.gz",
        f"{output_dir}/vcf/all.vcf.gz"
