"""
任务调度器模块，提供并行任务管理和资源控制功能
"""
import os
import logging
import concurrent.futures
import threading
import queue
import time
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from .cmd_utils import run_command

@dataclass
class Task:
    """任务数据类"""
    name: str
    command: str
    log_file: Optional[str] = None
    threads: int = 1
    memory: int = 4  # GB
    priority: int = 0  # 优先级，数字越大优先级越高

class TaskScheduler:
    """任务调度器类，管理并行任务的执行"""
    
    def __init__(self, 
                 max_workers: int = 4,
                 max_memory: int = 32,  # GB
                 logger: Optional[logging.Logger] = None):
        """
        初始化任务调度器
        
        参数:
            max_workers: 最大并行任务数
            max_memory: 最大内存使用量(GB)
            logger: 日志记录器
        """
        self.max_workers = max_workers
        self.max_memory = max_memory
        self.logger = logger or logging.getLogger(__name__)
        
        # 任务队列
        self.task_queue = queue.PriorityQueue()
        # 当前运行的任务
        self.running_tasks: Dict[str, Task] = {}
        # 任务执行器
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        # 资源锁
        self.resource_lock = threading.Lock()
        # 当前内存使用量
        self.current_memory = 0
        
    def add_task(self, task: Task):
        """
        添加任务到队列
        
        参数:
            task: 任务对象
        """
        # 使用负优先级实现最大堆
        self.task_queue.put((-task.priority, task))
        self.logger.debug(f"Added task {task.name} to queue")
        
    def _can_run_task(self, task: Task) -> bool:
        """
        检查是否可以运行任务
        
        参数:
            task: 任务对象
            
        返回:
            bool: 是否可以运行
        """
        with self.resource_lock:
            if len(self.running_tasks) >= self.max_workers:
                return False
            if self.current_memory + task.memory > self.max_memory:
                return False
            return True
            
    def _update_resources(self, task: Task, add: bool = True):
        """
        更新资源使用情况
        
        参数:
            task: 任务对象
            add: 是否添加资源
        """
        with self.resource_lock:
            if add:
                self.current_memory += task.memory
                self.running_tasks[task.name] = task
            else:
                self.current_memory -= task.memory
                self.running_tasks.pop(task.name, None)
                
    def _run_task(self, task: Task) -> bool:
        """
        运行单个任务
        
        参数:
            task: 任务对象
            
        返回:
            bool: 任务是否成功
        """
        try:
            self.logger.info(f"Starting task {task.name}")
            self._update_resources(task, add=True)
            
            result = run_command(
                task.command,
                log_file=task.log_file,
                threads=task.threads
            )
            
            success = result.returncode == 0
            if success:
                self.logger.info(f"Task {task.name} completed successfully")
            else:
                self.logger.error(f"Task {task.name} failed with return code {result.returncode}")
                
            return success
        finally:
            self._update_resources(task, add=False)
            
    def run_tasks(self) -> Dict[str, bool]:
        """
        运行所有任务
        
        返回:
            Dict[str, bool]: 任务名称到成功状态的映射
        """
        results = {}
        futures = []
        
        while not self.task_queue.empty():
            _, task = self.task_queue.get()
            
            # 等待资源可用
            while not self._can_run_task(task):
                time.sleep(1)
                
            # 提交任务
            future = self.executor.submit(self._run_task, task)
            futures.append((task.name, future))
            
        # 等待所有任务完成
        for task_name, future in futures:
            try:
                results[task_name] = future.result()
            except Exception as e:
                self.logger.error(f"Task {task_name} raised an exception: {str(e)}")
                results[task_name] = False
                
        return results
        
    def shutdown(self):
        """关闭任务调度器"""
        self.executor.shutdown(wait=True) 