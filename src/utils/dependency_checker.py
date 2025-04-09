import logging
import re
import subprocess
import os
import sys
from typing import Tuple, List, Dict, Optional
from .cmd_utils import CommandExecutor

class DependencyChecker:
    """依赖检查器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cmd_executor = CommandExecutor()
        
        # 需要检查的软件列表
        self.required_software = [
            "bwa",
            "samtools",
            "picard",
            "vcftools",
            "fastp",
            "qualimap",
            "java"
        ]
        
        # 检测是否在Conda环境中
        self.in_conda = self._is_in_conda()
    
    def _is_in_conda(self) -> bool:
        """检查是否在Conda环境中"""
        return 'CONDA_PREFIX' in os.environ
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有依赖"""
        issues = []
        
        for software in self.required_software:
            # 只检查软件是否安装
            software_path = self._check_software_exists(software)
            if not software_path:
                issues.append(f"未找到 {software}，请安装 {software}")
        
        return len(issues) == 0, issues
    
    def _check_software_exists(self, software: str) -> Optional[str]:
        """检查软件是否存在
        
        Args:
            software: 软件名称
            
        Returns:
            软件路径或None
        """
        try:
            # 使用which命令检查软件是否存在
            result = self.cmd_executor.run_command(f"which {software}", check=False)
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
                
            # 特殊处理picard和gatk
            if software == "picard":
                result = self.cmd_executor.run_command("which picard.jar", check=False)
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip()
            elif software == "gatk":
                result = self.cmd_executor.run_command("which gatk.jar", check=False)
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip()
                
            return None
        except Exception as e:
            self.logger.error(f"检查 {software} 存在性时出错: {str(e)}")
            return None
    
    def _check_software_version(self, software: str) -> str:
        """获取软件版本
        
        Args:
            software: 软件名称
            
        Returns:
            版本字符串，如果无法获取则返回"0.0.0"
        """
        try:
            version_cmd = self._get_version_command(software)
            if not version_cmd:
                return "0.0.0"
                
            result = self.cmd_executor.run_command(version_cmd, check=False)
            
            # 检查命令是否成功执行
            if result.returncode != 0:
                self.logger.warning(f"获取 {software} 版本命令执行失败: {result.stderr}")
                return "0.0.0"
                
            # 解析版本信息
            version_output = result.stdout if result.stdout else result.stderr
            if not version_output:
                self.logger.warning(f"获取 {software} 版本时没有输出")
                return "0.0.0"
                
            version = self._parse_version(software, version_output)
            self.logger.debug(f"{software} 版本: {version}")
            return version
        except Exception as e:
            self.logger.error(f"获取 {software} 版本时出错: {str(e)}")
            return "0.0.0"
    
    def _get_version_command(self, software: str) -> Optional[str]:
        """获取软件版本命令
        
        Args:
            software: 软件名称
            
        Returns:
            版本命令字符串
        """
        version_commands = {
            "bwa": "bwa 2>&1 | head -n 3 | grep Version",
            "samtools": "samtools --version | head -n 1",
            "picard": "java -jar $(which picard.jar) --version 2>&1",
            "gatk": "java -jar $(which gatk.jar) --version 2>&1",
            "vcftools": "vcftools --version 2>&1",
            "fastp": "fastp --version 2>&1",
            "qualimap": "qualimap --version 2>&1",
            "java": "java -version 2>&1"
        }
        return version_commands.get(software)
    
    def _parse_version(self, software: str, version_output: str) -> str:
        """从输出中解析版本号
        
        Args:
            software: 软件名称
            version_output: 版本命令的输出
            
        Returns:
            版本字符串，如果无法解析则返回"0.0.0"
        """
        try:
            version_patterns = {
                "samtools": r"samtools (\d+\.\d+(?:\.\d+)?)",
                "picard": r"(\d+\.\d+\.\d+)",
                "vcftools": r"VCFtools \((?:.*)\) (\d+\.\d+\.\d+)",
                "gatk": r"(\d+\.\d+\.\d+)",
                "bcftools": r"bcftools (\d+\.\d+(?:\.\d+)?)",
                "fastp": r"fastp (\d+\.\d+\.\d+)",
                "qualimap": r"QualiMap v(\d+\.\d+(?:\.\d+)?)",
                "multiqc": r"multiqc, version (\d+\.\d+(?:\.\d+)?)",
                "bwa": r"Version: (\d+\.\d+\.\d+)",
                "java": r"version \"(\d+\.\d+).*\""
            }
            
            pattern = version_patterns.get(software, r"(\d+\.\d+(?:\.\d+)?)")
            match = re.search(pattern, version_output)
            
            if match:
                return match.group(1)
                
            self.logger.warning(f"无法解析 {software} 版本，输出: {version_output}")
            return "0.0.0"
        except Exception as e:
            self.logger.error(f"解析 {software} 版本时出错: {str(e)}")
            return "0.0.0"
    
    def _is_version_sufficient(self, current: str, required: str) -> bool:
        """检查当前版本是否满足要求
        
        Args:
            current: 当前版本
            required: 要求的最低版本
            
        Returns:
            如果当前版本大于或等于要求的版本，则返回True
        """
        try:
            # 分割版本字符串
            current_parts = current.split('.')
            required_parts = required.split('.')
            
            # 确保两个版本列表长度相同
            while len(current_parts) < len(required_parts):
                current_parts.append('0')
            while len(required_parts) < len(current_parts):
                required_parts.append('0')
            
            # 比较版本
            for i in range(len(current_parts)):
                if int(current_parts[i]) > int(required_parts[i]):
                    return True
                elif int(current_parts[i]) < int(required_parts[i]):
                    return False
            
            # 所有部分都相等
            return True
        except Exception as e:
            self.logger.error(f"比较版本时出错: {str(e)}")
            return False 