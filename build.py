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
    """构建可执行程序"""
    # 获取平台信息
    system, machine = get_platform_info()
    print(f"开始为 {system}-{machine} 构建可执行程序...")
    
    # 清理旧的构建文件
    clean_build_dirs()
    
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
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
        sys.exit(1)

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