"""
样本管理器模块，提供样本信息管理和批量处理功能
"""
import os
import logging
import yaml
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from .file_utils import find_files, normalize_path

@dataclass
class SampleInfo:
    """样本信息数据类"""
    name: str
    r1_path: str
    r2_path: Optional[str] = None
    is_paired: bool = True
    metadata: Optional[Dict] = None

class SampleManager:
    """样本管理器类，管理样本信息和批量处理"""
    
    def __init__(self, 
                 samples_dir: str,
                 output_dir: str,
                 logger: Optional[logging.Logger] = None):
        """
        初始化样本管理器
        
        参数:
            samples_dir: 样本数据目录
            output_dir: 输出目录
            logger: 日志记录器
        """
        self.samples_dir = normalize_path(samples_dir)
        self.output_dir = normalize_path(output_dir)
        self.logger = logger or logging.getLogger(__name__)
        self.samples: Dict[str, SampleInfo] = {}
        self._load_samples()
        
    def _load_samples(self):
        """加载样本信息"""
        # 查找所有fastq文件
        fastq_files = find_files(self.samples_dir, "*.fastq.gz")
        
        # 按样本名分组
        sample_files: Dict[str, List[str]] = {}
        for file_path in fastq_files:
            file_name = os.path.basename(file_path)
            # 假设文件名格式为: sample_name_R1.fastq.gz 或 sample_name_R2.fastq.gz
            sample_name = file_name.split("_R")[0]
            if sample_name not in sample_files:
                sample_files[sample_name] = []
            sample_files[sample_name].append(file_path)
            
        # 创建样本信息
        for sample_name, files in sample_files.items():
            # 排序确保R1在前
            files.sort()
            
            if len(files) == 1:
                # 单端测序
                self.samples[sample_name] = SampleInfo(
                    name=sample_name,
                    r1_path=files[0],
                    is_paired=False
                )
            elif len(files) == 2:
                # 双端测序
                self.samples[sample_name] = SampleInfo(
                    name=sample_name,
                    r1_path=files[0],
                    r2_path=files[1],
                    is_paired=True
                )
            else:
                self.logger.warning(f"Sample {sample_name} has unexpected number of files: {len(files)}")
                
    def get_sample(self, sample_name: str) -> Optional[SampleInfo]:
        """
        获取样本信息
        
        参数:
            sample_name: 样本名称
            
        返回:
            SampleInfo: 样本信息，如果不存在则返回None
        """
        return self.samples.get(sample_name)
        
    def get_all_samples(self) -> List[SampleInfo]:
        """
        获取所有样本信息
        
        返回:
            List[SampleInfo]: 样本信息列表
        """
        return list(self.samples.values())
        
    def get_sample_names(self) -> List[str]:
        """
        获取所有样本名称
        
        返回:
            List[str]: 样本名称列表
        """
        return list(self.samples.keys())
        
    def get_sample_output_dir(self, sample_name: str) -> str:
        """
        获取样本的输出目录
        
        参数:
            sample_name: 样本名称
            
        返回:
            str: 输出目录路径
        """
        return os.path.join(self.output_dir, sample_name)
        
    def ensure_sample_dirs(self):
        """确保所有样本的输出目录存在"""
        for sample_name in self.samples:
            sample_dir = self.get_sample_output_dir(sample_name)
            os.makedirs(sample_dir, exist_ok=True)
            
    def save_sample_info(self, output_file: str):
        """
        保存样本信息到YAML文件
        
        参数:
            output_file: 输出文件路径
        """
        info = {
            "samples": {
                name: {
                    "r1_path": sample.r1_path,
                    "r2_path": sample.r2_path,
                    "is_paired": sample.is_paired,
                    "metadata": sample.metadata
                }
                for name, sample in self.samples.items()
            }
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(info, f, default_flow_style=False)
            
    def load_sample_info(self, input_file: str):
        """
        从YAML文件加载样本信息
        
        参数:
            input_file: 输入文件路径
        """
        with open(input_file, 'r') as f:
            info = yaml.safe_load(f)
            
        self.samples.clear()
        for name, data in info["samples"].items():
            self.samples[name] = SampleInfo(
                name=name,
                r1_path=data["r1_path"],
                r2_path=data.get("r2_path"),
                is_paired=data.get("is_paired", True),
                metadata=data.get("metadata")
            ) 