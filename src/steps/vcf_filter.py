"""
VCF过滤步骤，对VCF文件进行过滤
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command
from ..utils.file_utils import ensure_directory

class VcfFilter(BaseStep):
    """VCF过滤步骤，使用GATK VariantFiltration对VCF文件进行过滤"""
    
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
        self.filter_params = config.get(
            "gatk_variant_filtration_params", 
            "--filter-expression 'QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0 || SOR > 3.0' --filter-name 'hard_filter'"
        )
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["gatk"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        input_files = [self.reference_file]
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_files.append(os.path.join(vcf_dir, "all.vcf.gz"))
        return input_files
        
    def get_output_files(self):
        """获取输出文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "all.filtered.vcf.gz")]
    
    def execute(self):
        """执行VCF过滤步骤"""
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp", "vcf_filter")
        ensure_directory(temp_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "vcf_filter")
        ensure_directory(logs_dir)
        
        # 输入文件
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_vcf = os.path.join(vcf_dir, "all.vcf.gz")
        
        # 确保输入文件存在
        if not os.path.exists(input_vcf):
            self.logger.error(f"Input file not found: {input_vcf}")
            return False
        
        # 输出文件
        output_vcf = os.path.join(vcf_dir, "all.filtered.vcf.gz")
        
        # 检查输出文件是否已存在
        if os.path.exists(output_vcf):
            self.logger.info("Filtered VCF already exists, skipping")
            return True
            
        # 日志文件
        log_file = os.path.join(logs_dir, "vcf_filter.log")
        
        # GATK VariantFiltration命令
        cmd = (
            f"gatk --java-options \"{self.java_options} -Djava.io.tmpdir={temp_dir}\" "
            f"VariantFiltration "
            f"-R {self.reference_file} "
            f"-V {input_vcf} "
            f"-O {output_vcf} "
            f"{self.filter_params}"
        )
        
        # 执行命令
        self.logger.info("Running VariantFiltration")
        
        result = run_command(cmd, log_file=log_file)
        if result.returncode != 0:
            self.logger.error("Failed to filter VCF")
            return False
            
        self.logger.info("Successfully filtered VCF")
        return True 