import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple

class DependencyChecker:
    """检查系统依赖的工具类"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.required_tools = {
            "gatk": "4.0.0.0",
            "bwa": "0.7.17",
            "samtools": "1.10",
            "picard": "2.27.0",
            "vcftools": "0.1.16",
            "bcftools": "1.10",
            "fastp": "0.20.0",
            "qualimap": "2.2.2",
            "multiqc": "1.9",
            "bwa-mem2": "2.0",
            "java": "1.8"
        }
    
    def check_all(self):
        """检查所有依赖"""
        self.check_python_version()
        self.check_java()
        self.check_tools()
        self.check_system_resources()
    
    def check_python_version(self):
        """检查Python版本"""
        if sys.version_info < (3, 6):
            self.errors.append("需要Python 3.6或更高版本")
    
    def check_java(self):
        """检查Java环境"""
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_line = result.stderr.split("\n")[0]
            version = version_line.split('"')[1].split(".")[0]
            if int(version) < 8:
                self.errors.append("需要Java 8或更高版本")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("未找到Java，请安装Java 8或更高版本")
    
    def check_tools(self):
        """检查所有必需的工具"""
        for tool, min_version in self.required_tools.items():
            if tool == "bwa-mem2":
                self._check_bwa_mem2()
            else:
                self._check_tool_version(tool, min_version)
    
    def _check_tool_version(self, tool: str, min_version: str):
        """检查工具版本"""
        try:
            result = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = self._extract_version(result.stdout)
            if self._compare_versions(version, min_version) < 0:
                self.errors.append(
                    f"{tool} 版本 {version} 低于要求的最低版本 {min_version}"
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append(f"未找到 {tool}，请安装 {tool} {min_version} 或更高版本")
    
    def _check_bwa_mem2(self):
        """检查bwa-mem2"""
        try:
            subprocess.run(
                ["bwa-mem2", "version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append(
                "未找到bwa-mem2，请从 https://github.com/bwa-mem2/bwa-mem2 安装"
            )
    
    def check_system_resources(self):
        """检查系统资源"""
        # 检查内存
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.total < 32 * 1024 * 1024 * 1024:  # 32GB
                self.errors.append("系统内存不足，建议至少32GB内存")
        except ImportError:
            self.errors.append("无法检查系统资源，请安装psutil包")
    
    def _extract_version(self, output: str) -> str:
        """从工具输出中提取版本号"""
        # 这里需要根据不同的工具输出格式进行调整
        lines = output.split("\n")
        for line in lines:
            if "version" in line.lower():
                parts = line.split()
                for part in parts:
                    if part[0].isdigit():
                        return part
        return "0.0.0"
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """比较版本号"""
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1_part < v2_part:
                return -1
            elif v1_part > v2_part:
                return 1
        
        return 0
    
    def has_errors(self) -> bool:
        """检查是否有错误"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """获取所有错误信息"""
        return self.errors 