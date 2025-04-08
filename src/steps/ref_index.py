"""
参考基因组索引步骤
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command

class RefIndex(BaseStep):
    """参考基因组索引步骤，创建BWA索引、GATK字典和samtools索引"""
    
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
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["bwa-mem2", "gatk", "samtools"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        return [self.reference_file]
        
    def get_output_files(self):
        """获取输出文件列表"""
        # 提取参考基因组不带扩展名的基本路径
        ref_base = self.reference_file
        if ref_base.endswith(".fasta") or ref_base.endswith(".fa"):
            dict_output = os.path.splitext(ref_base)[0] + ".dict"
        else:
            dict_output = ref_base + ".dict"
            
        return [
            f"{self.reference_file}.0123",
            f"{self.reference_file}.amb",
            f"{self.reference_file}.ann",
            f"{self.reference_file}.bwt.2bit.64",
            f"{self.reference_file}.pac",
            dict_output,
            f"{self.reference_file}.fai"
        ]
    
    def execute(self):
        """执行参考基因组索引步骤"""
        log_dir = os.path.join(self.output_dir, "logs", "ref_index")
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建BWA索引
        self.logger.info(f"Creating BWA-MEM2 index for {self.reference_file}")
        bwa_cmd = f"bwa-mem2 index {self.reference_file}"
        bwa_result = run_command(
            bwa_cmd, 
            log_file=os.path.join(log_dir, "bwa_index.log"),
            threads=4
        )
        if bwa_result.returncode != 0:
            self.logger.error("BWA-MEM2 index creation failed")
            return False
        
        # 创建GATK字典
        dict_output = self.reference_file
        if dict_output.endswith(".fasta") or dict_output.endswith(".fa"):
            dict_output = os.path.splitext(dict_output)[0] + ".dict"
        else:
            dict_output = dict_output + ".dict"
            
        self.logger.info(f"Creating GATK sequence dictionary for {self.reference_file}")
        gatk_cmd = f"gatk CreateSequenceDictionary -R {self.reference_file} -O {dict_output}"
        gatk_result = run_command(
            gatk_cmd,
            log_file=os.path.join(log_dir, "gatk_dict.log")
        )
        if gatk_result.returncode != 0:
            self.logger.error("GATK dictionary creation failed")
            return False
        
        # 创建samtools索引
        self.logger.info(f"Creating samtools index for {self.reference_file}")
        samtools_cmd = f"samtools faidx {self.reference_file}"
        samtools_result = run_command(
            samtools_cmd,
            log_file=os.path.join(log_dir, "samtools_faidx.log")
        )
        if samtools_result.returncode != 0:
            self.logger.error("Samtools faidx creation failed")
            return False
            
        self.logger.info("All reference indexes created successfully")
        return True 