"""
基础步骤类，所有SNP calling流程步骤的基类
"""
import os
import logging
from abc import ABC, abstractmethod
from ..utils.cmd_utils import run_command
from ..utils.tool_utils import ToolChecker
from ..utils.task_scheduler import TaskScheduler, Task
from ..utils.sample_manager import SampleManager, SampleInfo
from typing import Optional

class BaseStep(ABC):
    """
    基础步骤抽象类，定义了所有步骤的通用接口
    """
    
    def __init__(self, config, logger):
        """
        初始化步骤
        
        参数:
            config (dict): 配置字典
            logger (Logger): 日志记录器
        """
        self.config = config
        self.logger = logger
        self.name = self.__class__.__name__
        self.work_dir = config.get("work_dir", ".")
        
        # 初始化工具检查器
        self.tool_checker = ToolChecker(logger)
        
        # 初始化任务调度器
        self.task_scheduler = TaskScheduler(
            max_workers=config.get("max_parallel_jobs", 4),
            max_memory=config.get("max_memory", 32),
            logger=logger
        )
        
        # 初始化样本管理器
        self.sample_manager = SampleManager(
            samples_dir=config.get("samples_dir"),
            output_dir=config.get("output_dir"),
            logger=logger
        )
        
    @abstractmethod
    def get_input_files(self):
        """
        获取输入文件列表
        
        返回:
            list: 输入文件路径列表
        """
        pass
        
    @abstractmethod
    def get_output_files(self):
        """
        获取输出文件列表
        
        返回:
            list: 输出文件路径列表
        """
        pass
        
    def check_dependencies(self):
        """
        检查步骤依赖的软件是否可用
        
        返回:
            bool: 依赖是否可用
        """
        required_tools = self.get_required_tools()
        if not required_tools:
            return True
            
        self.logger.info(f"Checking dependencies for {self.name}")
        tool_paths = self.tool_checker.check_tools(required_tools)
        
        missing_tools = [tool for tool, path in tool_paths.items() if path is None]
        if missing_tools:
            self.logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            raise RuntimeError(f"Missing required tools: {', '.join(missing_tools)}")
            
        # 检查工具版本
        for tool in required_tools:
            if not self.tool_checker.check_version(tool):
                self.logger.warning(f"Could not verify version for {tool}")
                
        return True
    
    def get_required_tools(self):
        """
        获取步骤依赖的工具列表
        
        返回:
            list: 工具名称列表
        """
        return []
        
    def validate_input(self):
        """
        验证输入文件是否存在
        
        返回:
            bool: 验证是否通过
        """
        for file_path in self.get_input_files():
            if not os.path.exists(file_path):
                self.logger.error(f"Input file not found: {file_path}")
                raise FileNotFoundError(f"Input file not found: {file_path}")
        return True
    
    def ensure_output_dirs(self):
        """
        确保输出目录存在
        """
        output_files = self.get_output_files()
        for output_file in output_files:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.logger.debug(f"Created output directory: {output_dir}")
                
    def add_task(self, 
                 name: str,
                 command: str,
                 log_file: Optional[str] = None,
                 threads: int = 1,
                 memory: int = 4,
                 priority: int = 0):
        """
        添加任务到调度器
        
        参数:
            name: 任务名称
            command: 要执行的命令
            log_file: 日志文件路径
            threads: 使用的线程数
            memory: 使用的内存(GB)
            priority: 任务优先级
        """
        task = Task(
            name=name,
            command=command,
            log_file=log_file,
            threads=threads,
            memory=memory,
            priority=priority
        )
        self.task_scheduler.add_task(task)
        
    def run_tasks(self) -> bool:
        """
        运行所有任务
        
        返回:
            bool: 所有任务是否成功
        """
        results = self.task_scheduler.run_tasks()
        return all(results.values())
        
    @abstractmethod
    def execute(self):
        """
        执行步骤的主逻辑
        
        返回:
            bool: 执行是否成功
        """
        pass
        
    def run(self):
        """
        运行步骤，包括验证和执行
        
        返回:
            bool: 运行是否成功
        """
        self.logger.info(f"Starting {self.name}")
        
        try:
            # 检查依赖
            self.check_dependencies()
            
            # 验证输入
            self.validate_input()
            
            # 确保输出目录存在
            self.ensure_output_dirs()
            
            # 执行步骤
            result = self.execute()
            
            self.logger.info(f"Completed {self.name}")
            return result
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {str(e)}")
            raise
        finally:
            # 关闭任务调度器
            self.task_scheduler.shutdown() 