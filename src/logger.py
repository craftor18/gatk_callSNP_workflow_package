"""
日志管理模块，提供日志记录功能
"""
import os
import logging
import datetime

class Logger:
    """日志管理类，用于统一管理日志记录"""
    
    def __init__(self, log_file=None, log_level=logging.INFO):
        """
        初始化日志管理器
        
        参数:
            log_file (str): 日志文件路径，如果为None则输出到控制台
            log_level (int): 日志级别
        """
        self.logger = logging.getLogger('snp_calling')
        self.logger.setLevel(log_level)
        self.logger.handlers = []  # 清除已有的处理器
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', 
                                           datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 如果指定了日志文件，添加文件处理器
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def info(self, message):
        """记录信息级别的日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告级别的日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误级别的日志"""
        self.logger.error(message)
    
    def debug(self, message):
        """记录调试级别的日志"""
        self.logger.debug(message)
    
    def critical(self, message):
        """记录严重错误级别的日志"""
        self.logger.critical(message) 