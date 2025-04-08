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
    print("开始检查依赖...")
    # 确保skip_version_check参数存在
    skip_version_check = getattr(args, 'skip_version_check', False)
    if skip_version_check:
        print("已启用版本检查跳过，仅检查软件是否存在")
        
    # 创建依赖检查器
    checker = DependencyChecker(skip_version_check=skip_version_check)
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
    # 确保skip_version_check参数存在
    skip_version_check = getattr(args, 'skip_version_check', False)
    # 确保skip_deps参数存在
    skip_deps = getattr(args, 'skip_deps', False)
    
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
    if not skip_deps:
        logger.info("检查依赖...")
        if skip_version_check:
            logger.info("已启用版本检查跳过，仅检查软件是否存在")
            
        checker = DependencyChecker(skip_version_check=skip_version_check)
        checker.check_all()
        if checker.has_errors():
            logger.error("发现依赖问题，请先解决：")
            for error in checker.get_errors():
                logger.error(f"- {error}")
            print("发现依赖问题，请先解决：")
            for error in checker.get_errors():
                print(f"- {error}")
            print("\n要跳过版本检查，请使用 --skip-version-check 选项")
            print("要完全跳过依赖检查，请使用 --skip-deps 选项")
            print("更多信息请参阅 DEPENDENCY_TROUBLESHOOTING.md")
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
    """主入口函数"""
    # 创建主解析器
    parser = argparse.ArgumentParser(
        description="GATK SNP Calling Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(
        dest="command",
        help="可用命令",
        metavar="COMMAND"
    )
    
    # init 命令
    init_parser = subparsers.add_parser(
        "init",
        help="初始化配置文件",
        description="初始化一个新的配置文件"
    )
    init_parser.add_argument(
        "--config",
        required=True,
        help="配置文件路径"
    )
    init_parser.set_defaults(func=init_config)
    
    # check-deps 命令
    check_parser = subparsers.add_parser(
        "check-deps",
        help="检查依赖",
        description="检查所有必需的软件依赖是否已安装"
    )
    check_parser.add_argument(
        "--skip-version-check",
        action="store_true",
        help="跳过版本检查，只检查软件是否存在"
    )
    check_parser.set_defaults(func=check_dependencies)
    
    # run 命令
    run_parser = subparsers.add_parser(
        "run",
        help="运行流程",
        description="运行GATK SNP Calling流程"
    )
    run_parser.add_argument(
        "--config",
        required=True,
        help="配置文件路径"
    )
    run_parser.add_argument(
        "--step",
        help="运行特定步骤"
    )
    run_parser.add_argument(
        "--from-step",
        help="从特定步骤开始运行"
    )
    run_parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="跳过依赖检查"
    )
    run_parser.add_argument(
        "--skip-version-check",
        action="store_true",
        help="跳过版本检查，只检查软件是否存在"
    )
    run_parser.set_defaults(func=run_pipeline)
    
    # 如果没有提供命令，显示帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行对应的函数
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 