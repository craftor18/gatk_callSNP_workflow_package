import argparse
import os
import subprocess

# Define a dictionary that maps each workflow step to its corresponding Snakemake file
step_to_snakemake_file = {
    "step0_ref_index": "./snakefiles/00_ref_index.smk",
    "step1_bwa_map": "./snakefiles/01_bwa_map.smk",
    "step2_sort_sam": "./snakefiles/02_sort_sam.smk",
    "step3_mark_duplicates": "./snakefiles/03_mark_duplicates.smk",
    "step4_index_bam":"./snakefiles/04_index_bam.smk",
    "step5_haplotype_caller":"./snakefiles/05_haplotype_caller.smk",
    "step6_combine_gvcfs":"./snakefiles/06_combine_gvcfs.smk",
    "step7_genotype_gvcfs":"./snakefiles/07_genotype_gvcfs.smk",
    "step8_vcf_filter":"./snakefiles/08_vcf_filter.smk",
    "step9_select_snp":"./snakefiles/09_select_snp.smk",
    "step10_get_GWAS_data":"./snakefiles/10_get_GWAS_data.smk"
}

# Define a function that runs Snakemake with customizable parameters
def run_snakemake(step, snakemake_file, config_file, work_dir):
    # command = f"snakemake --snakefile {snakemake_file} --configfile {config_file} --directory {work_dir} -np  --latency-wait 60  --cores 10  --dag all_{step} | dot -Tpdf > dag.pdf"
    command = f"nohup snakemake --snakefile {snakemake_file} --configfile {config_file} --directory {work_dir} --latency-wait 60  --cores 10 all_{step} > {work_dir}/{step}.log &"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully executed {snakemake_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {snakemake_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Snakemake workflows with customizable parameters")
    parser.add_argument("step", choices=step_to_snakemake_file.keys(), help="Select a workflow step")
    parser.add_argument("--config_file",dest="config_file",required=True, help="Path to the configuration file (config.yaml)")
    parser.add_argument("--work_dir", dest="work_dir",required=True,help="Path of the working directory")
    args = parser.parse_args()

    selected_snakemake_file = step_to_snakemake_file[args.step]
    seq = [args.step.split('_')[1],args.step.split('_')[2]]
    selected_step = '_'.join(seq)
    run_snakemake(selected_step,selected_snakemake_file, args.config_file, args.work_dir)
