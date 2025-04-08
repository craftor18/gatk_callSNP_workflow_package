"""
SNP选择步骤，从VCF文件中提取SNP
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command
from ..utils.file_utils import ensure_directory

class SelectSnp(BaseStep):
    """SNP选择步骤，使用GATK SelectVariants从VCF文件中提取SNP"""
    
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
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["gatk"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        input_files = [self.reference_file]
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_files.append(os.path.join(vcf_dir, "all.filtered.vcf.gz"))
        return input_files
        
    def get_output_files(self):
        """获取输出文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "all.snp.vcf.gz")]
    
    def execute(self):
        """执行SNP选择步骤"""
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp", "select_snp")
        ensure_directory(temp_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "select_snp")
        ensure_directory(logs_dir)
        
        # 输入文件
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_vcf = os.path.join(vcf_dir, "all.filtered.vcf.gz")
        
        # 确保输入文件存在
        if not os.path.exists(input_vcf):
            filtered_vcf = os.path.join(vcf_dir, "all.vcf.gz")
            if os.path.exists(filtered_vcf):
                self.logger.warning(f"Filtered VCF not found, using unfiltered VCF: {filtered_vcf}")
                input_vcf = filtered_vcf
            else:
                self.logger.error(f"Input VCF file not found: {input_vcf}")
                return False
        
        # 输出文件
        output_vcf = os.path.join(vcf_dir, "all.snp.vcf.gz")
        
        # 检查输出文件是否已存在
        if os.path.exists(output_vcf):
            self.logger.info("SNP VCF already exists, skipping")
            return True
            
        # 日志文件
        log_file = os.path.join(logs_dir, "select_snp.log")
        
        # GATK SelectVariants命令
        cmd = (
            f"gatk --java-options \"{self.java_options} -Djava.io.tmpdir={temp_dir}\" "
            f"SelectVariants "
            f"-R {self.reference_file} "
            f"-V {input_vcf} "
            f"-O {output_vcf} "
            f"--select-type SNP"
        )
        
        # 执行命令
        self.logger.info("Running SelectVariants to extract SNPs")
        
        result = run_command(cmd, log_file=log_file)
        if result.returncode != 0:
            self.logger.error("Failed to select SNPs")
            return False
            
        self.logger.info("Successfully selected SNPs")
        return True 