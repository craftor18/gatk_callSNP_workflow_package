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
        index5=f"{reference_file}.pac",
        dict=f"{reference_file}.dict".strip('.fasta')
    threads: 4
    shell:
        """
        bwa-mem2 index {input.ref} 
        gatk CreateSequenceDictionary -R {input.ref} -O {output.dict}
        samtools faidx {input.ref}
        """
rule all_ref_index:
    input:
        expand(f"{reference_file}.0123"),
        expand(f"{reference_file}.amb"),
        expand(f"{reference_file}.ann"),
        expand(f"{reference_file}.bwt.2bit.64"),
        expand(f"{reference_file}.pac"),
        expand(f"{reference_file}.dict".strip('.fasta')),
        expand(f"{reference_file}.fai")
