"""
HaplotypeCaller步骤，使用GATK HaplotypeCaller从BAM文件中检测变异
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command, run_parallel_commands
from ..utils.file_utils import ensure_directory

class HaplotypeCaller(BaseStep):
    """HaplotypeCaller步骤，使用GATK HaplotypeCaller从BAM文件中检测变异并生成GVCF文件"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.reference_file = config.get("reference_genome")
        self.output_dir = config.get("output_dir")
        self.java_options = config.get("gatk_java_options", "-Xmx4g")
        self.hc_params = config.get("gatk_haplotype_caller_params", "--pcr-indel-model CONSERVATIVE -ERC GVCF")
        self.threads_per_job = config.get("threads_per_job", 4)
        self.max_parallel_jobs = config.get("max_parallel_jobs", 3)
        
        # 获取样本列表 - 基于marked_duplicates目录中的BAM文件
        marked_duplicates_dir = os.path.join(self.output_dir, "marked_duplicates")
        self.samples = []
        if os.path.exists(marked_duplicates_dir):
            for file in os.listdir(marked_duplicates_dir):
                if file.endswith(".bam") and not file.endswith(".bai"):
                    sample = file.replace(".bam", "")
                    self.samples.append(sample)
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["gatk"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        marked_duplicates_dir = os.path.join(self.output_dir, "marked_duplicates")
        input_files = [self.reference_file]
        
        for sample in self.samples:
            input_files.append(os.path.join(marked_duplicates_dir, f"{sample}.bam"))
            input_files.append(os.path.join(marked_duplicates_dir, f"{sample}.bam.bai"))
            
        return input_files
        
    def get_output_files(self):
        """获取输出文件列表"""
        gvcf_dir = os.path.join(self.output_dir, "gvcf")
        return [os.path.join(gvcf_dir, f"{sample}.g.vcf.gz") 
                for sample in self.samples]
    
    def execute(self):
        """执行HaplotypeCaller步骤"""
        # 创建输出目录
        gvcf_dir = os.path.join(self.output_dir, "gvcf")
        ensure_directory(gvcf_dir)
        
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp")
        ensure_directory(temp_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "haplotype_caller")
        ensure_directory(logs_dir)
        
        self.logger.info(f"Running HaplotypeCaller for {len(self.samples)} samples")
        
        # 准备命令列表
        commands = []
        for sample in self.samples:
            # 输入文件
            input_bam = os.path.join(self.output_dir, "marked_duplicates", f"{sample}.bam")
            
            # 输出文件
            output_gvcf = os.path.join(gvcf_dir, f"{sample}.g.vcf.gz")
            
            # 检查输出文件是否已存在
            if os.path.exists(output_gvcf):
                self.logger.info(f"Output GVCF already exists for {sample}, skipping")
                continue
                
            # 临时目录
            sample_temp_dir = os.path.join(temp_dir, f"hc_{sample}")
            ensure_directory(sample_temp_dir)
            
            # 日志文件
            log_file = os.path.join(logs_dir, f"{sample}.log")
            
            # GATK HaplotypeCaller命令
            cmd = (
                f"gatk --java-options \"{self.java_options} -Djava.io.tmpdir={sample_temp_dir}\" "
                f"HaplotypeCaller "
                f"-R {self.reference_file} "
                f"-I {input_bam} "
                f"-O {output_gvcf} "
                f"{self.hc_params}"
            )
            
            commands.append((cmd, log_file, self.threads_per_job))
        
        # 如果没有需要处理的样本，直接返回成功
        if not commands:
            self.logger.info("No samples need processing")
            return True
            
        # 是否需要并行处理
        if self.max_parallel_jobs > 1 and len(commands) > 1:
            self.logger.info(f"Running HaplotypeCaller in parallel with {self.max_parallel_jobs} jobs")
            results = run_parallel_commands(commands, max_workers=self.max_parallel_jobs)
            
            # 检查结果
            success = True
            for i, result in enumerate(results):
                if result is None or result.returncode != 0:
                    sample_name = os.path.basename(commands[i][0].split("-I ")[1].split()[0]).replace(".bam", "")
                    self.logger.error(f"HaplotypeCaller failed for sample {sample_name}")
                    success = False
                    
            return success
        else:
            # 串行处理
            self.logger.info("Running HaplotypeCaller sequentially")
            for i, (cmd, log_file, threads) in enumerate(commands):
                sample_name = cmd.split("-I ")[1].split()[0].split("/")[-1].replace(".bam", "")
                self.logger.info(f"Running HaplotypeCaller for sample {sample_name} ({i+1}/{len(commands)})")
                result = run_command(cmd, log_file=log_file, threads=threads)
                if result.returncode != 0:
                    self.logger.error(f"HaplotypeCaller failed for sample {sample_name}")
                    return False
                    
            return True 