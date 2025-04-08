"""
BWA映射步骤，将测序数据比对到参考基因组
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command, run_parallel_commands
from ..utils.file_utils import get_sample_list, ensure_directory

class BwaMap(BaseStep):
    """BWA映射步骤，使用BWA-MEM2将测序数据比对到参考基因组"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.reference_file = config.get("reference_genome")
        self.samples_dir = config.get("samples_dir")
        self.output_dir = config.get("output_dir")
        self.threads_per_job = config.get("threads_per_job", 8)
        self.max_parallel_jobs = config.get("max_parallel_jobs", 3)
        
        # 获取样本列表
        self.samples = get_sample_list(
            self.samples_dir, 
            pattern="_clean_1.fastq.gz", 
            replace_with=""
        )
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["bwa-mem2"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        files = [self.reference_file]
        for sample in self.samples:
            files.append(f"{self.samples_dir}/{sample}_clean_1.fastq.gz")
            files.append(f"{self.samples_dir}/{sample}_clean_2.fastq.gz")
        return files
        
    def get_output_files(self):
        """获取输出文件列表"""
        return [os.path.join(self.output_dir, "mapped_reads", f"{sample}.sam") 
                for sample in self.samples]
    
    def execute(self):
        """执行BWA映射步骤"""
        # 创建输出目录
        mapped_reads_dir = os.path.join(self.output_dir, "mapped_reads")
        ensure_directory(mapped_reads_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "bwa_map")
        ensure_directory(logs_dir)
        
        self.logger.info(f"BWA mapping for {len(self.samples)} samples")
        
        # 准备命令列表
        commands = []
        for sample in self.samples:
            # 输入文件
            fastq1 = os.path.join(self.samples_dir, f"{sample}_clean_1.fastq.gz")
            fastq2 = os.path.join(self.samples_dir, f"{sample}_clean_2.fastq.gz")
            
            # 输出文件
            output_sam = os.path.join(mapped_reads_dir, f"{sample}.sam")
            
            # 日志文件
            log_file = os.path.join(logs_dir, f"{sample}.log")
            
            # BWA命令
            cmd = (
                f'bwa-mem2 mem -R "@RG\\tID:{sample}\\tLB:{sample}\\tPL:illumina\\tSM:{sample}" '
                f'-t {self.threads_per_job} {self.reference_file} {fastq1} {fastq2} -o {output_sam}'
            )
            
            commands.append((cmd, log_file, self.threads_per_job))
        
        # 是否需要并行处理
        if self.max_parallel_jobs > 1 and len(commands) > 1:
            self.logger.info(f"Running BWA in parallel with {self.max_parallel_jobs} jobs")
            results = run_parallel_commands(commands, max_workers=self.max_parallel_jobs)
            
            # 检查结果
            success = True
            for i, result in enumerate(results):
                if result is None or result.returncode != 0:
                    self.logger.error(f"BWA mapping failed for sample {self.samples[i]}")
                    success = False
                    
            return success
        else:
            # 串行处理
            self.logger.info("Running BWA sequentially")
            for i, (cmd, log_file, threads) in enumerate(commands):
                self.logger.info(f"Mapping sample {self.samples[i]} ({i+1}/{len(self.samples)})")
                result = run_command(cmd, log_file=log_file, threads=threads)
                if result.returncode != 0:
                    self.logger.error(f"BWA mapping failed for sample {self.samples[i]}")
                    return False
                    
            return True 