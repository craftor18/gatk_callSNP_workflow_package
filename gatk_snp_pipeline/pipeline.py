from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import os
from .config import ConfigManager
from .logger import Logger

class Pipeline:
    """GATK SNP Calling流程控制类"""
    
    def __init__(self, config: ConfigManager, logger: Optional[Logger] = None):
        self.config = config
        self.logger = logger or Logger(config.get_log_path())
        self.steps = self._get_steps()
    
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
    
    def run_all(self) -> bool:
        """运行完整流程"""
        self.logger.info("开始运行完整流程")
        for step_name in self.steps:
            if not self.run_step(step_name):
                self.logger.error(f"步骤 {step_name} 执行失败")
                return False
        self.logger.info("流程执行完成")
        return True
    
    def run_step(self, step_name: str) -> bool:
        """运行特定步骤"""
        if step_name not in self.steps:
            self.logger.error(f"未知的步骤: {step_name}")
            return False
        
        step = self.steps[step_name]
        self.logger.info(f"开始执行步骤: {step['name']}")
        
        try:
            cmd = step["command"]()
            cmd_str = ' '.join(cmd)
            self.logger.info(f"执行命令: {cmd_str}")
            
            # 检查命令中是否包含shell操作符
            if any(op in cmd_str for op in ['&&', '||', '>', '<', '|', ';']):
                # 使用shell=True执行包含shell操作符的命令
                result = subprocess.run(
                    cmd_str,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
            else:
                # 使用普通方式执行不包含shell操作符的命令
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            self.logger.info(f"步骤 {step_name} 执行成功")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"步骤 {step_name} 执行失败: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"步骤 {step_name} 执行出错: {str(e)}")
            return False
    
    def run_from_step(self, step_name: str) -> bool:
        """从特定步骤开始运行"""
        if step_name not in self.steps:
            self.logger.error(f"未知的步骤: {step_name}")
            return False
        
        step_index = list(self.steps.keys()).index(step_name)
        for step in list(self.steps.keys())[step_index:]:
            if not self.run_step(step):
                return False
        return True
    
    def _get_ref_index_cmd(self) -> List[str]:
        """获取参考基因组索引命令"""
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        bwa = self.config.get_software_path("bwa")
        gatk = self.config.get_software_path("gatk")
        samtools = self.config.get_software_path("samtools")
        
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
        bwa = self.config.get_software_path("bwa")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        samples_dir = self.config.get("samples_dir")
        if not samples_dir:
            raise ValueError("配置文件中缺少 samples_dir 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        threads = str(self.config.get("threads", 8))
        
        # 获取样本文件列表
        # 注意: 在shell=True模式下，这里的通配符会由shell展开
        # 这里假设一个样本只有一个配对的FASTQ文件（如果是双端测序，需要修改）
        sample_files = f"{samples_dir}/*.fastq.gz"
        
        return [
            bwa, "mem",
            "-t", threads,
            "-M",  # 添加-M参数，标记短分割比对
            ref,
            sample_files,
            ">", f"{output_dir}/aligned.sam"
        ]
    
    def _get_sort_sam_cmd(self) -> List[str]:
        """获取排序SAM文件命令"""
        samtools = self.config.get_software_path("samtools")
        
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        input_sam = f"{output_dir}/aligned.sam"
        if not os.path.exists(input_sam):
            raise FileNotFoundError(f"找不到输入文件: {input_sam}")
            
        output_bam = f"{output_dir}/sorted.bam"
        threads = str(self.config.get("threads", 8))
        
        return [
            samtools, "sort",
            "-@", threads,
            "-m", "2G",  # 每个线程使用2G内存
            "-o", output_bam,
            input_sam
        ]
    
    def _get_mark_duplicates_cmd(self) -> List[str]:
        """获取标记重复序列命令"""
        gatk = self.config.get_software_path("gatk")
        
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        input_bam = f"{output_dir}/sorted.bam"
        if not os.path.exists(input_bam):
            raise FileNotFoundError(f"找不到输入文件: {input_bam}")
            
        output_bam = f"{output_dir}/deduplicated.bam"
        metrics = f"{output_dir}/duplicate_metrics.txt"
        
        return [
            gatk, "MarkDuplicates",
            "-I", input_bam,
            "-O", output_bam,
            "-M", metrics,
            "--CREATE_INDEX", "true",
            "--VALIDATION_STRINGENCY", "SILENT",
            "--REMOVE_DUPLICATES", "false"
        ]
    
    def _get_index_bam_cmd(self) -> List[str]:
        """获取索引BAM文件命令"""
        samtools = self.config.get_software_path("samtools")
        
        output_dir = self.config.get("output_dir", ".")
        input_bam = f"{output_dir}/deduplicated.bam"
        if not os.path.exists(input_bam):
            raise FileNotFoundError(f"找不到输入文件: {input_bam}")
        
        return [samtools, "index", input_bam]
    
    def _get_haplotype_caller_cmd(self) -> List[str]:
        """获取HaplotypeCaller命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        input_bam = f"{output_dir}/deduplicated.bam"
        if not os.path.exists(input_bam):
            raise FileNotFoundError(f"找不到输入文件: {input_bam}")
            
        # 检查BAM索引是否存在
        bam_index = f"{input_bam}.bai"
        if not os.path.exists(bam_index):
            self.logger.warning(f"找不到BAM索引文件: {bam_index}，可能会导致HaplotypeCaller失败")
            
        output_gvcf = f"{output_dir}/raw_variants.g.vcf"
        
        # 从配置中获取质量参数
        min_base_quality = self.config.get("gatk", {}).get("min_base_quality", 20)
        min_allele_fraction = self.config.get("gatk", {}).get("min_allele_fraction", 0.2)
        
        return [
            gatk, "HaplotypeCaller",
            "-R", ref,
            "-I", input_bam,
            "-O", output_gvcf,
            "-ERC", "GVCF",
            "--min-base-quality", str(min_base_quality),
            "--min-pruning", "1",
            "--standard-min-confidence-threshold-for-calling", "30.0",
            "--heterozygosity", "0.001",
            "--heterozygosity-stdev", "0.01",
            "--min-dangling-branch-length", "4"
        ]
    
    def _get_combine_gvcfs_cmd(self) -> List[str]:
        """获取合并GVCF文件命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # 在shell=True模式下通配符会被正确展开
        input_gvcfs = f"{output_dir}/*.g.vcf"
        output_vcf = f"{output_dir}/combined.vcf"
        
        # 在非shell模式下，我们需要手动查找所有的GVCF文件
        cmd = [
            gatk, "CombineGVCFs",
            "-R", ref,
            "-V", input_gvcfs,
            "-O", output_vcf
        ]
        
        # 添加可选参数
        if self.config.get("gatk", {}).get("convert_to_hemizygous", False):
            cmd.extend(["--convert-to-hemizygous"])
            
        return cmd
    
    def _get_genotype_gvcfs_cmd(self) -> List[str]:
        """获取基因型分型命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
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
        gatk = self.config.get_software_path("gatk")
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
        gatk = self.config.get_software_path("gatk")
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
        vcftools = self.config.get_software_path("vcftools")
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
        bcftools = self.config.get_software_path("bcftools")
        input_vcf = f"{self.config.get('output_dir')}/soft_filtered_snps.vcf"
        output_file = f"{self.config.get('output_dir')}/gwas_data.txt"
        
        return [
            bcftools, "query",
            "-f", "%CHROM\\t%POS\\t%REF\\t%ALT[\\t%GT]\\n",
            input_vcf,
            ">", output_file
        ] 