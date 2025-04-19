import logging
import os
from pathlib import Path
from typing import Optional, Union, Dict

class Logger:
    """日志记录器类"""
    
    def __init__(self, log_path: Union[str, Path], level: str = "INFO"):
        # 确保log_path是Path对象
        self.log_path = Path(log_path) if not isinstance(log_path, Path) else log_path
        self.level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.current_level = self.level_map.get(level.upper(), logging.INFO)
        self.logger = self._setup_logger()
        self.handlers = {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        # 创建日志目录
        os.makedirs(self.log_path.parent, exist_ok=True)
        
        # 创建日志记录器
        logger = logging.getLogger("gatk_snp_pipeline")
        logger.setLevel(self.current_level)
        
        # 清除已有的处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建文件处理器
        file_handler = logging.FileHandler(str(self.log_path))
        file_handler.setLevel(self.current_level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.current_level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # 保存处理器引用
        self.handlers = {
            "file": file_handler,
            "console": console_handler
        }
        
        return logger
    
    def set_level(self, level: str) -> None:
        """设置日志级别
        
        Args:
            level: 日志级别，可以是 DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        if level.upper() in self.level_map:
            self.current_level = self.level_map[level.upper()]
            
            # 更新logger和所有处理器的级别
            self.logger.setLevel(self.current_level)
            for handler in self.handlers.values():
                handler.setLevel(self.current_level)
    
    def disable_console(self) -> None:
        """禁用控制台输出"""
        if "console" in self.handlers and self.handlers["console"] in self.logger.handlers:
            self.logger.removeHandler(self.handlers["console"])
    
    def enable_console(self) -> None:
        """启用控制台输出"""
        if "console" in self.handlers and self.handlers["console"] not in self.logger.handlers:
            self.logger.addHandler(self.handlers["console"])
    
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