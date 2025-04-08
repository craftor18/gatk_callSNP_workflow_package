"""
标记重复步骤，处理PCR重复序列
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command, run_parallel_commands
from ..utils.file_utils import ensure_directory

class MarkDuplicates(BaseStep):
    """标记重复步骤，使用GATK MarkDuplicates标记PCR重复序列"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.output_dir = config.get("output_dir")
        self.java_options = config.get("gatk_java_options", "-Xmx4g")
        self.threads_per_job = config.get("threads_per_job", 4)
        self.max_parallel_jobs = config.get("max_parallel_jobs", 3)
        
        # 获取样本列表 - 基于sorted_reads目录中的BAM文件
        sorted_reads_dir = os.path.join(self.output_dir, "sorted_reads")
        self.samples = []
        if os.path.exists(sorted_reads_dir):
            for file in os.listdir(sorted_reads_dir):
                if file.endswith(".bam"):
                    sample = file.replace(".bam", "")
                    self.samples.append(sample)
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["gatk"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        sorted_reads_dir = os.path.join(self.output_dir, "sorted_reads")
        return [os.path.join(sorted_reads_dir, f"{sample}.bam") 
                for sample in self.samples]
        
    def get_output_files(self):
        """获取输出文件列表"""
        marked_dup_dir = os.path.join(self.output_dir, "marked_duplicates")
        output_files = []
        for sample in self.samples:
            output_files.append(os.path.join(marked_dup_dir, f"{sample}.bam"))
            output_files.append(os.path.join(marked_dup_dir, f"{sample}.metrics.txt"))
        return output_files
    
    def execute(self):
        """执行标记重复步骤"""
        # 创建输出目录
        marked_dup_dir = os.path.join(self.output_dir, "marked_duplicates")
        ensure_directory(marked_dup_dir)
        
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp")
        ensure_directory(temp_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "mark_duplicates")
        ensure_directory(logs_dir)
        
        self.logger.info(f"Marking duplicates for {len(self.samples)} samples")
        
        # 准备命令列表
        commands = []
        for sample in self.samples:
            # 输入文件
            input_bam = os.path.join(self.output_dir, "sorted_reads", f"{sample}.bam")
            
            # 输出文件
            output_bam = os.path.join(marked_dup_dir, f"{sample}.bam")
            metrics_file = os.path.join(marked_dup_dir, f"{sample}.metrics.txt")
            
            # 临时目录
            sample_temp_dir = os.path.join(temp_dir, f"markdup_{sample}")
            ensure_directory(sample_temp_dir)
            
            # 日志文件
            log_file = os.path.join(logs_dir, f"{sample}.log")
            
            # GATK MarkDuplicates命令
            cmd = (
                f"gatk --java-options \"{self.java_options}\" MarkDuplicates "
                f"-I {input_bam} "
                f"-O {output_bam} "
                f"-M {metrics_file} "
                f"--TMP_DIR {sample_temp_dir} "
                f"--CREATE_INDEX true "
                f"--VALIDATION_STRINGENCY SILENT"
            )
            
            commands.append((cmd, log_file, self.threads_per_job))
        
        # 是否需要并行处理
        if self.max_parallel_jobs > 1 and len(commands) > 1:
            self.logger.info(f"Running MarkDuplicates in parallel with {self.max_parallel_jobs} jobs")
            results = run_parallel_commands(commands, max_workers=self.max_parallel_jobs)
            
            # 检查结果
            success = True
            for i, result in enumerate(results):
                if result is None or result.returncode != 0:
                    self.logger.error(f"MarkDuplicates failed for sample {self.samples[i]}")
                    success = False
                    
            return success
        else:
            # 串行处理
            self.logger.info("Running MarkDuplicates sequentially")
            for i, (cmd, log_file, threads) in enumerate(commands):
                self.logger.info(f"Marking duplicates for sample {self.samples[i]} ({i+1}/{len(self.samples)})")
                result = run_command(cmd, log_file=log_file, threads=threads)
                if result.returncode != 0:
                    self.logger.error(f"MarkDuplicates failed for sample {self.samples[i]}")
                    return False
                    
            return True 