"""
文件处理工具模块，提供文件操作相关的功能
"""
import os
import re
import glob
import logging

def get_sample_list(directory, pattern="_clean_1.fastq.gz", replace_with=""):
    """
    从目录中获取样本列表
    
    参数:
        directory (str): 样本文件所在目录
        pattern (str): 样本文件的匹配模式
        replace_with (str): 替换模式的字符串，用于提取样本名
    
    返回:
        list: 样本名列表
    """
    samples = []
    try:
        for file in os.listdir(directory):
            if pattern in file:
                sample = file.replace(pattern, replace_with)
                samples.append(sample)
        return samples
    except Exception as e:
        logging.error(f"Error getting sample list from {directory}: {str(e)}")
        return []

def ensure_directory(directory):
    """
    确保目录存在，如果不存在则创建
    
    参数:
        directory (str): 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def check_file_exists(file_path):
    """
    检查文件是否存在
    
    参数:
        file_path (str): 文件路径
    
    返回:
        bool: 文件是否存在
    """
    return os.path.isfile(file_path)

def find_files(directory, pattern):
    """
    在目录中查找符合模式的文件
    
    参数:
        directory (str): 目录路径
        pattern (str): 文件名匹配模式
    
    返回:
        list: 符合条件的文件路径列表
    """
    return glob.glob(os.path.join(directory, pattern))

def normalize_path(path):
    """
    规范化路径，处理Windows和Unix的路径差异
    
    参数:
        path (str): 原始路径
    
    返回:
        str: 规范化后的路径
    """
    return os.path.normpath(path) 