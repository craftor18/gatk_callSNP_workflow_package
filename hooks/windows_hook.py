"""
Windows平台特定的运行时钩子
处理Windows平台下的特殊配置和路径设置
"""

import os
import sys
from pathlib import Path

def setup_windows_environment():
    """设置Windows特定的环境变量和路径"""
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        base_dir = Path(sys._MEIPASS)
    else:
        # 如果是开发环境
        base_dir = Path(__file__).parent.parent

    # 设置环境变量
    os.environ['GATK_PIPELINE_HOME'] = str(base_dir)
    
    # 添加必要的DLL路径
    dll_path = base_dir / 'lib'
    if dll_path.exists():
        os.environ['PATH'] = str(dll_path) + os.pathsep + os.environ['PATH']
    
    # 设置临时目录
    temp_dir = base_dir / 'temp'
    temp_dir.mkdir(exist_ok=True)
    os.environ['TEMP'] = str(temp_dir)
    os.environ['TMP'] = str(temp_dir)

# 在模块导入时执行设置
setup_windows_environment() 