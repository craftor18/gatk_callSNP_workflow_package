"""
主流程控制模块，负责组织和执行各个步骤
"""
import os
import time
from .config_manager import ConfigManager
from .logger import Logger
from .steps import *
from typing import Dict, Any, Optional, List
from pathlib import Path
from .utils.cmd_utils import CommandExecutor

class Pipeline:
    """SNP Calling Pipeline主流程控制类"""
    
    def __init__(self, config_file, work_dir):
        """
        初始化流程控制
        
        参数:
            config_file (str): 配置文件路径
            work_dir (str): 工作目录
        """
        # 初始化日志
        log_dir = os.path.join(work_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"pipeline_{time.strftime('%Y%m%d_%H%M%S')}.log")
        self.logger = Logger(log_file)
        
        # 加载配置
        self.logger.info(f"Loading configuration from {config_file}")
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_config()
        self.config["work_dir"] = work_dir
        
        # 步骤映射
        self.steps = {
            "ref_index": RefIndex,
            "bwa_map": BwaMap,
            "sort_sam": SortSam,
            "mark_duplicates": MarkDuplicates,
            "index_bam": IndexBam,
            "haplotype_caller": HaplotypeCaller,
            "combine_gvcfs": CombineGvcfs,
            "genotype_gvcfs": GenotypeGvcfs,
            "vcf_filter": VcfFilter,
            "select_snp": SelectSnp,
            "soft_filter_snp": SoftFilterSnp,
            "get_gwas_data": GetGwasData
        }
        
        # 步骤顺序
        self.step_order = [
            "ref_index",
            "bwa_map",
            "sort_sam",
            "mark_duplicates",
            "index_bam",
            "haplotype_caller",
            "combine_gvcfs",
            "genotype_gvcfs",
            "vcf_filter",
            "select_snp",
            "soft_filter_snp",
            "get_gwas_data"
        ]
        
        self.logger.info(f"Pipeline initialized with {len(self.steps)} steps")
        
        self.cmd_executor = CommandExecutor()
        
    def run_step(self, step_name):
        """
        运行指定步骤
        
        参数:
            step_name (str): 步骤名称
            
        返回:
            bool: 运行结果
        """
        if step_name not in self.steps:
            self.logger.error(f"Unknown step: {step_name}")
            raise ValueError(f"Unknown step: {step_name}")
            
        # 创建步骤实例
        step_class = self.steps[step_name]
        step = step_class(self.config, self.logger)
        
        # 执行步骤
        try:
            self.logger.info(f"Running step: {step_name}")
            result = step.run()
            if result:
                self.logger.info(f"Step {step_name} completed successfully")
            else:
                self.logger.error(f"Step {step_name} failed")
            return result
        except Exception as e:
            self.logger.error(f"Error in step {step_name}: {str(e)}")
            raise
        
    def run_all(self):
        """
        运行所有步骤
        
        返回:
            bool: 是否全部成功
        """
        self.logger.info("Starting full pipeline")
        start_time = time.time()
        
        for step_name in self.step_order:
            step_start = time.time()
            try:
                result = self.run_step(step_name)
                if not result:
                    self.logger.error(f"Pipeline stopped at step {step_name}")
                    return False
                step_end = time.time()
                self.logger.info(f"Step {step_name} completed in {step_end - step_start:.2f} seconds")
            except Exception as e:
                self.logger.error(f"Pipeline failed at step {step_name}: {str(e)}")
                return False
                
        end_time = time.time()
        self.logger.info(f"Full pipeline completed in {end_time - start_time:.2f} seconds")
        return True
            
    def run_from(self, start_step):
        """
        从指定步骤开始运行
        
        参数:
            start_step (str): 起始步骤名称
            
        返回:
            bool: 是否全部成功
        """
        if start_step not in self.steps:
            self.logger.error(f"Unknown step: {start_step}")
            raise ValueError(f"Unknown step: {start_step}")
            
        self.logger.info(f"Starting pipeline from step {start_step}")
        start_time = time.time()
        
        # 找到起始步骤的索引
        try:
            start_index = self.step_order.index(start_step)
        except ValueError:
            self.logger.error(f"Step {start_step} not found in step order")
            return False
            
        # 执行从起始步骤开始的所有步骤
        for i in range(start_index, len(self.step_order)):
            step_name = self.step_order[i]
            step_start = time.time()
            try:
                result = self.run_step(step_name)
                if not result:
                    self.logger.error(f"Pipeline stopped at step {step_name}")
                    return False
                step_end = time.time()
                self.logger.info(f"Step {step_name} completed in {step_end - step_start:.2f} seconds")
            except Exception as e:
                self.logger.error(f"Pipeline failed at step {step_name}: {str(e)}")
                return False
                
        end_time = time.time()
        self.logger.info(f"Pipeline completed in {end_time - start_time:.2f} seconds")
        return True

    def _get_steps(self) -> Dict[str, Dict[str, Any]]:
        """获取所有步骤的配置"""
        return {
            "ref_index": {
                "name": "参考基因组索引",
                "command": self._get_ref_index_cmd,
                "dependencies": ["bwa", "gatk", "samtools"]
            },
            "bwa_map": {
                "name": "BWA比对",
                "command": self._get_bwa_map_cmd,
                "dependencies": ["bwa"]
            },
            "sort_sam": {
                "name": "排序SAM文件",
                "command": self._get_sort_sam_cmd,
                "dependencies": ["samtools"]
            },
            "mark_duplicates": {
                "name": "标记重复序列",
                "command": self._get_mark_duplicates_cmd,
                "dependencies": ["gatk"]
            },
            "index_bam": {
                "name": "索引BAM文件",
                "command": self._get_index_bam_cmd,
                "dependencies": ["samtools"]
            },
            "haplotype_caller": {
                "name": "GATK HaplotypeCaller",
                "command": self._get_haplotype_caller_cmd,
                "dependencies": ["gatk"]
            },
            "combine_gvcfs": {
                "name": "合并GVCF文件",
                "command": self._get_combine_gvcfs_cmd,
                "dependencies": ["gatk"]
            },
            "genotype_gvcfs": {
                "name": "基因型分型",
                "command": self._get_genotype_gvcfs_cmd,
                "dependencies": ["gatk"]
            },
            "vcf_filter": {
                "name": "VCF过滤",
                "command": self._get_vcf_filter_cmd,
                "dependencies": ["gatk"]
            },
            "select_snp": {
                "name": "选择SNP",
                "command": self._get_select_snp_cmd,
                "dependencies": ["gatk"]
            },
            "soft_filter_snp": {
                "name": "SNP软过滤",
                "command": self._get_soft_filter_snp_cmd,
                "dependencies": ["vcftools"]
            },
            "get_gwas_data": {
                "name": "获取GWAS数据",
                "command": self._get_gwas_data_cmd,
                "dependencies": ["bcftools"]
            }
        }
    
    def _get_ref_index_cmd(self) -> List[str]:
        """获取参考基因组索引命令"""
        ref = self.config.get("reference_genome")
        bwa = self.cmd_executor.which("bwa")
        gatk = self.cmd_executor.which("gatk")
        samtools = self.cmd_executor.which("samtools")
        
        return [
            bwa, "index", ref,
            "&&",
            gatk, "CreateSequenceDictionary",
            "-R", ref,
            "&&",
            samtools, "faidx", ref
        ]
    
    def _get_bwa_map_cmd(self) -> List[str]:
        """获取BWA比对命令"""
        bwa = self.cmd_executor.which("bwa")
        ref = self.config.get("reference_genome")
        samples_dir = self.config.get("samples_dir")
        output_dir = self.config.get("output_dir")
        
        return [
            bwa, "mem",
            "-t", str(self.config.get("threads_per_job")),
            ref,
            f"{samples_dir}/*.fastq.gz",
            ">", f"{output_dir}/aligned.sam"
        ]
    
    def _get_sort_sam_cmd(self) -> List[str]:
        """获取排序SAM文件命令"""
        samtools = self.cmd_executor.which("samtools")
        input_sam = f"{self.config.get('output_dir')}/aligned.sam"
        output_bam = f"{self.config.get('output_dir')}/sorted.bam"
        
        return [
            samtools, "sort",
            "-@", str(self.config.get("threads_per_job")),
            "-o", output_bam,
            input_sam
        ]
    
    def _get_mark_duplicates_cmd(self) -> List[str]:
        """获取标记重复序列命令"""
        gatk = self.cmd_executor.which("gatk")
        input_bam = f"{self.config.get('output_dir')}/sorted.bam"
        output_bam = f"{self.config.get('output_dir')}/deduplicated.bam"
        metrics = f"{self.config.get('output_dir')}/metrics.txt"
        
        return [
            gatk, "MarkDuplicates",
            "-I", input_bam,
            "-O", output_bam,
            "-M", metrics
        ]
    
    def _get_index_bam_cmd(self) -> List[str]:
        """获取索引BAM文件命令"""
        samtools = self.cmd_executor.which("samtools")
        input_bam = f"{self.config.get('output_dir')}/deduplicated.bam"
        
        return [samtools, "index", input_bam]
    
    def _get_haplotype_caller_cmd(self) -> List[str]:
        """获取HaplotypeCaller命令"""
        gatk = self.cmd_executor.which("gatk")
        ref = self.config.get("reference_genome")
        input_bam = f"{self.config.get('output_dir')}/deduplicated.bam"
        output_gvcf = f"{self.config.get('output_dir')}/raw_variants.g.vcf"
        
        return [
            gatk, "HaplotypeCaller",
            "-R", ref,
            "-I", input_bam,
            "-O", output_gvcf,
            "-ERC", "GVCF"
        ]
    
    def _get_combine_gvcfs_cmd(self) -> List[str]:
        """获取合并GVCF文件命令"""
        gatk = self.cmd_executor.which("gatk")
        ref = self.config.get("reference_genome")
        input_gvcfs = f"{self.config.get('output_dir')}/*.g.vcf"
        output_vcf = f"{self.config.get('output_dir')}/combined.vcf"
        
        return [
            gatk, "CombineGVCFs",
            "-R", ref,
            "-V", input_gvcfs,
            "-O", output_vcf
        ]
    
    def _get_genotype_gvcfs_cmd(self) -> List[str]:
        """获取基因型分型命令"""
        gatk = self.cmd_executor.which("gatk")
        ref = self.config.get("reference_genome")
        input_vcf = f"{self.config.get('output_dir')}/combined.vcf"
        output_vcf = f"{self.config.get('output_dir')}/genotyped.vcf"
        
        return [
            gatk, "GenotypeGVCFs",
            "-R", ref,
            "-V", input_vcf,
            "-O", output_vcf
        ]
    
    def _get_vcf_filter_cmd(self) -> List[str]:
        """获取VCF过滤命令"""
        gatk = self.cmd_executor.which("gatk")
        input_vcf = f"{self.config.get('output_dir')}/genotyped.vcf"
        output_vcf = f"{self.config.get('output_dir')}/filtered.vcf"
        
        return [
            gatk, "VariantFiltration",
            "-V", input_vcf,
            "-O", output_vcf,
            "--filter-expression", "QD < 2.0 || FS > 60.0 || MQ < 40.0",
            "--filter-name", "my_filter"
        ]
    
    def _get_select_snp_cmd(self) -> List[str]:
        """获取选择SNP命令"""
        gatk = self.cmd_executor.which("gatk")
        input_vcf = f"{self.config.get('output_dir')}/filtered.vcf"
        output_vcf = f"{self.config.get('output_dir')}/snps.vcf"
        
        return [
            gatk, "SelectVariants",
            "-V", input_vcf,
            "-O", output_vcf,
            "-select-type", "SNP"
        ]
    
    def _get_soft_filter_snp_cmd(self) -> List[str]:
        """获取SNP软过滤命令"""
        vcftools = self.cmd_executor.which("vcftools")
        input_vcf = f"{self.config.get('output_dir')}/snps.vcf"
        output_vcf = f"{self.config.get('output_dir')}/soft_filtered_snps.vcf"
        
        return [
            vcftools,
            "--vcf", input_vcf,
            "--max-missing", "0.9",
            "--maf", "0.05",
            "--geno", "0.1",
            "--recode",
            "--out", output_vcf
        ]
    
    def _get_gwas_data_cmd(self) -> List[str]:
        """获取GWAS数据命令"""
        bcftools = self.cmd_executor.which("bcftools")
        input_vcf = f"{self.config.get('output_dir')}/soft_filtered_snps.vcf"
        output_file = f"{self.config.get('output_dir')}/gwas_data.txt"
        
        return [
            bcftools, "query",
            "-f", "%CHROM\\t%POS\\t%REF\\t%ALT[\\t%GT]\\n",
            input_vcf,
            ">", output_file
        ] 