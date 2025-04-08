"""
命令执行工具模块，提供命令行执行功能
"""
import subprocess
import os
import threading
import logging
from typing import List, Optional, Union

def run_command(cmd, log_file=None, threads=1, check=False):
    """
    运行shell命令并返回结果
    
    参数:
        cmd (str): 要执行的命令
        log_file (str): 日志文件路径，如果提供则输出重定向到该文件
        threads (int): 线程数量，用于设置环境变量
        check (bool): 是否检查命令执行状态
    
    返回:
        subprocess.CompletedProcess: 命令执行结果
    """
    env = os.environ.copy()
    if threads > 1:
        env["OMP_NUM_THREADS"] = str(threads)
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        with open(log_file, 'w') as f:
            result = subprocess.run(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT, env=env, check=check)
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, check=check)
    
    return result

def run_parallel_commands(commands, max_workers=4):
    """
    并行运行多个命令
    
    参数:
        commands (list): 命令列表，每个元素是(cmd, log_file, threads)的元组
        max_workers (int): 最大并行执行数量
    
    返回:
        list: 命令执行结果列表
    """
    threads = []
    results = [None] * len(commands)
    
    def worker(idx, cmd, log_file=None, threads=1):
        try:
            results[idx] = run_command(cmd, log_file, threads)
        except Exception as e:
            logging.error(f"Error executing command: {cmd}")
            logging.error(str(e))
            results[idx] = None
    
    # 创建并启动线程
    active_threads = []
    for i, (cmd, log_file, thread_count) in enumerate(commands):
        t = threading.Thread(target=worker, args=(i, cmd, log_file, thread_count))
        threads.append(t)
        t.start()
        active_threads.append(t)
        
        # 控制最大并行数
        if len(active_threads) >= max_workers:
            active_threads[0].join()
            active_threads.pop(0)
    
    # 等待所有线程完成
    for t in threads:
        t.join()
        
    return results

class CommandExecutor:
    """命令执行工具类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.env = self._get_full_environment()
    
    def _get_full_environment(self) -> dict:
        """获取完整的执行环境"""
        env = os.environ.copy()
        
        # 获取当前shell的PATH
        try:
            shell_path = subprocess.run(
                ["bash", "-c", "echo $PATH"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # 合并PATH
            current_path = env.get("PATH", "")
            if shell_path not in current_path:
                env["PATH"] = f"{shell_path}:{current_path}"
        except Exception as e:
            self.logger.warning(f"获取shell PATH失败: {str(e)}")
        
        return env
    
    def run_command(
        self,
        cmd: Union[str, List[str]],
        check: bool = True,
        capture_output: bool = True,
        text: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """执行命令
        
        Args:
            cmd: 要执行的命令，可以是字符串或列表
            check: 是否检查返回码
            capture_output: 是否捕获输出
            text: 是否以文本形式返回输出
            **kwargs: 其他传递给subprocess.run的参数
        
        Returns:
            subprocess.CompletedProcess对象
        """
        try:
            if isinstance(cmd, str):
                cmd = ["bash", "-c", cmd]
            
            return subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=text,
                env=self.env,
                **kwargs
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"命令执行失败: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"执行命令时出错: {str(e)}")
            raise
    
    def which(self, program: str) -> Optional[str]:
        """检查程序是否存在
        
        Args:
            program: 要检查的程序名
            
        Returns:
            如果找到程序，返回其完整路径；否则返回None
        """
        try:
            result = self.run_command(f"which {program}")
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None 