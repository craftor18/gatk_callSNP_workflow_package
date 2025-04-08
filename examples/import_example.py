#!/usr/bin/env python
"""
导入示例脚本，展示如何使用改进后的导入方式
"""

# 方式1：直接从包中导入所有类和模块
from src import Pipeline, Logger, ConfigManager, RefIndex, BwaMap

# 方式2：导入特定步骤
from src.steps import HaplotypeCaller, CombineGvcfs

# 方式3：导入工具函数
from src.utils import run_command, ensure_directory

# 示例使用
if __name__ == "__main__":
    # 创建一个配置管理器
    config_mgr = ConfigManager("path/to/config.yaml")
    
    # 创建一个日志记录器
    logger = Logger("path/to/log.log")
    
    # 创建一个流程实例
    pipeline = Pipeline("path/to/config.yaml", "path/to/work_dir")
    
    # 创建一个参考基因组索引步骤
    ref_index = RefIndex(config_mgr.get_config(), logger)
    
    # 使用工具函数
    ensure_directory("path/to/directory")
    
    print("导入示例完成") 