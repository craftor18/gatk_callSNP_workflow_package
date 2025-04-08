import subprocess
import sys
import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class CommandExecutor:
    """命令执行工具类"""
    
    def __init__(self):
        self.env = self._get_full_environment()
        # 检查是否为conda环境
        self.in_conda = 'CONDA_PREFIX' in os.environ
        self.conda_prefix = os.environ.get('CONDA_PREFIX', '')
        # 在Linux下保存conda的bin路径
        if self.in_conda and os.name != 'nt':
            self.conda_bin = os.path.join(self.conda_prefix, 'bin')
        else:
            self.conda_bin = ''
    
    def _get_full_environment(self) -> dict:
        """获取完整的执行环境"""
        env = os.environ.copy()
        
        # 获取当前shell的PATH
        try:
            # 在Linux/Unix系统上尝试获取shell PATH
            if os.name != 'nt':  # 不是Windows
                # 特别处理conda环境
                if 'CONDA_PREFIX' in env:
                    conda_bin = os.path.join(env['CONDA_PREFIX'], 'bin')
                    # 确保conda的bin目录在PATH的开头
                    current_path = env.get("PATH", "")
                    if conda_bin not in current_path:
                        env["PATH"] = f"{conda_bin}:{current_path}"
                    # 在Linux下，优先检查conda环境中的bin目录
                    print(f"检测到conda环境: {env['CONDA_PREFIX']}")
                    print(f"PATH环境变量: {env['PATH']}")
                else:
                    shell_path = subprocess.run(
                        ["bash", "-c", "echo $PATH"],
                        capture_output=True,
                        text=True
                    ).stdout.strip()
                    
                    # 合并PATH
                    current_path = env.get("PATH", "")
                    if shell_path and shell_path not in current_path:
                        env["PATH"] = f"{shell_path}:{current_path}"
        except Exception as e:
            print(f"获取shell PATH时出错: {str(e)}")
        
        return env
    
    def run_command(self, cmd, check=True, capture_output=True, text=True, **kwargs):
        """执行命令"""
        if isinstance(cmd, list):
            return subprocess.run(cmd, check=check, capture_output=capture_output, 
                                 text=text, env=self.env, **kwargs)
        else:
            return subprocess.run(cmd, shell=True, check=check, 
                                 capture_output=capture_output, text=text, 
                                 env=self.env, **kwargs)
    
    def which(self, command: str) -> Optional[str]:
        """查找命令的完整路径"""
        try:
            # 首先尝试使用系统which命令
            if os.name == 'nt':  # Windows
                # Windows上使用where命令
                result = self.run_command(f"where {command}", check=False)
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            else:  # Unix/Linux
                # 如果在conda环境中，直接检查conda的bin目录
                if self.in_conda:
                    conda_command_path = os.path.join(self.conda_bin, command)
                    if os.path.exists(conda_command_path) and os.access(conda_command_path, os.X_OK):
                        return conda_command_path
                
                # 使用which命令
                result = self.run_command(f"which {command}", check=False)
                if result.returncode == 0:
                    return result.stdout.strip()
                
                # 使用shutil.which作为备选方法
                path = shutil.which(command, path=self.env.get('PATH'))
                if path:
                    return path
                    
            return None
        except Exception as e:
            print(f"检查{command}路径时出错: {str(e)}")
            return None

class DependencyChecker:
    """检查系统依赖的工具类"""
    
    def __init__(self, skip_version_check=False):
        self.errors: List[str] = []
        self.cmd_executor = CommandExecutor()
        self.skip_version_check = skip_version_check
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
            "java": "1.8"
        }
        
        # 检测是否在Conda环境中
        self.in_conda = 'CONDA_PREFIX' in os.environ
        if self.in_conda:
            print(f"检测到Conda环境: {os.environ['CONDA_PREFIX']}")
    
    def check_all(self):
        """检查所有依赖"""
        self.check_python_version()
        self.check_tools()
        # 如果是Conda环境，跳过系统资源检查
        if not self.in_conda:
            self.check_system_resources()
    
    def check_python_version(self):
        """检查Python版本"""
        if sys.version_info < (3, 6):
            self.errors.append("需要Python 3.6或更高版本")
    
    def check_tools(self):
        """检查所有必需的工具"""
        if self.in_conda and self.skip_version_check:
            print("检测到Conda环境，且启用了版本检查跳过，仅检查软件是否存在")
            for tool in self.required_tools:
                if not self._check_tool_exists(tool):
                    self.errors.append(f"未找到 {tool}，请安装 {tool} {self.required_tools[tool]} 或更高版本")
        else:
            for tool, min_version in self.required_tools.items():
                self._check_tool_version(tool, min_version)
    
    def _check_tool_version(self, tool: str, min_version: str):
        """检查工具版本"""
        # 先检查工具是否存在
        tool_path = self._check_tool_exists(tool)
        if not tool_path:
            self.errors.append(f"未找到 {tool}，请安装 {tool} {min_version} 或更高版本")
            return
            
        # 检查版本（如果需要）
        if not self.skip_version_check:
            version = self._get_tool_version(tool, tool_path)
            if version == "0.0.0" or self._compare_versions(version, min_version) < 0:
                self.errors.append(f"{tool} 版本 {version} 低于要求的最低版本 {min_version}")
                # 打印详细信息以便调试
                print(f"工具 {tool} 路径: {tool_path}")
                print(f"检测到版本: {version}, 要求版本: {min_version}")
    
    def _check_tool_exists(self, tool: str) -> Optional[str]:
        """检查工具是否存在"""
        try:
            # 在Linux环境下进行额外检查
            if os.name != 'nt' and self.in_conda:
                # 特殊处理特定工具
                if tool == "picard":
                    # 在conda环境中检查picard
                    conda_bin = os.path.join(os.environ['CONDA_PREFIX'], 'bin')
                    picard_path = os.path.join(conda_bin, "picard")
                    if os.path.exists(picard_path) and os.access(picard_path, os.X_OK):
                        print(f"在conda环境中找到picard: {picard_path}")
                        return picard_path
                    
                    picard_jar_path = os.path.join(conda_bin, "picard.jar")
                    if os.path.exists(picard_jar_path) and os.access(picard_jar_path, os.R_OK):
                        print(f"在conda环境中找到picard.jar: {picard_jar_path}")
                        return picard_jar_path
                        
                elif tool == "gatk":
                    # 在conda环境中检查gatk
                    conda_bin = os.path.join(os.environ['CONDA_PREFIX'], 'bin')
                    gatk_path = os.path.join(conda_bin, "gatk")
                    if os.path.exists(gatk_path) and os.access(gatk_path, os.X_OK):
                        print(f"在conda环境中找到gatk: {gatk_path}")
                        return gatk_path
                    
                    gatk4_path = os.path.join(conda_bin, "gatk4")
                    if os.path.exists(gatk4_path) and os.access(gatk4_path, os.X_OK):
                        print(f"在conda环境中找到gatk4: {gatk4_path}")
                        return gatk4_path
                    
                    gatk_jar_path = os.path.join(conda_bin, "gatk.jar")
                    if os.path.exists(gatk_jar_path) and os.access(gatk_jar_path, os.R_OK):
                        print(f"在conda环境中找到gatk.jar: {gatk_jar_path}")
                        return gatk_jar_path
                else:
                    # 在conda环境的bin目录中检查其他工具
                    conda_bin = os.path.join(os.environ['CONDA_PREFIX'], 'bin')
                    tool_path = os.path.join(conda_bin, tool)
                    if os.path.exists(tool_path) and os.access(tool_path, os.X_OK):
                        print(f"在conda环境中找到{tool}: {tool_path}")
                        return tool_path
                    
            # 使用CommandExecutor.which()检查软件是否存在
            path = self.cmd_executor.which(tool)
            if path:
                print(f"使用which找到 {tool}: {path}")
                return path
                
            # 特殊处理picard和gatk
            if tool == "picard":
                # 尝试查找picard.jar或picard
                picard_path = self.cmd_executor.which("picard.jar")
                if picard_path:
                    print(f"找到 picard.jar: {picard_path}")
                    return picard_path
                picard_path = self.cmd_executor.which("picard")
                if picard_path:
                    print(f"找到 picard: {picard_path}")
                    return picard_path
                return None
            elif tool == "gatk":
                # 尝试查找gatk或gatk.jar或gatk4
                gatk_path = self.cmd_executor.which("gatk")
                if gatk_path:
                    print(f"找到 gatk: {gatk_path}")
                    return gatk_path
                gatk_path = self.cmd_executor.which("gatk4")
                if gatk_path:
                    print(f"找到 gatk4: {gatk_path}")
                    return gatk_path
                gatk_path = self.cmd_executor.which("gatk.jar")
                if gatk_path:
                    print(f"找到 gatk.jar: {gatk_path}")
                    return gatk_path
                return None
            
            return None
        except Exception as e:
            print(f"检查 {tool} 存在性时出错: {str(e)}")
            return None
    
    def _get_tool_version(self, tool: str, tool_path: str) -> str:
        """获取工具版本"""
        try:
            version_cmd = self._get_version_command(tool, tool_path)
            if not version_cmd:
                return "0.0.0"
                
            print(f"执行版本检查命令: {version_cmd}")
            result = self.cmd_executor.run_command(version_cmd, check=False)
            
            # 检查命令是否成功执行
            if result.returncode != 0:
                print(f"执行{tool}版本命令失败，返回码: {result.returncode}")
                print(f"错误输出: {result.stderr}")
                return "0.0.0"
                
            # 解析输出
            output = result.stdout if result.stdout else result.stderr
            version = self._parse_version(tool, output)
            print(f"解析得到{tool}版本: {version}")
            return version
        except Exception as e:
            print(f"获取 {tool} 版本时出错: {str(e)}")
            return "0.0.0"
    
    def _get_version_command(self, tool: str, tool_path: str) -> str:
        """获取检查版本的命令"""
        # 使用绝对路径以确保在conda环境中正确执行
        if os.name != 'nt' and self.in_conda:  # Linux和conda环境
            version_commands = {
                "samtools": f"{tool_path} --version",
                "picard": f"java -jar {tool_path} --version 2>&1" if tool_path.endswith('.jar') else f"{tool_path} --version 2>&1",
                "vcftools": f"{tool_path} --version",
                "gatk": f"{tool_path} --version",
                "bcftools": f"{tool_path} --version",
                "fastp": f"{tool_path} --version 2>&1",
                "qualimap": f"{tool_path} --version 2>&1",
                "multiqc": f"{tool_path} --version",
                "bwa": f"{tool_path} 2>&1",
                "java": "java -version 2>&1"
            }
        else:
            version_commands = {
                "samtools": "samtools --version",
                "picard": "java -jar $(which picard.jar 2>/dev/null || echo $(which picard)) --version 2>&1",
                "vcftools": "vcftools --version",
                "gatk": "gatk --version",
                "bcftools": "bcftools --version",
                "fastp": "fastp --version 2>&1",
                "qualimap": "qualimap --version 2>&1",
                "multiqc": "multiqc --version",
                "bwa": "bwa 2>&1",
                "java": "java -version 2>&1"
            }
        
        return version_commands.get(tool, f"{tool_path} --version")
    
    def _parse_version(self, tool: str, version_output: str) -> str:
        """从工具输出中提取版本号"""
        version_patterns = {
            "samtools": r"samtools (\d+\.\d+(?:\.\d+)?)",
            "picard": r"(\d+\.\d+\.\d+)",
            "vcftools": r"VCFtools\s+\(.+\)\s+(\d+\.\d+\.\d+)",
            "gatk": r"(\d+\.\d+\.\d+)",
            "bcftools": r"bcftools (\d+\.\d+(?:\.\d+)?)",
            "fastp": r"fastp (\d+\.\d+\.\d+)",
            "qualimap": r"QualiMap v(\d+\.\d+(?:\.\d+)?)",
            "multiqc": r"multiqc, version (\d+\.\d+(?:\.\d+)?)",
            "bwa": r"Version: (\d+\.\d+\.\d+)",
            "java": r"version \"(\d+\.\d+).*\""
        }
        
        pattern = version_patterns.get(tool, r"(\d+\.\d+(?:\.\d+)?)")
        match = re.search(pattern, version_output)
        
        if match:
            return match.group(1)
            
        # 打印原始输出以帮助调试
        print(f"{tool}版本输出: {version_output}")
        print(f"未能匹配版本，使用模式: {pattern}")
        return "0.0.0"
    
    def check_system_resources(self):
        """检查系统资源"""
        # 检查内存
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.total < 32 * 1024 * 1024 * 1024:  # 32GB
                self.errors.append("系统内存不足，建议至少32GB内存")
        except ImportError:
            pass  # 如果没有psutil，跳过系统资源检查
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """比较版本号"""
        try:
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
        except Exception as e:
            print(f"比较版本号时出错: {str(e)}")
            return -1  # 出错时假设当前版本低于要求版本
    
    def has_errors(self) -> bool:
        """检查是否有错误"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """获取所有错误信息"""
        return self.errors 