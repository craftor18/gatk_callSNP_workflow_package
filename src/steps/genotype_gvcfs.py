"""
基因型分型步骤，对合并的GVCF文件进行基因型分型
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command
from ..utils.file_utils import ensure_directory

class GenotypeGvcfs(BaseStep):
    """基因型分型步骤，使用GATK GenotypeGVCFs对合并的GVCF文件进行基因型分型"""
    
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
        self.genotype_params = config.get("gatk_genotype_gvcfs_params", "--max-alternate-alleles 2")
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["gatk"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        input_files = [self.reference_file]
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_files.append(os.path.join(vcf_dir, "cohort.g.vcf.gz"))
        return input_files
        
    def get_output_files(self):
        """获取输出文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "all.vcf.gz")]
    
    def execute(self):
        """执行基因型分型步骤"""
        # 创建输出目录
        vcf_dir = os.path.join(self.output_dir, "vcf")
        ensure_directory(vcf_dir)
        
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp", "genotype_gvcfs")
        ensure_directory(temp_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "genotype_gvcfs")
        ensure_directory(logs_dir)
        
        # 输入文件
        input_gvcf = os.path.join(vcf_dir, "cohort.g.vcf.gz")
        
        # 确保输入文件存在
        if not os.path.exists(input_gvcf):
            self.logger.error(f"Input file not found: {input_gvcf}")
            return False
        
        # 输出文件
        output_vcf = os.path.join(vcf_dir, "all.vcf.gz")
        
        # 检查输出文件是否已存在
        if os.path.exists(output_vcf):
            self.logger.info("Genotyped VCF already exists, skipping")
            return True
            
        # 日志文件
        log_file = os.path.join(logs_dir, "genotype_gvcfs.log")
        
        # GATK GenotypeGVCFs命令
        cmd = (
            f"gatk --java-options \"{self.java_options} -Djava.io.tmpdir={temp_dir}\" "
            f"GenotypeGVCFs "
            f"-R {self.reference_file} "
            f"-V {input_gvcf} "
            f"-O {output_vcf} "
            f"{self.genotype_params}"
        )
        
        # 执行命令
        self.logger.info("Running GenotypeGVCFs")
        
        result = run_command(cmd, log_file=log_file)
        if result.returncode != 0:
            self.logger.error("Failed to genotype GVCFs")
            return False
            
        self.logger.info("Successfully genotyped GVCFs")
        return True 