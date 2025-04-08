"""
主流程控制模块，负责组织和执行各个步骤
"""
import os
import time
from .config_manager import ConfigManager
from .logger import Logger
from .steps import *

class Pipeline:
    """SNP Calling Pipeline主流程控制类"""
    
    def __init__(self, config_file, work_dir):
        """
        初始化流程控制
        
        参数:
            config_file (str): 配置文件路径
            work_dir (str): 工作目录
        """
        # 初始化日志
        log_dir = os.path.join(work_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"pipeline_{time.strftime('%Y%m%d_%H%M%S')}.log")
        self.logger = Logger(log_file)
        
        # 加载配置
        self.logger.info(f"Loading configuration from {config_file}")
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_config()
        self.config["work_dir"] = work_dir
        
        # 步骤映射
        self.steps = {
            "ref_index": RefIndex,
            "bwa_map": BwaMap,
            "sort_sam": SortSam,
            "mark_duplicates": MarkDuplicates,
            "index_bam": IndexBam,
            "haplotype_caller": HaplotypeCaller,
            "combine_gvcfs": CombineGvcfs,
            "genotype_gvcfs": GenotypeGvcfs,
            "vcf_filter": VcfFilter,
            "select_snp": SelectSnp,
            "soft_filter_snp": SoftFilterSnp,
            "get_gwas_data": GetGwasData
        }
        
        # 步骤顺序
        self.step_order = [
            "ref_index",
            "bwa_map",
            "sort_sam",
            "mark_duplicates",
            "index_bam",
            "haplotype_caller",
            "combine_gvcfs",
            "genotype_gvcfs",
            "vcf_filter",
            "select_snp",
            "soft_filter_snp",
            "get_gwas_data"
        ]
        
        self.logger.info(f"Pipeline initialized with {len(self.steps)} steps")
        
    def run_step(self, step_name):
        """
        运行指定步骤
        
        参数:
            step_name (str): 步骤名称
            
        返回:
            bool: 运行结果
        """
        if step_name not in self.steps:
            self.logger.error(f"Unknown step: {step_name}")
            raise ValueError(f"Unknown step: {step_name}")
            
        # 创建步骤实例
        step_class = self.steps[step_name]
        step = step_class(self.config, self.logger)
        
        # 执行步骤
        try:
            self.logger.info(f"Running step: {step_name}")
            result = step.run()
            if result:
                self.logger.info(f"Step {step_name} completed successfully")
            else:
                self.logger.error(f"Step {step_name} failed")
            return result
        except Exception as e:
            self.logger.error(f"Error in step {step_name}: {str(e)}")
            raise
        
    def run_all(self):
        """
        运行所有步骤
        
        返回:
            bool: 是否全部成功
        """
        self.logger.info("Starting full pipeline")
        start_time = time.time()
        
        for step_name in self.step_order:
            step_start = time.time()
            try:
                result = self.run_step(step_name)
                if not result:
                    self.logger.error(f"Pipeline stopped at step {step_name}")
                    return False
                step_end = time.time()
                self.logger.info(f"Step {step_name} completed in {step_end - step_start:.2f} seconds")
            except Exception as e:
                self.logger.error(f"Pipeline failed at step {step_name}: {str(e)}")
                return False
                
        end_time = time.time()
        self.logger.info(f"Full pipeline completed in {end_time - start_time:.2f} seconds")
        return True
            
    def run_from(self, start_step):
        """
        从指定步骤开始运行
        
        参数:
            start_step (str): 起始步骤名称
            
        返回:
            bool: 是否全部成功
        """
        if start_step not in self.steps:
            self.logger.error(f"Unknown step: {start_step}")
            raise ValueError(f"Unknown step: {start_step}")
            
        self.logger.info(f"Starting pipeline from step {start_step}")
        start_time = time.time()
        
        # 找到起始步骤的索引
        try:
            start_index = self.step_order.index(start_step)
        except ValueError:
            self.logger.error(f"Step {start_step} not found in step order")
            return False
            
        # 执行从起始步骤开始的所有步骤
        for i in range(start_index, len(self.step_order)):
            step_name = self.step_order[i]
            step_start = time.time()
            try:
                result = self.run_step(step_name)
                if not result:
                    self.logger.error(f"Pipeline stopped at step {step_name}")
                    return False
                step_end = time.time()
                self.logger.info(f"Step {step_name} completed in {step_end - step_start:.2f} seconds")
            except Exception as e:
                self.logger.error(f"Pipeline failed at step {step_name}: {str(e)}")
                return False
                
        end_time = time.time()
        self.logger.info(f"Pipeline completed in {end_time - start_time:.2f} seconds")
        return True 