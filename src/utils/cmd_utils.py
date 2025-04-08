"""
命令执行工具模块，提供命令行执行功能
"""
import subprocess
import os
import threading
import logging

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