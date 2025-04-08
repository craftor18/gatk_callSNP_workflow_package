#!/usr/bin/env python3
"""
构建可执行程序的脚本
支持跨平台构建（Windows, Linux, macOS）
"""

import os
import sys
import shutil
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

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_executable():
    # 获取当前操作系统信息
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 设置输出文件名
    if system == 'windows':
        output_name = f'gatk-snp-pipeline-{system}-{machine}.exe'
    else:
        output_name = f'gatk-snp-pipeline-{system}-{machine}'
    
    # 确保dist目录存在
    dist_dir = Path('dist')
    dist_dir.mkdir(exist_ok=True)
    
    # 构建PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', output_name,
        '--add-data', 'config:config',
        '--add-data', 'README.md:.',
        'src/gatk_snp_pipeline/cli.py'
    ]
    
    # 执行PyInstaller命令
    os.system(' '.join(cmd))
    
    # 设置可执行权限（Linux和macOS）
    if system in ['linux', 'darwin']:
        exe_path = dist_dir / output_name
        os.chmod(exe_path, 0o755)
    
    print(f"构建完成: {output_name}")

def main():
    """主函数"""
    # 确保在正确的目录中
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    
    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 构建可执行程序
    build_executable()

if __name__ == "__main__":
    main() 