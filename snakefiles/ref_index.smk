#configfile: "config.yaml"
import os
samples_dir = config["samples_dir"]
output_dir = config["output_dir"]
reference_file = config["reference_genome"]
rule ref_index:
    input:
        ref=f"{reference_file}"
    output:
        index1=f"{reference_file}.0123",
        index2=f"{reference_file}.amb",
        index3=f"{reference_file}.ann",
        index4=f"{reference_file}.bwt.2bit.64",
        index5=f"{reference_file}.pac"
    threads: 4
    shell:
        """
        /home/software/bwa-mem2-2.2.1_x64-linux/bwa-mem2 index {input.ref} 
        """
rule all_ref_index:
    input:
        expand(f"{reference_file}.0123"),
        expand(f"{reference_file}.amb"),
        expand(f"{reference_file}.ann"),
        expand(f"{reference_file}.bwt.2bit.64"),
        expand(f"{reference_file}.pac")
