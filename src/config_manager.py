"""
配置管理模块，用于处理配置文件
"""
import os
import yaml
import logging

class ConfigManager:
    """配置管理类，处理配置文件的读取和验证"""
    
    def __init__(self, config_file):
        """
        初始化配置管理器
        
        参数:
            config_file (str): 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """
        加载配置文件
        
        返回:
            dict: 配置字典
        """
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logging.error(f"Error loading config file: {str(e)}")
            raise
    
    def _validate_config(self):
        """
        验证配置文件中必要的设置
        
        验证包括:
        - samples_dir: 样本目录
        - output_dir: 输出目录
        - reference_genome: 参考基因组文件
        """
        required_fields = ['samples_dir', 'output_dir', 'reference_genome']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Required field '{field}' missing in config file")
            
            # 检查路径是否存在
            if field in ['samples_dir', 'reference_genome']:
                path = self.config[field]
                if not os.path.exists(path):
                    logging.warning(f"Path '{path}' specified for '{field}' does not exist")
        
        # 确保输出目录存在
        os.makedirs(self.config['output_dir'], exist_ok=True)
    
    def get_config(self):
        """
        获取配置字典
        
        返回:
            dict: 配置字典
        """
        return self.config
    
    def update_config(self, key, value):
        """
        更新配置项
        
        参数:
            key (str): 配置项键
            value: 配置项值
        """
        self.config[key] = value 