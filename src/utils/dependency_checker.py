import subprocess
from typing import Tuple, List
import logging

class DependencyChecker:
    """依赖检查器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
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
                # 使用which命令检查软件是否存在
                result = subprocess.run(
                    ["which", software],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    missing.append(f"未找到 {software}，请安装 {software}")
            except Exception as e:
                self.logger.error(f"检查 {software} 时出错: {str(e)}")
                missing.append(f"检查 {software} 时出错: {str(e)}")
        
        return len(missing) == 0, missing 