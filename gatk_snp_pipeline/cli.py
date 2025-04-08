import argparse
import sys
import os
from pathlib import Path
from .pipeline import Pipeline
from .config import ConfigManager
from .dependency_checker import DependencyChecker
from .logger import Logger

def init_config(args):
    """初始化配置文件"""
    config_path = Path(args.config)
    if config_path.exists():
        print(f"配置文件 {config_path} 已存在")
        return
    
    config_manager = ConfigManager()
    config_manager.create_default_config(config_path)
    print(f"已创建默认配置文件: {config_path}")

def check_dependencies(args):
    """检查依赖"""
    checker = DependencyChecker(skip_version_check=args.skip_version_check)
    checker.check_all()
    
    if checker.has_errors():
        print("发现以下问题：")
        for error in checker.get_errors():
            print(f"- {error}")
        sys.exit(1)
    else:
        print("所有依赖检查通过！")

def run_pipeline(args):
    """运行流程"""
    # 检查配置文件是否存在
    if not os.path.isfile(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        sys.exit(1)
    
    # 加载配置
    try:
        config = ConfigManager(args.config)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)
    
    # 创建日志记录器
    logger = Logger(config.get_log_path())
    logger.info(f"使用配置文件: {args.config}")
    
    # 检查依赖（如果指定了--skip-deps则跳过）
    if not args.skip_deps:
        logger.info("检查依赖...")
        checker = DependencyChecker(skip_version_check=args.skip_version_check)
        checker.check_all()
        if checker.has_errors():
            logger.error("发现依赖问题，请先解决：")
            for error in checker.get_errors():
                logger.error(f"- {error}")
            print("发现依赖问题，请先解决：")
            for error in checker.get_errors():
                print(f"- {error}")
            sys.exit(1)
        logger.info("依赖检查通过")
    else:
        logger.info("跳过依赖检查")
    
    # 创建并运行流程
    try:
        pipeline = Pipeline(config, logger)
        
        if args.step:
            logger.info(f"运行单个步骤: {args.step}")
            result = pipeline.run_step(args.step)
        elif args.from_step:
            logger.info(f"从步骤 {args.from_step} 开始运行")
            result = pipeline.run_from_step(args.from_step)
        else:
            logger.info("运行完整流程")
            result = pipeline.run_all()
        
        if result:
            logger.info("流程执行成功")
            print("流程执行成功")
        else:
            logger.error("流程执行失败")
            print("流程执行失败")
            sys.exit(1)
    except Exception as e:
        logger.error(f"流程执行出错: {str(e)}")
        print(f"流程执行出错: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="GATK SNP Calling Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化配置文件")
    init_parser.add_argument("--config", required=True, help="配置文件路径")
    init_parser.set_defaults(func=init_config)
    
    # check-deps 命令
    check_parser = subparsers.add_parser("check-deps", help="检查依赖")
    check_parser.add_argument("--skip-version-check", action="store_true", help="跳过版本检查，只检查软件是否存在")
    check_parser.set_defaults(func=check_dependencies)
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="运行流程")
    run_parser.add_argument("--config", required=True, help="配置文件路径")
    run_parser.add_argument("--step", help="运行特定步骤")
    run_parser.add_argument("--from-step", help="从特定步骤开始运行")
    run_parser.add_argument("--skip-deps", action="store_true", help="跳过依赖检查")
    run_parser.add_argument("--skip-version-check", action="store_true", help="跳过版本检查，只检查软件是否存在")
    run_parser.set_defaults(func=run_pipeline)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == "__main__":
    main() 