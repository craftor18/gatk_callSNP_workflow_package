"""
GWAS数据准备步骤，从SNP数据生成GWAS分析所需的格式
"""
import os
import glob
from .base_step import BaseStep
from ..utils.cmd_utils import run_command
from ..utils.file_utils import ensure_directory

class GetGwasData(BaseStep):
    """GWAS数据准备步骤，生成GWAS分析所需的数据文件"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.output_dir = config.get("output_dir")
        self.gwas_tools_dir = config.get("gwas_tools_dir", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools/GWAS_select_trait-related_genes_from_sigcsv_gff"))
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["bcftools", "plink"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "all.snp.vcf.gz")]
        
    def get_output_files(self):
        """获取输出文件列表"""
        gwas_dir = os.path.join(self.output_dir, "gwas")
        return [
            os.path.join(gwas_dir, "snp.bed"),
            os.path.join(gwas_dir, "snp.bim"),
            os.path.join(gwas_dir, "snp.fam")
        ]
    
    def execute(self):
        """执行GWAS数据准备步骤"""
        # 创建输出目录
        gwas_dir = os.path.join(self.output_dir, "gwas")
        ensure_directory(gwas_dir)
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "get_gwas_data")
        ensure_directory(logs_dir)
        
        # 输入文件
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_vcf = os.path.join(vcf_dir, "all.snp.vcf.gz")
        
        # 确保输入文件存在
        if not os.path.exists(input_vcf):
            self.logger.error(f"Input SNP VCF file not found: {input_vcf}")
            return False
        
        # 输出文件前缀
        output_prefix = os.path.join(gwas_dir, "snp")
        
        # 检查输出文件是否已存在
        if os.path.exists(f"{output_prefix}.bed") and os.path.exists(f"{output_prefix}.bim") and os.path.exists(f"{output_prefix}.fam"):
            self.logger.info("GWAS data files already exist, skipping")
            return True
            
        # 日志文件
        log_file = os.path.join(logs_dir, "get_gwas_data.log")
        
        # 步骤1: 使用bcftools过滤和规范化VCF
        self.logger.info("Normalizing VCF with bcftools")
        
        normalized_vcf = os.path.join(gwas_dir, "normalized.vcf.gz")
        cmd1 = (
            f"bcftools norm -m-any "
            f"-Oz -o {normalized_vcf} "
            f"{input_vcf}"
        )
        
        result1 = run_command(cmd1, log_file=log_file)
        if result1.returncode != 0:
            self.logger.error("Failed to normalize VCF")
            return False
            
        # 步骤2: 使用plink转换为GWAS分析格式
        self.logger.info("Converting to PLINK format")
        
        cmd2 = (
            f"plink --vcf {normalized_vcf} "
            f"--double-id "
            f"--allow-extra-chr "
            f"--make-bed "
            f"--out {output_prefix}"
        )
        
        result2 = run_command(cmd2, log_file=log_file)
        if result2.returncode != 0:
            self.logger.error("Failed to convert to PLINK format")
            return False
        
        # 步骤3: 如果有自定义的GWAS工具脚本，则运行它
        gwas_script = os.path.join(self.gwas_tools_dir, "select_trait_related_genes.py")
        if os.path.exists(gwas_script):
            self.logger.info("Running custom GWAS analysis script")
            
            cmd3 = (
                f"python {gwas_script} "
                f"--input {output_prefix} "
                f"--out {os.path.join(gwas_dir, 'gwas_result')}"
            )
            
            result3 = run_command(cmd3, log_file=os.path.join(logs_dir, "gwas_analysis.log"))
            if result3.returncode != 0:
                self.logger.warning("GWAS analysis script did not complete successfully")
                # 不影响主流程，继续返回成功
        
        self.logger.info("Successfully prepared GWAS data")
        return True 