"""
SNP软过滤步骤，使用vcftools对SNP变异进行软过滤
"""
import os
from .base_step import BaseStep
from ..utils.cmd_utils import run_command
from ..utils.file_utils import ensure_directory

class SoftFilterSnp(BaseStep):
    """SNP软过滤步骤，使用vcftools对SNP变异进行软过滤，直接删除不符合条件的变异"""
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        super().__init__(config, logger)
        self.output_dir = config.get("output_dir")
        
        # SNP软过滤参数，可以在配置文件中指定或使用默认值
        try:
            self.max_missing = float(config.get("snp_soft_filter_max_missing", 0.2))  # 最大缺失率
            self.maf = float(config.get("snp_soft_filter_maf", 0.05))  # 最小次等位基因频率
            self.geno = float(config.get("snp_soft_filter_geno", 0.1))  # 最大基因型缺失率
            
            # 验证参数范围
            if not (0 <= self.max_missing <= 1):
                logger.warning(f"max_missing参数值超出范围(0-1)：{self.max_missing}，使用默认值0.2")
                self.max_missing = 0.2
            if not (0 <= self.maf <= 1):
                logger.warning(f"maf参数值超出范围(0-1)：{self.maf}，使用默认值0.05")
                self.maf = 0.05
            if not (0 <= self.geno <= 1):
                logger.warning(f"geno参数值超出范围(0-1)：{self.geno}，使用默认值0.1")
                self.geno = 0.1
        except ValueError:
            logger.warning("过滤参数类型错误，使用默认值")
            self.max_missing = 0.2  # 最大缺失率
            self.maf = 0.05  # 最小次等位基因频率
            self.geno = 0.1  # 最大基因型缺失率
        
    def get_required_tools(self):
        """获取步骤依赖的工具列表"""
        return ["vcftools", "bgzip", "tabix"]
    
    def get_input_files(self):
        """获取输入文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "all.snp.vcf.gz")]
        
    def get_output_files(self):
        """获取输出文件列表"""
        vcf_dir = os.path.join(self.output_dir, "vcf")
        return [os.path.join(vcf_dir, "all.snp.filtered.vcf.gz")]
    
    def execute(self):
        """执行SNP软过滤步骤"""
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp", "soft_filter_snp")
        try:
            ensure_directory(temp_dir)
        except Exception as e:
            self.logger.error(f"创建临时目录失败: {e}")
            return False
        
        # 创建日志目录
        logs_dir = os.path.join(self.output_dir, "logs", "soft_filter_snp")
        try:
            ensure_directory(logs_dir)
        except Exception as e:
            self.logger.error(f"创建日志目录失败: {e}")
            return False
        
        # 输入文件
        vcf_dir = os.path.join(self.output_dir, "vcf")
        input_vcf = os.path.join(vcf_dir, "all.snp.vcf.gz")
        
        # 确保输入文件存在
        if not os.path.exists(input_vcf):
            self.logger.error(f"输入文件不存在: {input_vcf}")
            return False
        
        # 检查输入文件是否可读
        if not os.access(input_vcf, os.R_OK):
            self.logger.error(f"输入文件无法读取: {input_vcf}")
            return False
        
        # 检查输出目录是否可写
        if not os.access(vcf_dir, os.W_OK):
            self.logger.error(f"输出目录没有写入权限: {vcf_dir}")
            return False
        
        # 输出文件
        output_vcf = os.path.join(vcf_dir, "all.snp.filtered.vcf.gz")
        
        # 检查输出文件是否已存在
        if os.path.exists(output_vcf):
            self.logger.info("软过滤后的SNP VCF文件已存在，跳过")
            return True
        
        # 日志文件
        log_file = os.path.join(logs_dir, "soft_filter_snp.log")
        
        # vcftools命令 - 软过滤
        cmd = (
            f"vcftools --gzvcf {input_vcf} "
            f"--max-missing {self.max_missing} "
            f"--maf {self.maf} "
            f"--geno {self.geno} "
            f"--recode --recode-INFO-all "
            f"--stdout | bgzip > {os.path.splitext(output_vcf)[0]}.temp.vcf.gz"
        )
        
        # 执行命令
        self.logger.info("对SNP进行软过滤")
        
        result = run_command(cmd, log_file=log_file)
        if result.returncode != 0:
            self.logger.error("SNP软过滤失败")
            return False
        
        # 检查输出文件是否存在
        temp_output = f"{os.path.splitext(output_vcf)[0]}.temp.vcf.gz"
        if not os.path.exists(temp_output):
            self.logger.error(f"vcftools过滤后的文件不存在: {temp_output}")
            return False
        
        # 创建索引
        cmd = f"tabix -p vcf {temp_output}"
        result = run_command(cmd, log_file=log_file)
        if result.returncode != 0:
            self.logger.warning("为过滤后的VCF创建索引失败，但将继续处理")
        
        # 重命名文件
        try:
            os.rename(temp_output, output_vcf)
        except OSError as e:
            self.logger.error(f"重命名文件失败: {e}")
            return False
        
        self.logger.info("SNP软过滤成功完成")
        return True 