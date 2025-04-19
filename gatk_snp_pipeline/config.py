import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

class ConfigManager:
    """配置管理器，负责加载和处理配置文件"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则创建空配置
        """
        self.config_path = config_path
        self.config = self._load_config(config_path) if config_path else {}
        self.global_options = {
            "force": False,   # 强制覆盖输出文件
            "resume": False,  # 从中断处恢复
            "verbose": False, # 显示详细信息
            "quiet": False    # 静默模式
        }
        
        # 初始化运行状态跟踪
        self.completed_steps = set()
        self.current_step = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def set_global_option(self, option: str, value: Any) -> None:
        """设置全局选项
        
        Args:
            option: 选项名称
            value: 选项值
        """
        if option in self.global_options:
            self.global_options[option] = value
    
    def get_global_option(self, option: str) -> Any:
        """获取全局选项
        
        Args:
            option: 选项名称
            
        Returns:
            选项值
        """
        return self.global_options.get(option, None)
    
    def get_log_path(self) -> str:
        """获取日志文件路径
        
        Returns:
            日志文件路径
        """
        log_dir = self.get("log_dir", "logs")
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "gatk_snp_pipeline.log")
    
    def get_software_path(self, software_name: str) -> str:
        """获取软件路径
        
        Args:
            software_name: 软件名称
            
        Returns:
            软件路径
        """
        software_config = self.get("software", {})
        return software_config.get(software_name, software_name)
    
    def save(self, path: Optional[str] = None) -> None:
        """保存配置到文件
        
        Args:
            path: 保存路径，默认为原配置文件路径
        """
        save_path = path or self.config_path
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
    
    def validate(self) -> List[str]:
        """验证配置有效性
        
        Returns:
            错误信息列表，如果为空则表示验证通过
        """
        errors = []
        
        # 检查必需字段
        required_fields = ["reference", "output_dir"]
        for field in required_fields:
            if field not in self.config:
                errors.append(f"缺少必需配置项: {field}")
        
        # 验证文件是否存在
        if "reference" in self.config and not os.path.exists(self.config["reference"]):
            errors.append(f"参考基因组文件不存在: {self.config['reference']}")
        
        if "samples_dir" in self.config and not os.path.exists(self.config["samples_dir"]):
            errors.append(f"样本目录不存在: {self.config['samples_dir']}")
        
        # 验证输出目录是否可写
        if "output_dir" in self.config:
            output_dir = self.config["output_dir"]
            if os.path.exists(output_dir):
                if not os.access(output_dir, os.W_OK):
                    errors.append(f"输出目录不可写: {output_dir}")
            else:
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    errors.append(f"无法创建输出目录: {output_dir}, 错误: {str(e)}")
        
        return errors
    
    def create_backup(self) -> str:
        """创建配置文件备份
        
        Returns:
            备份文件路径
        """
        if not self.config_path:
            return ""
            
        backup_path = f"{self.config_path}.bak"
        shutil.copy2(self.config_path, backup_path)
        return backup_path
    
    def mark_step_complete(self, step_name: str) -> None:
        """标记步骤为已完成
        
        Args:
            step_name: 步骤名称
        """
        self.completed_steps.add(step_name)
        self.save_progress()
    
    def save_progress(self) -> None:
        """保存运行进度到文件"""
        output_dir = self.get("output_dir", ".")
        progress_path = os.path.join(output_dir, ".progress")
        with open(progress_path, 'w') as f:
            for step in self.completed_steps:
                f.write(f"{step}\n")
    
    def load_progress(self) -> None:
        """从文件加载运行进度"""
        output_dir = self.get("output_dir", ".")
        progress_path = os.path.join(output_dir, ".progress")
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                self.completed_steps = set(line.strip() for line in f if line.strip())
    
    @staticmethod
    def generate_default_config(output_path: str) -> None:
        """生成默认配置文件
        
        Args:
            output_path: 输出文件路径
        """
        default_config = {
            "reference": "path/to/reference.fasta",
            "samples_dir": "path/to/samples",
            "output_dir": "results",
            "threads": 8,
            "max_memory": 16,
            "log_dir": "logs",
            "software": {
                "gatk": "gatk",
                "bwa": "bwa",
                "samtools": "samtools",
                "picard": "picard",
                "vcftools": "vcftools",
                "bcftools": "bcftools",
                "fastp": "fastp",
                "qualimap": "qualimap",
                "multiqc": "multiqc"
            },
            "gatk": {
                "convert_to_hemizygous": False
            },
            "quality_control": {
                "min_base_quality": 20,
                "min_mapping_quality": 30
            },
            "variant_filter": {
                "quality_filter": "QD < 2.0 || FS > 60.0 || MQ < 40.0",
                "filter_name": "basic_filter"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"默认配置文件已生成: {output_path}")
        print("请编辑配置文件，设置参考基因组和样本目录等必要参数。") 