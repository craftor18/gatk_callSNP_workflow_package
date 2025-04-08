"""
BAM文件索引步骤，为BAM文件创建索引
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command, run_parallel_commands
from ..utils.file_utils import ensure_directory

class IndexBam(BaseStep):
    """BAM文件索引步骤，使用samtools为BAM文件创建索引"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.output_dir = config.get("output_dir")
        self.threads_per_job = config.get("threads_per_job", 2)
        self.max_parallel_jobs = config.get("max_parallel_jobs", 4)
        
        # 获取样本列表 - 基于marked_duplicates目录中的BAM文件
        # 标记重复步骤已经可能创建了索引，但我们仍然执行此步骤以确保索引存在
        marked_duplicates_dir = os.path.join(self.output_dir, "marked_duplicates")
        self.samples = []
        if os.path.exists(marked_duplicates_dir):
            for file in os.listdir(marked_duplicates_dir):
                if file.endswith(".bam") and not file.endswith(".bai"):
                    sample = file.replace(".bam", "")
                    self.samples.append(sample)
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["samtools"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        marked_duplicates_dir = os.path.join(self.output_dir, "marked_duplicates")
        return [os.path.join(marked_duplicates_dir, f"{sample}.bam") 
                for sample in self.samples]
        
    def get_output_files(self):
        """获取输出文件列表"""
        marked_duplicates_dir = os.path.join(self.output_dir, "marked_duplicates")
        return [os.path.join(marked_duplicates_dir, f"{sample}.bam.bai") 
                for sample in self.samples]
    
    def execute(self):
        """执行BAM索引步骤"""
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "index_bam")
        ensure_directory(logs_dir)
        
        self.logger.info(f"Indexing BAM files for {len(self.samples)} samples")
        
        # 准备命令列表
        commands = []
        for sample in self.samples:
            # 输入文件
            input_bam = os.path.join(self.output_dir, "marked_duplicates", f"{sample}.bam")
            
            # 确保BAM文件存在
            if not os.path.exists(input_bam):
                self.logger.error(f"BAM file not found: {input_bam}")
                return False
            
            # 检查索引是否已存在
            expected_bai = f"{input_bam}.bai"
            if os.path.exists(expected_bai):
                self.logger.info(f"Index already exists for {sample}, skipping")
                continue
                
            # 日志文件
            log_file = os.path.join(logs_dir, f"{sample}.log")
            
            # Samtools index命令
            cmd = f"samtools index {input_bam}"
            
            commands.append((cmd, log_file, self.threads_per_job))
        
        # 如果没有需要索引的文件，直接返回成功
        if not commands:
            self.logger.info("No BAM files need indexing")
            return True
            
        # 是否需要并行处理
        if self.max_parallel_jobs > 1 and len(commands) > 1:
            self.logger.info(f"Running BAM indexing in parallel with {self.max_parallel_jobs} jobs")
            results = run_parallel_commands(commands, max_workers=self.max_parallel_jobs)
            
            # 检查结果
            success = True
            for i, result in enumerate(results):
                if result is None or result.returncode != 0:
                    sample_name = os.path.basename(commands[i][0].split()[1]).replace(".bam", "")
                    self.logger.error(f"BAM indexing failed for sample {sample_name}")
                    success = False
                    
            return success
        else:
            # 串行处理
            self.logger.info("Running BAM indexing sequentially")
            for i, (cmd, log_file, threads) in enumerate(commands):
                sample_name = os.path.basename(cmd.split()[1]).replace(".bam", "")
                self.logger.info(f"Indexing BAM for sample {sample_name} ({i+1}/{len(commands)})")
                result = run_command(cmd, log_file=log_file, threads=threads)
                if result.returncode != 0:
                    self.logger.error(f"BAM indexing failed for sample {sample_name}")
                    return False
                    
            return True 