#!/usr/bin/env python
"""
GATK SNP Calling Pipeline的主入口程序

用法:
    python run.py --config path/to/config.yaml --work_dir path/to/work/dir [--step step_name] [--from_step step_name] [--threads 40]
"""
import argparse
import os
import sys
# 直接从包导入Pipeline类
from src import Pipeline

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description="GATK SNP Calling Pipeline")
    parser.add_argument("--config", required=True, help="配置文件路径 (config.yaml)")
    parser.add_argument("--work_dir", required=True, help="工作目录路径")
    parser.add_argument("--step", help="仅运行指定步骤", choices=[
        "ref_index", "bwa_map", "sort_sam", "mark_duplicates", "index_bam", 
        "haplotype_caller", "combine_gvcfs", "genotype_gvcfs", "vcf_filter", 
        "select_snp", "soft_filter_snp", "get_gwas_data"
    ])
    parser.add_argument("--from_step", help="从指定步骤开始运行", choices=[
        "ref_index", "bwa_map", "sort_sam", "mark_duplicates", "index_bam", 
        "haplotype_caller", "combine_gvcfs", "genotype_gvcfs", "vcf_filter", 
        "select_snp", "soft_filter_snp", "get_gwas_data"
    ])
    parser.add_argument("--threads", type=int, default=40, help="CPU线程数")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    
    args = parser.parse_args()
    
    # 如果请求显示版本信息
    if args.version:
        import src
        print(f"GATK SNP Calling Pipeline 版本: {src.__version__}")
        sys.exit(0)
    
    # 检查配置文件是否存在
    if not os.path.isfile(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        sys.exit(1)
        
    # 创建工作目录
    os.makedirs(args.work_dir, exist_ok=True)
    
    try:
        # 创建管道实例
        pipeline = Pipeline(args.config, args.work_dir)
        
        # 运行管道
        if args.step:
            result = pipeline.run_step(args.step)
        elif args.from_step:
            result = pipeline.run_from(args.from_step)
        else:
            result = pipeline.run_all()
            
        # 检查结果
        if result:
            print("管道执行成功完成")
            sys.exit(0)
        else:
            print("管道执行失败")
            sys.exit(1)
    except Exception as e:
        print(f"管道执行时发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 