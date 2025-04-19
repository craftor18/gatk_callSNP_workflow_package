#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行程序的脚本
只支持 Linux 平台构建
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

def get_platform_specific_params():
    """获取平台特定的构建参数"""
    system = platform.system().lower()
    
    # 通用参数
    params = {
        'onefile': True,
        'console': True,
        'add_data': [],
        'hidden_imports': [
            'gatk_snp_pipeline.data_generator',  # 确保测试数据生成模块被包含
            'gatk_snp_pipeline.config',
            'gatk_snp_pipeline.pipeline',
            'gatk_snp_pipeline.dependency_checker',
            'gatk_snp_pipeline.logger',
            'psutil'  # 性能优化依赖
        ]
    }
    
    # 平台特定参数
    if system == 'linux':
        params['name'] = 'gatk-snp-pipeline-linux-x64'
        params['icon'] = None
    elif system == 'windows':
        params['name'] = 'gatk-snp-pipeline-win-x64'
        params['icon'] = None
    else:
        print("警告：未知平台，使用通用设置")
        params['name'] = 'gatk-snp-pipeline'
        
    return params

def main():
    # 检查平台
    if platform.system().lower() != 'linux' and platform.system().lower() != 'windows':
        print("警告：此构建脚本主要为Linux平台设计，在其他平台可能无法正常工作")
    
    # 获取平台特定的参数
    params = get_platform_specific_params()
    
    # 确保dist目录存在
    dist_dir = Path('dist')
    dist_dir.mkdir(exist_ok=True)
    
    # 构建PyInstaller命令
    cmd = [
        'pyinstaller',
        '--name', params['name'],
        '--distpath', str(dist_dir),
        '--workpath', 'build',
        '--specpath', 'build',
        '--clean',
        '--noconfirm',
    ]
    
    if params['console']:
        cmd.append('--console')
    else:
        cmd.append('--windowed')
    
    if params['onefile']:
        cmd.append('--onefile')
    
    if params['icon']:
        cmd.extend(['--icon', params['icon']])
    
    # 添加隐藏导入
    for hidden_import in params['hidden_imports']:
        cmd.extend(['--hidden-import', hidden_import])
    
    # 添加数据文件
    for data in params['add_data']:
        cmd.extend(['--add-data', data])
    
    # 添加主程序入口
    cmd.append('gatk_snp_pipeline/main.py')
    
    # 打印构建命令
    print(f"Building executable for {platform.system()}...")
    print(f"Command: {' '.join(cmd)}")
    
    # 执行构建命令
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        
        # 设置可执行权限
        exe_path = dist_dir / params['name']
        if exe_path.exists():
            exe_path.chmod(0o755)
            print(f"Set executable permissions for {exe_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 