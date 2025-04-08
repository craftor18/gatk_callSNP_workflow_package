"""
SAM文件排序步骤，将BWA比对输出的SAM文件排序为BAM文件
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command, run_parallel_commands
from ..utils.file_utils import get_sample_list, ensure_directory

class SortSam(BaseStep):
    """SAM文件排序步骤，使用samtools将SAM文件排序并转换为BAM格式"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.output_dir = config.get("output_dir")
        self.threads_per_job = config.get("threads_per_job", 4)
        self.max_parallel_jobs = config.get("max_parallel_jobs", 3)
        
        # 获取样本列表 - 基于mapped_reads目录中的SAM文件
        mapped_reads_dir = os.path.join(self.output_dir, "mapped_reads")
        self.samples = []
        if os.path.exists(mapped_reads_dir):
            for file in os.listdir(mapped_reads_dir):
                if file.endswith(".sam"):
                    sample = file.replace(".sam", "")
                    self.samples.append(sample)
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["samtools"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        mapped_reads_dir = os.path.join(self.output_dir, "mapped_reads")
        return [os.path.join(mapped_reads_dir, f"{sample}.sam") 
                for sample in self.samples]
        
    def get_output_files(self):
        """获取输出文件列表"""
        sorted_reads_dir = os.path.join(self.output_dir, "sorted_reads")
        return [os.path.join(sorted_reads_dir, f"{sample}.bam") 
                for sample in self.samples]
    
    def execute(self):
        """执行SAM排序步骤"""
        # 创建输出目录
        sorted_reads_dir = os.path.join(self.output_dir, "sorted_reads")
        ensure_directory(sorted_reads_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "sort_sam")
        ensure_directory(logs_dir)
        
        self.logger.info(f"Sorting SAM files for {len(self.samples)} samples")
        
        # 准备命令列表
        commands = []
        for sample in self.samples:
            # 输入文件
            input_sam = os.path.join(self.output_dir, "mapped_reads", f"{sample}.sam")
            
            # 输出文件
            output_bam = os.path.join(sorted_reads_dir, f"{sample}.bam")
            
            # 日志文件
            log_file = os.path.join(logs_dir, f"{sample}.log")
            
            # Samtools命令
            cmd = f"samtools sort -@ {self.threads_per_job - 1} -o {output_bam} {input_sam}"
            
            commands.append((cmd, log_file, self.threads_per_job))
        
        # 是否需要并行处理
        if self.max_parallel_jobs > 1 and len(commands) > 1:
            self.logger.info(f"Running SAM sorting in parallel with {self.max_parallel_jobs} jobs")
            results = run_parallel_commands(commands, max_workers=self.max_parallel_jobs)
            
            # 检查结果
            success = True
            for i, result in enumerate(results):
                if result is None or result.returncode != 0:
                    self.logger.error(f"SAM sorting failed for sample {self.samples[i]}")
                    success = False
                    
            return success
        else:
            # 串行处理
            self.logger.info("Running SAM sorting sequentially")
            for i, (cmd, log_file, threads) in enumerate(commands):
                self.logger.info(f"Sorting sample {self.samples[i]} ({i+1}/{len(self.samples)})")
                result = run_command(cmd, log_file=log_file, threads=threads)
                if result.returncode != 0:
                    self.logger.error(f"SAM sorting failed for sample {self.samples[i]}")
                    return False
                    
            return True 