import logging
from typing import Tuple, List
from .cmd_utils import CommandExecutor

class DependencyChecker:
    """依赖检查器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cmd_executor = CommandExecutor()
        self.required_software = [
            "samtools",
            "picard",
            "vcftools",
            "gatk",
            "bcftools",
            "fastp",
            "qualimap",
            "multiqc",
            "bwa-mem2",
            "java"
        ]
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有依赖"""
        missing = []
        for software in self.required_software:
            try:
                if not self.cmd_executor.which(software):
                    missing.append(f"未找到 {software}，请安装 {software}")
            except Exception as e:
                self.logger.error(f"检查 {software} 时出错: {str(e)}")
                missing.append(f"检查 {software} 时出错: {str(e)}")
        
        return len(missing) == 0, missing 