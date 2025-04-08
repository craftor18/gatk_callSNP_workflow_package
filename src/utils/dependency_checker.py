import subprocess
from typing import Tuple, List
import logging

class DependencyChecker:
    """依赖检查器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.required_software = [
            "bwa",
            "bwa-mem2",
            "samtools",
            "picard",
            "gatk",
            "vcftools",
            "fastp",
            "qualimap",
            "bcftools",
            "java"
        ]
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有依赖"""
        missing = []
        for software in self.required_software:
            try:
                # 检查软件是否存在
                if not self._check_software_exists(software):
                    missing.append(f"未找到 {software}，请安装 {software}")
            except Exception as e:
                self.logger.error(f"检查 {software} 时出错: {str(e)}")
                missing.append(f"检查 {software} 时出错: {str(e)}")
        
        return len(missing) == 0, missing
    
    def _check_software_exists(self, software: str) -> bool:
        """检查软件是否存在"""
        try:
            # 首先检查配置文件中指定的路径
            if software in self.config.get("software_paths", {}):
                path = self.config.get("software_paths")[software]
                if Path(path).exists():
                    return True
            
            # 然后检查系统PATH
            result = subprocess.run(
                ["which", software],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False 