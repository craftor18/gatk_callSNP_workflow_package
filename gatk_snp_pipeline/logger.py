import logging
from pathlib import Path
from typing import Optional

class Logger:
    """日志记录器类"""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        # 创建日志目录
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建日志记录器
        logger = logging.getLogger("gatk_snp_pipeline")
        logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误"""
        self.logger.critical(message)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message) 