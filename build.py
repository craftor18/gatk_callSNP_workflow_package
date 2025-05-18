#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行程序的脚本
支持 Linux 和 Windows 平台构建
"""

import os
import sys
import shutil
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildError(Exception):
    """构建过程中的自定义异常"""
    pass

def setup_logging() -> None:
    """设置日志配置"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / 'build.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def clean_build_dirs() -> None:
    """
    清理构建目录
    删除build、dist、__pycache__目录和.spec文件
    """
    try:
        dirs_to_clean = ['build', 'dist', '__pycache__']
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                logger.info(f"Cleaned directory: {dir_name}")
        
        # 清理.spec文件
        for spec_file in Path('.').glob('*.spec'):
            spec_file.unlink()
            logger.info(f"Removed spec file: {spec_file}")
    except Exception as e:
        logger.error(f"Error cleaning build directories: {e}")
        raise BuildError(f"Failed to clean build directories: {e}")

def get_platform_specific_params() -> Dict[str, Any]:
    """
    获取平台特定的构建参数
    
    Returns:
        Dict[str, Any]: 包含构建参数的字典
    """
    system = platform.system().lower()
    
    # 通用参数
    params = {
        'onefile': True,
        'console': True,
        'add_data': [],
        'hidden_imports': [
            'gatk_snp_pipeline.data_generator',
            'gatk_snp_pipeline.config',
            'gatk_snp_pipeline.pipeline',
            'gatk_snp_pipeline.dependency_checker',
            'gatk_snp_pipeline.logger',
            'psutil',
            'yaml',
            'argparse',
            'pathlib',
            'typing'
        ]
    }
    
    # 平台特定参数
    if system == 'linux':
        params.update({
            'name': 'gatk-snp-pipeline-linux-x64',
            'icon': None,
            'runtime_hooks': ['hooks/linux_hook.py']
        })
    elif system == 'windows':
        params.update({
            'name': 'gatk-snp-pipeline-win-x64',
            'icon': None,
            'runtime_hooks': ['hooks/windows_hook.py']
        })
    else:
        logger.warning(f"Unsupported platform: {system}, using generic settings")
        params.update({
            'name': 'gatk-snp-pipeline',
            'icon': None
        })
        
    return params

def check_dependencies() -> None:
    """
    检查构建依赖是否满足
    """
    try:
        import PyInstaller
        logger.info(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        logger.error("PyInstaller not found. Please install it first: pip install pyinstaller")
        raise BuildError("Missing PyInstaller dependency")

def build_executable(params: Dict[str, Any]) -> None:
    """
    构建可执行文件
    
    Args:
        params (Dict[str, Any]): 构建参数
    """
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
    
    # 添加运行时钩子
    if 'runtime_hooks' in params:
        for hook in params['runtime_hooks']:
            cmd.extend(['--runtime-hook', hook])
    
    # 添加主程序入口
    cmd.append('gatk_snp_pipeline/main.py')
    
    # 打印构建命令
    logger.info(f"Building executable for {platform.system()}...")
    logger.debug(f"Command: {' '.join(cmd)}")
    
    # 执行构建命令
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Build completed successfully!")
        logger.debug(f"Build output: {result.stdout}")
        
        # 设置可执行权限（仅Linux）
        if platform.system().lower() == 'linux':
            exe_path = dist_dir / params['name']
            if exe_path.exists():
                exe_path.chmod(0o755)
                logger.info(f"Set executable permissions for {exe_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Build failed with error: {e}")
        logger.error(f"Error output: {e.stderr}")
        raise BuildError(f"Build process failed: {e}")

def main() -> None:
    """主函数"""
    try:
        setup_logging()
        logger.info("Starting build process...")
        
        # 检查平台
        system = platform.system().lower()
        if system not in ['linux', 'windows']:
            logger.warning(f"Unsupported platform: {system}. Build may not work correctly.")
        
        # 检查依赖
        check_dependencies()
        
        # 清理旧的构建文件
        clean_build_dirs()
        
        # 获取构建参数
        params = get_platform_specific_params()
        
        # 执行构建
        build_executable(params)
        
        logger.info("Build process completed successfully!")
        
    except BuildError as e:
        logger.error(f"Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 