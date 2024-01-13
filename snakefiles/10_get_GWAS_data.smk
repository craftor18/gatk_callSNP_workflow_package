#configfile: "config.yaml"
import os
pheno = config['phenotype_file']
output_dir = config["output_dir"]

rule vcf_to_plink:
    input:
        input_vcf=f"{output_dir}/vcf/all.snp.vcf.gz"
    output:
        output_plink=f"{output_dir}/GWAS/all"
    threads: 4
    log:
        "logs/vcf_to_plink.log"
    shell:
        """
        plink2 --vcf  auratus_eff.ID.vcf.gz --chr-set  50 --geno 0.1 --mind 0.1 --maf 0.01 --hwe 1e-4  --make-bed --export ped --allow-extra-chr  --out auratus
        """