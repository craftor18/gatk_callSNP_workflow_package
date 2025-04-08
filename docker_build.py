#!/usr/bin/env python3
"""
Docker内部使用的构建脚本
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_platform_info():
    """获取平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 规范化架构名称
    if machine in ['x86_64', 'amd64']:
        machine = 'x64'
    elif machine in ['i386', 'i686', 'x86']:
        machine = 'x86'
    elif machine in ['arm64', 'aarch64']:
        machine = 'arm64'
    elif machine.startswith('arm'):
        machine = 'arm'
        
    return system, machine

def build_executable():
    """在Docker内部构建可执行文件"""
    # 获取平台信息
    system, machine = get_platform_info()
    print(f"在Docker内部为 {system}-{machine} 构建可执行文件...")
    
    # 构建命令
    exe_name = f"gatk-snp-pipeline-{system}-{machine}"
    if system == 'windows':
        exe_name += '.exe'
    
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--name", exe_name,
        "--add-data", "README.md:.",
        "--add-data", "DEPENDENCY_TROUBLESHOOTING.md:.",
        "gatk_snp_pipeline/main.py"
    ]
    
    # 执行构建
    try:
        subprocess.check_call(cmd)
        print(f"\n构建完成！")
        
        # 显示文件大小
        exe_path = Path("dist") / exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"文件大小: {size_mb:.1f} MB")
            return True
        else:
            print(f"错误: 未找到生成的可执行文件 {exe_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
        return False

if __name__ == "__main__":
    build_executable() 