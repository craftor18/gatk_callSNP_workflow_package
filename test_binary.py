#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编译后的二进制程序功能
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def run_command(cmd, description=None):
    """运行命令并处理输出"""
    if description:
        print(f"\n=== {description} ===")
    
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True,
            text=True
        )
        print(f"命令输出:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败:\n{e.stderr}")
        return False

def get_binary_path():
    """获取二进制文件路径"""
    dist_dir = Path('dist')
    system = platform.system().lower()
    
    if system == 'linux':
        binary = 'gatk-snp-pipeline-linux-x64'
    elif system == 'windows':
        binary = 'gatk-snp-pipeline-win-x64.exe'
    else:
        binary = 'gatk-snp-pipeline'
    
    binary_path = dist_dir / binary
    if not binary_path.exists():
        print(f"错误: 二进制文件 {binary_path} 不存在!")
        print("请先运行 build.py 构建二进制文件")
        sys.exit(1)
    
    return str(binary_path)

def test_generate_test_data(binary_path):
    """测试生成测试数据功能"""
    test_dir = "binary_test"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # 生成测试数据
    cmd = f"{binary_path} generate-test-data --output-dir {test_dir}/test_data --create-config {test_dir}/test_config.yaml"
    if not run_command(cmd, "测试数据生成"):
        return False
    
    # 验证文件是否生成
    config_path = Path(f"{test_dir}/test_config.yaml")
    ref_dir = Path(f"{test_dir}/test_data/reference")
    samples_dir = Path(f"{test_dir}/test_data/samples")
    
    if not config_path.exists():
        print(f"错误: 配置文件 {config_path} 未生成!")
        return False
    
    if not ref_dir.exists() or not any(ref_dir.iterdir()):
        print(f"错误: 参考基因组目录 {ref_dir} 不存在或为空!")
        return False
    
    if not samples_dir.exists() or not any(samples_dir.iterdir()):
        print(f"错误: 样本数据目录 {samples_dir} 不存在或为空!")
        return False
    
    print("测试数据生成成功!")
    return True

def test_test_mode(binary_path):
    """测试测试模式功能"""
    test_dir = "binary_test_mode"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # 创建一个空的配置文件
    with open(f"{test_dir}/test_config.yaml", "w") as f:
        f.write("# 测试配置文件\n")
    
    # 运行测试模式
    cmd = f"{binary_path} run --config {test_dir}/test_config.yaml --test-mode --skip-deps"
    if not run_command(cmd, "测试模式"):
        return False
    
    print("测试模式运行成功!")
    return True

def main():
    """主函数"""
    binary_path = get_binary_path()
    print(f"使用二进制文件: {binary_path}")
    
    # 测试帮助信息
    run_command(f"{binary_path} --help", "帮助信息")
    
    # 测试生成测试数据
    if not test_generate_test_data(binary_path):
        print("测试数据生成测试失败!")
        sys.exit(1)
    
    # 测试测试模式
    if not test_test_mode(binary_path):
        print("测试模式测试失败!")
        sys.exit(1)
    
    print("\n所有测试通过! 二进制文件包含所有期望的功能。")

if __name__ == "__main__":
    main() 