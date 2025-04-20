import argparse
import sys
import os
from pathlib import Path
# 修改导入方式，使用绝对导入替代相对导入
try:
    from .pipeline import Pipeline
    from .config import ConfigManager
    from .dependency_checker import DependencyChecker
    from .logger import Logger
    from .data_generator import TestDataGenerator
except ImportError:
    # 在打包为可执行文件后使用绝对导入
    from gatk_snp_pipeline.pipeline import Pipeline
    from gatk_snp_pipeline.config import ConfigManager
    from gatk_snp_pipeline.dependency_checker import DependencyChecker
    from gatk_snp_pipeline.logger import Logger
    from gatk_snp_pipeline.data_generator import TestDataGenerator

def init_config(args):
    """初始化配置文件"""
    config_path = Path(args.config)
    if config_path.exists():
        print(f"配置文件 {config_path} 已存在")
        return
    
    # 创建一个空配置管理器
    config_manager = ConfigManager(None)
    config_manager.generate_default_config(config_path)
    print(f"已创建默认配置文件: {config_path}")

def check_dependencies(args):
    """检查依赖"""
    print("开始检查依赖...")
    # 创建依赖检查器，默认跳过版本检查
    checker = DependencyChecker(skip_version_check=True)
    checker.check_all()
    
    if checker.has_errors():
        print("发现以下问题：")
        for error in checker.get_errors():
            print(f"- {error}")
        sys.exit(1)
    else:
        print("所有依赖检查通过！")

def generate_test_data(args):
    """生成测试数据"""
    print("开始生成测试数据...")
    
    # 创建输出目录
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建日志记录器
    logger = Logger(Path(output_dir) / "data_generation.log")
    
    # 创建测试数据生成器，传入测序类型
    generator = TestDataGenerator(output_dir, logger, args.sequencing_type)
    
    # 生成数据
    ref_path, samples_dir = generator.generate_all()
    
    # 创建配置文件
    if args.create_config:
        config_path = Path(args.create_config)
        # 创建一个空配置管理器
        config = ConfigManager(None)
        config.generate_default_config(str(config_path))
        
        # 加载生成的配置
        config = ConfigManager(str(config_path))
        
        # 更新配置
        config.set("reference", ref_path)
        config.set("samples_dir", samples_dir)
        config.set("output_dir", output_dir)
        config.set("sequencing_type", args.sequencing_type)  # 设置测序类型
        
        # 保存配置
        config.save()
        
        print(f"测试数据配置文件已创建: {config_path}")
    
    print(f"测试数据生成完成！参考基因组: {ref_path}, 样本目录: {samples_dir}, 测序类型: {args.sequencing_type}")

def run_pipeline(args):
    """运行流程"""
    # 确保skip_deps参数存在
    skip_deps = getattr(args, 'skip_deps', False)
    
    # 测试模式标志
    test_mode = getattr(args, 'test_mode', False)
    
    # 如果是测试模式，先生成测试数据
    if test_mode:
        # 获取测序类型
        sequencing_type = getattr(args, 'test_sequencing_type', 'single')
        
        print(f"运行测试模式，自动生成{sequencing_type}测序测试数据...")
        # 创建临时测试数据目录
        test_output_dir = Path("test_data")
        os.makedirs(test_output_dir, exist_ok=True)
        
        # 生成测试数据
        logger = Logger(Path(test_output_dir) / "data_generation.log")
        generator = TestDataGenerator(str(test_output_dir), logger, sequencing_type)
        ref_path, samples_dir = generator.generate_all()
        
        # 创建临时配置文件
        test_config_path = test_output_dir / "test_config.yaml"
        
        # 先生成默认配置文件
        temp_config = ConfigManager(None)
        temp_config.generate_default_config(str(test_config_path))
        
        # 然后加载并修改配置
        config = ConfigManager(str(test_config_path))
        config.set("reference", ref_path)
        config.set("samples_dir", samples_dir)
        config.set("output_dir", str(test_output_dir / "results"))
        config.set("sequencing_type", sequencing_type)  # 设置测序类型
        
        # 保存配置
        config.save()
        
        # 使用测试配置文件
        args.config = str(test_config_path)
        print(f"测试数据已生成，使用配置文件: {args.config}")
    
    # 检查配置文件是否存在
    if not args.config:
        if test_mode:
            # 测试模式下已生成配置文件，不应该出现这种情况
            print("错误: 测试模式生成配置文件失败")
            sys.exit(1)
        else:
            # 非测试模式下必须提供配置文件
            print("错误: 必须提供配置文件路径 (--config)")
            sys.exit(1)
    
    if not os.path.isfile(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        sys.exit(1)
    
    # 加载配置
    try:
        config = ConfigManager(args.config)
        
        # 设置全局选项
        if hasattr(args, 'force') and args.force:
            config.set_global_option("force", True)
            print("强制覆盖模式已启用")
        
        if hasattr(args, 'resume') and args.resume:
            config.set_global_option("resume", True)
            print("断点续运行模式已启用")
        
        if hasattr(args, 'verbose') and args.verbose:
            config.set_global_option("verbose", True)
            print("详细输出模式已启用")
        
        if hasattr(args, 'quiet') and args.quiet:
            config.set_global_option("quiet", True)
            print("静默模式已启用")
        
        # 验证配置是否有效
        errors = config.validate()
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)
    
    # 确保输出目录存在
    output_dir = config.get("output_dir", ".")
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建日志记录器
    log_path = config.get_log_path()
    logger = Logger(log_path)
    logger.info(f"使用配置文件: {args.config}")
    
    # 如果启用了静默模式，调整日志级别
    if config.get_global_option("quiet"):
        logger.set_level("ERROR")
    elif config.get_global_option("verbose"):
        logger.set_level("DEBUG")
    
    # 检查依赖（如果指定了--skip-deps则跳过）
    if not skip_deps:
        logger.info("检查依赖...")
        checker = DependencyChecker(skip_version_check=True)
        checker.check_all()
        if checker.has_errors():
            logger.error("发现依赖问题，请先解决：")
            for error in checker.get_errors():
                logger.error(f"- {error}")
            print("发现依赖问题，请先解决：")
            for error in checker.get_errors():
                print(f"- {error}")
            print("\n要跳过依赖检查，请使用 --skip-deps 选项")
            print("更多信息请参阅 DEPENDENCY_TROUBLESHOOTING.md")
            sys.exit(1)
        logger.info("依赖检查通过")
    else:
        logger.info("跳过依赖检查")
    
    # 创建并运行流程
    try:
        pipeline = Pipeline(config, logger)
        
        if hasattr(args, 'step') and args.step:
            logger.info(f"运行单个步骤: {args.step}")
            result = pipeline.run_step(args.step)
        elif hasattr(args, 'from_step') and args.from_step:
            logger.info(f"从步骤 {args.from_step} 开始运行")
            result = pipeline.run_from_step(args.from_step)
        else:
            logger.info("运行完整流程")
            result = pipeline.run_all()
        
        if result:
            logger.info("流程执行成功")
            
            # 显示统计摘要（除非静默模式）
            if not config.get_global_option("quiet"):
                output_dir = config.get("output_dir", ".")
                report_path = os.path.join(output_dir, "summary_report.txt")
                if os.path.exists(report_path):
                    print("\n=== 执行摘要 ===")
                    with open(report_path, 'r') as f:
                        print(f.read())
                
            print("流程执行成功")
        else:
            logger.error("流程执行失败")
            print("流程执行失败")
            sys.exit(1)
    except Exception as e:
        logger.error(f"流程执行出错: {str(e)}")
        print(f"流程执行出错: {str(e)}")
        
        # 详细模式下输出完整异常信息
        if config.get_global_option("verbose"):
            import traceback
            print("\n详细错误信息:")
            print(traceback.format_exc())
            
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
    check_parser.set_defaults(func=check_dependencies)
    
    # generate-test-data 命令
    test_data_parser = subparsers.add_parser(
        "generate-test-data",
        help="生成测试数据",
        description="生成用于测试的参考基因组和FASTQ样本文件"
    )
    test_data_parser.add_argument(
        "--output-dir",
        required=True,
        help="测试数据输出目录"
    )
    test_data_parser.add_argument(
        "--create-config",
        help="创建配置文件路径，该配置文件将自动设置为使用生成的测试数据"
    )
    test_data_parser.add_argument(
        "--sequencing-type",
        choices=["single", "paired"],
        default="single",
        help="测序类型: single(单端测序)或paired(双端测序)，默认为single"
    )
    test_data_parser.set_defaults(func=generate_test_data)
    
    # run 命令
    run_parser = subparsers.add_parser(
        "run",
        help="运行流程",
        description="运行GATK SNP Calling流程"
    )
    run_parser.add_argument(
        "--config",
        required=False,
        help="配置文件路径，测试模式下可省略"
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
        "--test-mode",
        action="store_true",
        help="测试模式，自动生成测试数据并运行"
    )
    run_parser.add_argument(
        "--test-sequencing-type",
        choices=["single", "paired"],
        default="single",
        help="测试模式下的测序类型: single(单端测序)或paired(双端测序)，默认为single"
    )
    
    # 全局选项
    run_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="强制覆盖所有已存在的输出文件"
    )
    run_parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="从上次中断的步骤继续运行"
    )
    run_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出信息"
    )
    run_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，只显示错误信息"
    )
    
    # 列出可用步骤命令
    list_steps_parser = subparsers.add_parser(
        "list-steps",
        help="列出所有可用的流程步骤",
        description="列出所有可用的流程步骤及其描述"
    )
    list_steps_parser.set_defaults(func=list_steps)
    
    # 转换VCF格式命令
    convert_parser = subparsers.add_parser(
        "convert",
        help="转换文件格式",
        description="转换流程结果文件到其他格式"
    )
    convert_parser.add_argument(
        "--input",
        required=True,
        help="输入文件路径"
    )
    convert_parser.add_argument(
        "--output",
        required=True,
        help="输出文件路径"
    )
    convert_parser.add_argument(
        "--format",
        choices=["csv", "tsv", "bed"],
        required=True,
        help="输出格式"
    )
    convert_parser.set_defaults(func=convert_file)
    
    run_parser.set_defaults(func=run_pipeline)
    
    # 解析参数
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # 执行对应的函数
    args.func(args)

def list_steps(args):
    """列出所有可用的流程步骤"""
    # 导入Pipeline类
    from gatk_snp_pipeline.pipeline import Pipeline
    
    # 创建临时配置
    config = ConfigManager(None)
    
    # 创建Pipeline实例
    pipeline = Pipeline(ConfigManager(None), None)
    
    # 获取步骤信息
    steps = pipeline.steps
    
    print("可用的流程步骤:")
    print("-" * 60)
    print(f"{'步骤名称':<15}{'描述':<45}")
    print("-" * 60)
    
    for step_name, step_info in steps.items():
        print(f"{step_name:<15}{step_info['name']:<45}")

def convert_file(args):
    """转换文件格式"""
    input_file = args.input
    output_file = args.output
    output_format = args.format
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在: {input_file}")
        sys.exit(1)
    
    print(f"正在将 {input_file} 转换为 {output_format} 格式...")
    
    try:
        # 根据格式选择转换方法
        if output_format == "csv":
            convert_vcf_to_csv(input_file, output_file)
        elif output_format == "tsv":
            convert_vcf_to_tsv(input_file, output_file)
        elif output_format == "bed":
            convert_vcf_to_bed(input_file, output_file)
        
        print(f"转换完成: {output_file}")
    
    except Exception as e:
        print(f"转换失败: {str(e)}")
        sys.exit(1)

def convert_vcf_to_csv(input_file, output_file):
    """将VCF文件转换为CSV格式"""
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        # 写入CSV头
        header_written = False
        
        for line in f_in:
            if line.startswith('#'):
                if line.startswith('#CHROM'):
                    # 处理VCF标题行
                    headers = line.strip().split('\t')
                    f_out.write(','.join(headers) + '\n')
                    header_written = True
            else:
                # 处理数据行
                if not header_written:
                    # 如果没有找到标题行，创建默认标题
                    default_headers = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']
                    # 通过计算制表符数量来确定样本列
                    sample_count = len(line.strip().split('\t')) - 9
                    for i in range(sample_count):
                        default_headers.append(f'SAMPLE_{i+1}')
                    f_out.write(','.join(default_headers) + '\n')
                    header_written = True
                
                # 写入数据行
                data = line.strip().split('\t')
                f_out.write(','.join(data) + '\n')

def convert_vcf_to_tsv(input_file, output_file):
    """将VCF文件转换为TSV格式"""
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            if line.startswith('#'):
                if line.startswith('#CHROM'):
                    # 去掉注释符号#
                    f_out.write(line[1:])
            else:
                f_out.write(line)

def convert_vcf_to_bed(input_file, output_file):
    """将VCF文件转换为BED格式"""
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        # BED格式: CHROM, START, END, NAME, SCORE
        for line in f_in:
            if not line.startswith('#'):
                fields = line.strip().split('\t')
                chrom = fields[0]
                pos = int(fields[1])
                # BED是0-based，VCF是1-based
                start = pos - 1
                # 计算变异长度
                ref = fields[3]
                alt = fields[4]
                # 变异名称
                name = fields[2] if fields[2] != '.' else f"{chrom}_{pos}_{ref}_{alt}"
                # 用QUAL作为分数
                score = fields[5] if fields[5] != '.' else '0'
                
                # 确定END位置
                end = start + len(ref)
                
                # 写入BED行
                f_out.write(f"{chrom}\t{start}\t{end}\t{name}\t{score}\n")

if __name__ == "__main__":
    main() 