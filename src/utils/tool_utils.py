"""
工具检测模块，提供软件依赖检查功能
"""
import os
import subprocess
import platform
import logging
import re
from typing import List, Dict, Optional, Tuple

class ToolChecker:
    """工具检测类，用于检查软件依赖"""
    
    # 定义工具的最低版本要求
    MIN_VERSIONS = {
        "gatk": "4.0.0.0",
        "samtools": "1.10",
        "bwa": "0.7.17",
        "picard": "2.27.0",
        "vcftools": "0.1.16",
        "bgzip": "1.10",  # 与samtools版本相同
        "tabix": "1.10",  # 与samtools版本相同
        "fastp": "0.20.0",
        "qualimap": "2.2.2",
        "multiqc": "1.9"
    }
    
    def __init__(self, logger: logging.Logger):
        """
        初始化工具检测器
        
        参数:
            logger: 日志记录器
        """
        self.logger = logger
        self.system = platform.system().lower()
        
    def check_tool(self, tool_name: str) -> Optional[str]:
        """
        检查单个工具是否可用
        
        参数:
            tool_name: 工具名称
            
        返回:
            str: 工具路径，如果不可用则返回None
        """
        try:
            if self.system == "windows":
                cmd = f"where {tool_name}"
            else:
                cmd = f"which {tool_name}"
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                self.logger.debug(f"Tool {tool_name} found at: {path}")
                return path
            else:
                self.logger.error(f"Tool {tool_name} not found in PATH")
                return None
        except Exception as e:
            self.logger.error(f"Error checking tool {tool_name}: {str(e)}")
            return None
            
    def check_tools(self, tools: List[str]) -> Dict[str, Optional[str]]:
        """
        检查多个工具是否可用
        
        参数:
            tools: 工具名称列表
            
        返回:
            Dict[str, Optional[str]]: 工具名称到路径的映射
        """
        results = {}
        for tool in tools:
            results[tool] = self.check_tool(tool)
        return results
        
    def _get_version(self, tool_name: str, tool_path: str) -> Optional[str]:
        """
        获取工具版本
        
        参数:
            tool_name: 工具名称
            tool_path: 工具路径
            
        返回:
            str: 版本号，如果无法获取则返回None
        """
        try:
            if tool_name == "gatk":
                cmd = f"{tool_path} --version"
            elif tool_name == "samtools":
                cmd = f"{tool_path} --version"
            elif tool_name == "bwa":
                cmd = f"{tool_path} 2>&1 | head -n 3"
            elif tool_name == "picard":
                cmd = f"java -jar {tool_path} --version"
            elif tool_name == "vcftools":
                cmd = f"{tool_path} --version"
            elif tool_name in ["bgzip", "tabix"]:
                cmd = f"{tool_path} --version"
            elif tool_name == "fastp":
                cmd = f"{tool_path} --version"
            elif tool_name == "qualimap":
                cmd = f"{tool_path} --version"
            elif tool_name == "multiqc":
                cmd = f"{tool_path} --version"
            else:
                cmd = f"{tool_path} --version"
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.warning(f"Could not get version for {tool_name}")
                return None
                
            version = result.stdout.strip()
            self.logger.debug(f"{tool_name} version: {version}")
            return version
        except Exception as e:
            self.logger.error(f"Error getting version for {tool_name}: {str(e)}")
            return None
            
    def _parse_version(self, version_str: str) -> Tuple[int, ...]:
        """
        解析版本号字符串为可比较的元组
        
        参数:
            version_str: 版本号字符串
            
        返回:
            Tuple[int, ...]: 版本号元组
        """
        # 提取数字部分
        numbers = re.findall(r'\d+', version_str)
        if not numbers:
            return (0,)
        return tuple(map(int, numbers))
        
    def check_version(self, tool_name: str, min_version: Optional[str] = None) -> bool:
        """
        检查工具版本是否满足要求
        
        参数:
            tool_name: 工具名称
            min_version: 最低版本要求，如果为None则使用默认值
            
        返回:
            bool: 版本是否满足要求
        """
        try:
            # 获取工具路径
            tool_path = self.check_tool(tool_name)
            if not tool_path:
                return False
                
            # 获取版本信息
            version_str = self._get_version(tool_name, tool_path)
            if not version_str:
                return False
                
            # 获取最低版本要求
            if min_version is None:
                min_version = self.MIN_VERSIONS.get(tool_name)
                if min_version is None:
                    self.logger.warning(f"No minimum version specified for {tool_name}")
                    return True
                    
            # 解析版本号
            current_version = self._parse_version(version_str)
            required_version = self._parse_version(min_version)
            
            # 比较版本
            if current_version < required_version:
                self.logger.error(
                    f"{tool_name} version {version_str} is lower than required {min_version}"
                )
                return False
                
            self.logger.info(f"{tool_name} version {version_str} meets requirement {min_version}")
            return True
        except Exception as e:
            self.logger.error(f"Error checking version for {tool_name}: {str(e)}")
            return False 