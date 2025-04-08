#!/usr/bin/env python3
"""
跨平台构建脚本
使用Docker构建多平台可执行文件
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# 定义支持的平台
PLATFORMS = [
    {"system": "linux", "image": "python:3.9-slim", "machine": "x64"},
    {"system": "windows", "image": None, "machine": "x64"},  # 本地构建
    {"system": "darwin", "image": None, "machine": "x64"},  # macOS需要在macOS系统上构建
    {"system": "darwin", "image": None, "machine": "arm64"},  # macOS M1/M2需要在对应硬件上构建
]

def get_current_platform():
    """获取当前平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 规范化架构名称
    if machine in ['x86_64', 'amd64']:
        machine = 'x64'
    elif machine in ['i386', 'i686', 'x86']:
        machine = 'x86'
    elif machine in ['arm64', 'aarch64']:
        machine = 'arm64'
    elif machine.startswith('arm'):
        machine = 'arm'
        
    return system, machine

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_local(system, machine):
    """在本地构建可执行文件"""
    print(f"在本地构建 {system}-{machine} 版本...")
    
    # 构建命令
    exe_name = f"gatk-snp-pipeline-{system}-{machine}"
    if system == 'windows':
        exe_name += '.exe'
    
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--name", exe_name,
        "--add-data", "README.md:.",
        "--add-data", "DEPENDENCY_TROUBLESHOOTING.md:.",
        "gatk_snp_pipeline/main.py"
    ]
    
    # 执行构建
    try:
        subprocess.check_call(cmd)
        print(f"\n本地构建 {system}-{machine} 版本完成！")
        
        # 显示文件大小
        exe_path = Path("dist") / exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"文件大小: {size_mb:.1f} MB")
            return True
        else:
            print(f"错误: 未找到生成的可执行文件 {exe_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
        return False

def build_with_docker(system, machine, image):
    """使用Docker构建可执行文件"""
    print(f"使用Docker构建 {system}-{machine} 版本...")
    
    # 检查Docker是否可用
    try:
        subprocess.check_call(["docker", "--version"], stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: Docker未安装或无法运行，请先安装Docker")
        return False
    
    # 项目目录
    project_dir = os.path.abspath(".")
    
    # Docker工作目录
    docker_workdir = "/app"
    
    # 构建Dockerfile
    dockerfile_content = f"""FROM {image}
WORKDIR {docker_workdir}
COPY . .
RUN pip install --no-cache-dir -r requirements.txt pyinstaller
RUN python docker_build.py
"""
    
    # 创建临时目录
    temp_dir = Path("temp_docker")
    temp_dir.mkdir(exist_ok=True)
    
    # 写入Dockerfile
    with open(temp_dir / "Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # 构建Docker镜像
    try:
        tag_name = f"gatk-snp-pipeline-{system}-{machine}"
        build_cmd = ["docker", "build", "-t", tag_name, "-f", str(temp_dir / "Dockerfile"), "."]
        subprocess.check_call(build_cmd)
        
        # 运行容器并复制结果
        container_name = f"build-{system}-{machine}"
        run_cmd = ["docker", "run", "--name", container_name, tag_name, "sleep", "1"]
        subprocess.check_call(run_cmd)
        
        # 创建dist目录
        Path("dist").mkdir(exist_ok=True)
        
        # 从容器中复制可执行文件
        exe_name = f"gatk-snp-pipeline-{system}-{machine}"
        copy_cmd = ["docker", "cp", f"{container_name}:{docker_workdir}/dist/{exe_name}", "dist/"]
        subprocess.check_call(copy_cmd)
        
        # 清理
        subprocess.check_call(["docker", "rm", container_name])
        
        # 检查是否成功
        exe_path = Path("dist") / exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\nDocker构建 {system}-{machine} 版本完成！")
            print(f"文件大小: {size_mb:.1f} MB")
            return True
        else:
            print(f"错误: 未找到生成的可执行文件 {exe_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\nDocker构建失败: {e}")
        return False
    finally:
        # 清理临时文件
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def build_all():
    """构建所有平台版本"""
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 获取当前平台
    current_system, current_machine = get_current_platform()
    
    # 构建结果
    results = []
    
    # 依次构建各平台
    for platform_info in PLATFORMS:
        system = platform_info["system"]
        machine = platform_info["machine"]
        image = platform_info["image"]
        
        # 如果是当前平台，使用本地构建
        if system == current_system and machine == current_machine:
            success = build_local(system, machine)
        # 否则使用Docker构建
        elif image:
            success = build_with_docker(system, machine, image)
        else:
            print(f"跳过 {system}-{machine} 版本（不支持跨平台构建且非当前平台）")
            success = False
        
        results.append({
            "system": system,
            "machine": machine,
            "success": success
        })
    
    # 打印汇总结果
    print("\n构建结果汇总:")
    for result in results:
        status = "成功" if result["success"] else "失败"
        print(f"  {result['system']}-{result['machine']}: {status}")
    
    # 显示dist目录内容
    print("\n最终生成的可执行文件:")
    for file in Path("dist").glob("*"):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {file.name} ({size_mb:.1f} MB)")

def main():
    """主函数"""
    # 确保在正确的目录中
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    
    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 构建所有平台版本
    build_all()

if __name__ == "__main__":
    main() 