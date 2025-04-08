"""
合并GVCF步骤，合并多个样本的GVCF文件
"""
import os
import glob
from .base_step import BaseStep
from ..utils.cmd_utils import run_command
from ..utils.file_utils import ensure_directory

class CombineGvcfs(BaseStep):
    """合并GVCF步骤，使用GATK CombineGVCFs合并多个样本的GVCF文件"""
    
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
        self.java_options = config.get("gatk_java_options", "-Xmx8g")
        
        # 获取GVCF文件列表
        gvcf_dir = os.path.join(self.output_dir, "gvcf")
        self.gvcf_files = []
        if os.path.exists(gvcf_dir):
            self.gvcf_files = glob.glob(os.path.join(gvcf_dir, "*.g.vcf.gz"))
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["gatk"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        input_files = [self.reference_file]
        input_files.extend(self.gvcf_files)
        return input_files
        
    def get_output_files(self):
        """获取输出文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "cohort.g.vcf.gz")]
    
    def execute(self):
        """执行合并GVCF步骤"""
        # 如果没有GVCF文件，无法合并
        if not self.gvcf_files:
            self.logger.error("No GVCF files found for combining")
            return False
            
        # 创建输出目录
        vcf_dir = os.path.join(self.output_dir, "vcf")
        ensure_directory(vcf_dir)
        
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp", "combine_gvcfs")
        ensure_directory(temp_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "combine_gvcfs")
        ensure_directory(logs_dir)
        
        # 输出文件
        output_gvcf = os.path.join(vcf_dir, "cohort.g.vcf.gz")
        
        # 检查输出文件是否已存在
        if os.path.exists(output_gvcf):
            self.logger.info("Combined GVCF already exists, skipping")
            return True
            
        # 日志文件
        log_file = os.path.join(logs_dir, "combine_gvcfs.log")
        
        # 构建输入文件参数
        variant_args = ""
        for gvcf in self.gvcf_files:
            variant_args += f" --variant {gvcf}"
        
        # GATK CombineGVCFs命令
        cmd = (
            f"gatk --java-options \"{self.java_options} -Djava.io.tmpdir={temp_dir}\" "
            f"CombineGVCFs "
            f"-R {self.reference_file} "
            f"{variant_args} "
            f"-O {output_gvcf}"
        )
        
        # 执行命令
        self.logger.info(f"Combining {len(self.gvcf_files)} GVCF files")
        
        result = run_command(cmd, log_file=log_file)
        if result.returncode != 0:
            self.logger.error("Failed to combine GVCF files")
            return False
            
        self.logger.info("Successfully combined GVCF files")
        return True 