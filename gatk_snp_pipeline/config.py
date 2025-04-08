import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        if config_path:
            self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
    
    def create_default_config(self, config_path: Path):
        """创建默认配置文件"""
        default_config = {
            "samples_dir": "path/to/samples",
            "output_dir": "path/to/output",
            "reference_genome": "path/to/reference.fasta",
            "threads_per_job": 8,
            "max_parallel_jobs": 3,
            "max_memory": 32,
            "software_paths": {
                "gatk": "path/to/gatk",
                "bwa": "path/to/bwa",
                "samtools": "path/to/samtools",
                "picard": "path/to/picard",
                "vcftools": "path/to/vcftools",
                "bcftools": "path/to/bcftools",
                "fastp": "path/to/fastp",
                "qualimap": "path/to/qualimap",
                "multiqc": "path/to/multiqc",
                "bwa-mem2": "path/to/bwa-mem2"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value
    
    def save(self):
        """保存配置到文件"""
        if not self.config_path:
            raise ValueError("未指定配置文件路径")
        
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_log_path(self) -> Path:
        """获取日志文件路径"""
        output_dir = Path(self.get("output_dir"))
        return output_dir / "pipeline.log"
    
    def get_software_path(self, software: str) -> str:
        """获取软件路径"""
        software_paths = self.get("software_paths", {})
        return software_paths.get(software, software)  # 如果未配置，返回软件名称
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        required_keys = ["samples_dir", "output_dir", "reference_genome"]
        for key in required_keys:
            if key not in self.config:
                return False
        return True 