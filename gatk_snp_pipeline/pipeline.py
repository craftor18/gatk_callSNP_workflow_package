from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import os
import glob
import psutil
from .config import ConfigManager
from .logger import Logger

class Pipeline:
    """GATK SNP Calling流程控制类"""
    
    def __init__(self, config: ConfigManager, logger: Optional[Logger] = None):
        self.config = config
        self.logger = logger or Logger(config.get_log_path())
        self.steps = self._get_steps()
        
        # 自动优化性能参数
        self._optimize_performance_params()
    
    def _optimize_performance_params(self):
        """根据系统资源自动优化性能参数"""
        # 获取系统资源信息
        total_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False)
        total_memory_gb = psutil.virtual_memory().total / (1024 ** 3)  # 转换为GB
        
        # 记录系统资源信息
        self.logger.info(f"系统资源信息: CPU总核数={total_cores}, 物理核数={physical_cores}, 内存={total_memory_gb:.1f}GB")
        
        # 当前配置中的线程数
        current_threads = self.config.get("threads", 8)
        
        # 根据系统资源优化线程数
        if total_cores > 4:
            # 保留至少1个核心给系统
            recommended_threads = max(1, min(total_cores - 1, current_threads))
            if recommended_threads != current_threads:
                self.logger.info(f"根据系统资源优化线程数: {current_threads} -> {recommended_threads}")
                self.config.set("threads", recommended_threads)
                
        # 内存优化
        # GATK和其他工具的内存参数
        # 可用内存的70%，并保留至少2GB给系统
        available_memory_gb = max(2, total_memory_gb * 0.7)
        recommended_memory_gb = min(available_memory_gb, self.config.get("max_memory", 32))
        
        # 设置内存参数
        self.logger.info(f"设置最大内存使用: {recommended_memory_gb:.1f}GB")
        self.config.set("max_memory", recommended_memory_gb)
        
        # 为每个线程分配的内存
        memory_per_thread_gb = max(1, int(recommended_memory_gb / recommended_threads))
        self.logger.info(f"每线程内存分配: {memory_per_thread_gb}GB")
        self.config.set("memory_per_thread", memory_per_thread_gb)
    
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
        
        # 获取字典文件路径和目录
        ref_path = Path(ref)
        dict_path = ref_path.with_suffix('.dict')
        
        # 构建命令，先删除可能存在的字典文件，然后再创建新的
        return [
            f"rm -f {dict_path}",
            "&&",
            bwa, "index", ref,
            "&&",
            gatk, "CreateSequenceDictionary",
            "-R", ref,
            "-O", str(dict_path),  # 显式指定输出文件
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
        
        # 获取样本文件列表，处理通配符路径
        sample_pattern = f"{samples_dir}/*.fastq.gz"
        sample_files = glob.glob(sample_pattern)
        
        if not sample_files:
            raise FileNotFoundError(f"未找到与模式 {sample_pattern} 匹配的样本文件")
        
        # 处理多个样本的情况
        cmds = []
        for sample_file in sample_files:
            sample_name = os.path.basename(sample_file).split('.')[0]
            output_sam = f"{output_dir}/{sample_name}.sam"
            
            cmd = [
                bwa, "mem",
                "-t", threads,
                "-M",  # 添加-M参数，标记短分割比对
                ref,
                sample_file,
                ">", output_sam
            ]
            cmds.append(' '.join(cmd))
            
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_sort_sam_cmd(self) -> List[str]:
        """获取排序SAM文件命令"""
        samtools = self.config.get_software_path("samtools")
        
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有SAM文件
        sam_pattern = f"{output_dir}/*.sam"
        sam_files = glob.glob(sam_pattern)
        
        if not sam_files:
            raise FileNotFoundError(f"未找到与模式 {sam_pattern} 匹配的SAM文件")
        
        # 处理多个SAM文件的情况
        cmds = []
        for sam_file in sam_files:
            sample_name = os.path.basename(sam_file).split('.')[0]
            output_bam = f"{output_dir}/{sample_name}.sorted.bam"
            threads = str(self.config.get("threads", 8))
            memory_per_thread = str(self.config.get("memory_per_thread", 2))
            
            cmd = [
                samtools, "sort",
                "-@", threads,
                "-m", f"{memory_per_thread}G",  # 每个线程使用的内存
                "-o", output_bam,
                sam_file
            ]
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_mark_duplicates_cmd(self) -> List[str]:
        """获取标记重复序列命令"""
        gatk = self.config.get_software_path("gatk")
        
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有排序后的BAM文件
        bam_pattern = f"{output_dir}/*.sorted.bam"
        bam_files = glob.glob(bam_pattern)
        
        if not bam_files:
            raise FileNotFoundError(f"未找到与模式 {bam_pattern} 匹配的BAM文件")
        
        # 处理多个BAM文件的情况
        cmds = []
        for bam_file in bam_files:
            sample_name = os.path.basename(bam_file).split('.')[0]
            output_bam = f"{output_dir}/{sample_name}.dedup.bam"
            metrics = f"{output_dir}/{sample_name}.metrics.txt"
            
            # 设置Java最大内存
            max_memory_gb = int(self.config.get("max_memory", 32))
            java_mem = f"-Xmx{max_memory_gb}g"
            
            cmd = [
                gatk, "--java-options", f'"{java_mem}"', "MarkDuplicates",
                "-I", bam_file,
                "-O", output_bam,
                "-M", metrics,
                "--CREATE_INDEX", "true",
                "--VALIDATION_STRINGENCY", "SILENT",
                "--REMOVE_DUPLICATES", "false"
            ]
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_index_bam_cmd(self) -> List[str]:
        """获取索引BAM文件命令"""
        samtools = self.config.get_software_path("samtools")
        
        output_dir = self.config.get("output_dir", ".")
        
        # 获取所有去重后的BAM文件
        bam_pattern = f"{output_dir}/*.dedup.bam"
        bam_files = glob.glob(bam_pattern)
        
        if not bam_files:
            raise FileNotFoundError(f"未找到与模式 {bam_pattern} 匹配的BAM文件")
        
        # 构建索引命令
        cmds = []
        for bam_file in bam_files:
            cmd = [samtools, "index", bam_file]
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_haplotype_caller_cmd(self) -> List[str]:
        """获取HaplotypeCaller命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有去重和索引后的BAM文件
        bam_pattern = f"{output_dir}/*.dedup.bam"
        bam_files = glob.glob(bam_pattern)
        
        if not bam_files:
            raise FileNotFoundError(f"未找到与模式 {bam_pattern} 匹配的BAM文件")
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        # 处理多个BAM文件的情况
        cmds = []
        for bam_file in bam_files:
            sample_name = os.path.basename(bam_file).split('.')[0]
            output_gvcf = f"{output_dir}/{sample_name}.g.vcf"
            
            # 确保参数格式正确，使用空格分隔每个参数
            cmd = [
                gatk, "--java-options", f'"{java_mem}"', "HaplotypeCaller",
                "-R", ref,
                "-I", bam_file,
                "-O", output_gvcf,
                "--sample-name", sample_name
            ]
            
            # 添加额外参数，确保它们是正确分隔的独立参数
            cmd.extend(["--emit-ref-confidence", "GVCF"])
            
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_combine_gvcfs_cmd(self) -> List[str]:
        """获取合并GVCF文件命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # 获取所有GVCF文件
        gvcf_pattern = f"{output_dir}/*.g.vcf"
        gvcf_files = glob.glob(gvcf_pattern)
        
        if not gvcf_files:
            raise FileNotFoundError(f"未找到与模式 {gvcf_pattern} 匹配的GVCF文件")
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        # 构建命令，为每个GVCF文件添加-V参数
        cmd = [gatk, "--java-options", f'"{java_mem}"', "CombineGVCFs", "-R", ref]
        
        for gvcf_file in gvcf_files:
            cmd.extend(["-V", gvcf_file])
        
        cmd.extend(["-O", f"{output_dir}/combined.vcf"])
        
        # 添加可选参数
        if self.config.get("gatk", {}).get("convert_to_hemizygous", False):
            cmd.extend(["--convert-to-hemizygous"])
            
        return cmd
    
    def _get_genotype_gvcfs_cmd(self) -> List[str]:
        """获取基因型分型命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/combined.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_vcf = f"{output_dir}/genotyped.vcf"
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        return [
            gatk, "--java-options", f'"{java_mem}"', "GenotypeGVCFs",
            "-R", ref,
            "-V", input_vcf,
            "-O", output_vcf
        ]
    
    def _get_vcf_filter_cmd(self) -> List[str]:
        """获取VCF过滤命令"""
        gatk = self.config.get_software_path("gatk")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/genotyped.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_vcf = f"{output_dir}/filtered.vcf"
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        return [
            gatk, "--java-options", f'"{java_mem}"', "VariantFiltration",
            "-V", input_vcf,
            "-O", output_vcf,
            "--filter-expression", "QD < 2.0 || FS > 60.0 || MQ < 40.0",
            "--filter-name", "my_filter"
        ]
    
    def _get_select_snp_cmd(self) -> List[str]:
        """获取选择SNP命令"""
        gatk = self.config.get_software_path("gatk")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/filtered.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_vcf = f"{output_dir}/snps.vcf"
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        return [
            gatk, "--java-options", f'"{java_mem}"', "SelectVariants",
            "-V", input_vcf,
            "-O", output_vcf,
            "-select-type", "SNP"
        ]
    
    def _get_soft_filter_snp_cmd(self) -> List[str]:
        """获取SNP软过滤命令"""
        vcftools = self.config.get_software_path("vcftools")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/snps.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_prefix = f"{output_dir}/soft_filtered_snps"
        
        # 设置线程数
        threads = str(self.config.get("threads", 8))
        
        return [
            vcftools,
            "--vcf", input_vcf,
            "--max-missing", "0.9",
            "--maf", "0.05",
            "--geno", "0.1",
            "--recode",
            "--recode-INFO-all",
            "--out", output_prefix,
            "--threads", threads
        ]
    
    def _get_gwas_data_cmd(self) -> List[str]:
        """获取GWAS数据命令"""
        bcftools = self.config.get_software_path("bcftools")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/soft_filtered_snps.recode.vcf"
        if not os.path.exists(input_vcf):
            # 尝试使用另一个可能的文件名
            input_vcf = f"{output_dir}/soft_filtered_snps.vcf"
            if not os.path.exists(input_vcf):
                raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_file = f"{output_dir}/gwas_data.txt"
        
        # 设置线程数
        threads = str(self.config.get("threads", 8))
        
        return [
            bcftools, "query",
            "-f", "%CHROM\\t%POS\\t%REF\\t%ALT[\\t%GT]\\n",
            "--threads", threads,
            input_vcf,
            ">", output_file
        ] 