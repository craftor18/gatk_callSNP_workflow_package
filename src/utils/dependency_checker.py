import logging
import re
import subprocess
import os
import sys
from typing import Tuple, List, Dict, Optional
from .cmd_utils import CommandExecutor

class DependencyChecker:
    """依赖检查器"""
    
    def __init__(self, config, skip_version_check=False):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cmd_executor = CommandExecutor()
        self.skip_version_check = skip_version_check
        
        # 软件及其最低版本要求
        self.required_software = {
            "samtools": "1.10",
            "picard": "2.27.0",
            "vcftools": "0.1.16",
            "gatk": "4.2.0",
            "bcftools": "1.10",
            "fastp": "0.20.0",
            "qualimap": "2.2.2",
            "multiqc": "1.9",
            "bwa": "0.7.17",
            "java": "1.8"
        }
        
        # 检测是否在Conda环境中
        self.in_conda = self._is_in_conda()
    
    def _is_in_conda(self) -> bool:
        """检查是否在Conda环境中"""
        return 'CONDA_PREFIX' in os.environ
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有依赖"""
        issues = []
        
        if self.in_conda and self.skip_version_check:
            self.logger.info("检测到Conda环境，且启用了skip_version_check，仅检查软件是否存在")
            for software in self.required_software:
                # 检查软件是否安装
                software_path = self._check_software_exists(software)
                if not software_path:
                    issues.append(f"未找到 {software}，请安装 {software} {self.required_software[software]} 或更高版本")
        else:
            for software, min_version in self.required_software.items():
                # 检查软件是否安装
                software_path = self._check_software_exists(software)
                if not software_path:
                    issues.append(f"未找到 {software}，请安装 {software} {min_version} 或更高版本")
                    continue
                    
                # 检查软件版本
                if not self.skip_version_check:
                    version = self._check_software_version(software)
                    if version == "0.0.0" or not self._is_version_sufficient(version, min_version):
                        issues.append(f"{software} 版本 {version} 低于要求的最低版本 {min_version}")
        
        return len(issues) == 0, issues
    
    def _check_software_exists(self, software: str) -> Optional[str]:
        """检查软件是否存在
        
        Args:
            software: 软件名称
            
        Returns:
            软件路径或None
        """
        try:
            # 使用CommandExecutor.which()检查软件是否存在
            path = self.cmd_executor.which(software)
            if path:
                self.logger.debug(f"找到 {software}: {path}")
                return path
                
            # 特殊处理picard和gatk
            if software == "picard" and self.cmd_executor.which("picard.jar"):
                return self.cmd_executor.which("picard.jar")
            elif software == "gatk" and self.cmd_executor.which("gatk.jar"):
                return self.cmd_executor.which("gatk.jar")
                
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
            version = self._parse_version(software, version_output)
            self.logger.debug(f"{software} 版本: {version}")
            return version
        except Exception as e:
            self.logger.error(f"获取 {software} 版本时出错: {str(e)}")
            return "0.0.0"
    
    def _get_version_command(self, software: str) -> str:
        """获取检查版本的命令
        
        Args:
            software: 软件名称
            
        Returns:
            命令字符串
        """
        version_commands = {
            "samtools": "samtools --version",
            "picard": "java -jar $(which picard.jar 2>/dev/null || echo $(which picard)) --version 2>&1",
            "vcftools": "vcftools --version",
            "gatk": "gatk --version",
            "bcftools": "bcftools --version",
            "fastp": "fastp --version 2>&1",
            "qualimap": "qualimap --version 2>&1",
            "multiqc": "multiqc --version",
            "bwa": "bwa 2>&1 | head -n 1",
            "java": "java -version 2>&1"
        }
        
        return version_commands.get(software, f"{software} --version")
    
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