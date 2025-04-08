import subprocess
import os
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
        
        # 获取完整的PATH环境
        self.env = os.environ.copy()
        
        # 获取当前shell的PATH
        try:
            shell_path = subprocess.run(
                ["bash", "-c", "echo $PATH"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # 合并PATH
            current_path = self.env.get("PATH", "")
            if shell_path not in current_path:
                self.env["PATH"] = f"{shell_path}:{current_path}"
        except Exception as e:
            self.logger.warning(f"获取shell PATH失败: {str(e)}")
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有依赖"""
        missing = []
        for software in self.required_software:
            try:
                # 使用which命令检查软件是否存在
                result = subprocess.run(
                    ["bash", "-c", f"which {software}"],
                    capture_output=True,
                    text=True,
                    env=self.env
                )
                if result.returncode != 0:
                    missing.append(f"未找到 {software}，请安装 {software}")
            except Exception as e:
                self.logger.error(f"检查 {software} 时出错: {str(e)}")
                missing.append(f"检查 {software} 时出错: {str(e)}")
        
        return len(missing) == 0, missing 