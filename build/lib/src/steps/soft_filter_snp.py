"""
SNP软过滤步骤，使用vcftools对SNP变异进行软过滤
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import CommandExecutor
from ..logger import Logger
from typing import List

class SoftFilterSNP:
    """SNP软过滤步骤"""
    
    def __init__(self, config, logger: Logger = None):
        self.config = config
        self.logger = logger or Logger(config.get_log_path())
        self.cmd_executor = CommandExecutor()
    
    def get_required_tools(self) -> List[str]:
        """获取所需的工具"""
        return ["vcftools"]
    
    def execute(self) -> bool:
        """执行软过滤"""
        try:
            # 获取输入输出文件路径
            input_vcf = f"{self.config.get('output_dir')}/snps.vcf"
            output_vcf = f"{self.config.get('output_dir')}/soft_filtered_snps.vcf"
            
            # 构建命令
            cmd = [
                self.cmd_executor.which("vcftools"),
                "--vcf", input_vcf,
                "--max-missing", "0.9",
                "--maf", "0.05",
                "--geno", "0.1",
                "--recode",
                "--out", output_vcf
            ]
            
            # 执行命令
            self.logger.info(f"执行命令: {' '.join(cmd)}")
            result = self.cmd_executor.run_command(cmd)
            
            # 压缩输出文件
            self.logger.info("压缩输出文件")
            compress_cmd = [
                "bgzip",
                f"{output_vcf}.recode.vcf"
            ]
            self.cmd_executor.run_command(compress_cmd)
            
            # 重命名文件
            self.logger.info("重命名文件")
            rename_cmd = [
                "mv",
                f"{output_vcf}.recode.vcf.gz",
                f"{output_vcf}.gz"
            ]
            self.cmd_executor.run_command(rename_cmd)
            
            self.logger.info("SNP软过滤完成")
            return True
            
        except Exception as e:
            self.logger.error(f"SNP软过滤失败: {str(e)}")
            return False 