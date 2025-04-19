#!/usr/bin/env python3
"""
GATK SNP Calling Pipeline 主程序入口
"""

import sys
import os
from pathlib import Path

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def main():
    """主入口函数"""
    # 确保配置文件存在
    config_dir = Path.home() / ".gatk_snp_pipeline"
    config_dir.mkdir(exist_ok=True)
    
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 导入必要的模块
    # 确保所有模块都能在打包后导入
    try:
        from gatk_snp_pipeline.cli import main as cli_main
        from gatk_snp_pipeline.pipeline import Pipeline
        from gatk_snp_pipeline.config import ConfigManager
        from gatk_snp_pipeline.dependency_checker import DependencyChecker
        from gatk_snp_pipeline.logger import Logger
        from gatk_snp_pipeline.data_generator import TestDataGenerator
    except ImportError as e:
        print(f"导入模块失败: {e}")
        sys.exit(1)
    
    # 运行命令行接口
    cli_main()

if __name__ == "__main__":
    main() 