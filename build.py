#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行程序的脚本
支持跨平台构建（Linux, macOS）
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    # 清理.spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()

def get_platform_info():
    """获取平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 标准化平台名称
    if system == 'darwin':
        system = 'darwin'  # macOS
    elif system == 'linux':
        system = 'linux'
    else:
        raise ValueError(f"不支持的操作系统: {system}")
    
    # 标准化架构名称
    if machine in ['x86_64', 'amd64']:
        machine = 'x64'
    elif machine in ['aarch64', 'arm64']:
        machine = 'arm64'
    else:
        raise ValueError(f"不支持的架构: {machine}")
    
    return system, machine

def build_executable():
    """构建可执行程序"""
    # 获取平台信息
    system, machine = get_platform_info()
    print(f"开始为 {system}-{machine} 构建可执行程序...")
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建命令
    exe_name = f"gatk-snp-pipeline-{system}-{machine}"
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--name", exe_name,
        "--add-data", "README.md:.",
        "--add-data", "DEPENDENCY_TROUBLESHOOTING.md:.",
        "gatk_snp_pipeline/cli.py"
    ]
    
    # 执行构建
    try:
        subprocess.check_call(cmd)
        print("\n构建完成！")
        
        # 显示构建结果
        dist_dir = Path("dist")
        if dist_dir.exists():
            print("\n可执行程序位于：")
            for file in dist_dir.glob("gatk-snp-pipeline-*"):
                print(f"  {file}")
                
            # 显示文件大小
            exe_path = dist_dir / exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n文件大小: {size_mb:.1f} MB")
                
                # 设置可执行权限
                os.chmod(exe_path, 0o755)
                print(f"已设置可执行权限: {exe_path}")
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    build_executable()

if __name__ == '__main__':
    main() 