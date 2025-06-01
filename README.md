# GATK SNP Pipeline / GATK SNP 检测流水线

[English](#english) | [中文](#chinese)

<a name="chinese"></a>

# GATK SNP 检测流水线

一个简单易用的SNP检测和分析工具，基于GATK最佳实践开发。

## 目录 / Table of Contents

- [简介 / Introduction](#introduction)
- [快速开始 / Quick Start](#quick-start)
- [详细使用指南 / Detailed Guide](#detailed-guide)
- [流程步骤说明 / Pipeline Steps](#pipeline-steps)
- [常见问题 / FAQ](#faq)
- [系统要求 / System Requirements](#system-requirements)
- [许可证 / License](#license)

## 简介 / Introduction

这是一个用于SNP检测和分析的自动化工具，可以帮助您：
- 自动完成从原始测序数据到SNP检测的全过程
- 生成高质量的变异检测结果
- 提供详细的运行报告和日志
- 支持断点续运行，随时可以暂停和继续

## 快速开始 / Quick Start

### 第一步：安装软件 / Step 1: Installation

1. 下载程序：
```bash
wget https://github.com/craftor18/gatk_callSNP_workflow_package/releases/download/v4/gatk-snp-pipeline-linux-x64
chmod +x gatk-snp-pipeline-linux-x64
sudo mv gatk-snp-pipeline-linux-x64 /usr/local/bin/gatk-snp-pipeline
```

2. 验证安装：
```bash
gatk-snp-pipeline --version
```

### 第二步：准备数据 / Step 2: Prepare Data

1. 准备参考基因组文件（.fasta格式）
2. 准备测序数据文件（.fastq格式）
3. 创建配置文件：
```bash
gatk-snp-pipeline init --config my_project.yaml
```

### 第三步：运行分析 / Step 3: Run Analysis

1. 检查环境：
```bash
gatk-snp-pipeline check-deps
```

2. 运行分析：
```bash
gatk-snp-pipeline run --config my_project.yaml
```

## 详细使用指南 / Detailed Guide

### 配置文件说明 / Configuration Guide

配置文件（config.yaml）包含以下重要参数：

```yaml
# 必需参数 / Required parameters
reference: /path/to/your/reference.fasta    # 参考基因组文件路径
samples_dir: /path/to/your/samples         # 测序数据存放目录
output_dir: results                        # 结果输出目录
sequencing_type: paired                    # 测序类型（paired或single）

# 性能参数 / Performance parameters
threads: 8                                 # 使用的CPU线程数
max_memory: 16                            # 最大内存使用量(GB)
memory_per_thread: 2                      # 每个线程的内存使用量(GB)
```

### 运行模式 / Running Modes

1. 完整运行：
```bash
gatk-snp-pipeline run --config config.yaml
```

2. 运行特定步骤：
```bash
gatk-snp-pipeline run --config config.yaml --step ref_index
```

3. 从特定步骤继续：
```bash
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

## 流程步骤说明 / Pipeline Steps

### 1. 参考基因组索引 (ref_index)
```bash
gatk-snp-pipeline run --config config.yaml --step ref_index
```
- 为参考基因组创建BWA索引
- 创建FASTA索引
- 创建字典文件

### 2. BWA比对 (bwa_map)
```bash
gatk-snp-pipeline run --config config.yaml --step bwa_map
```
- 使用BWA-MEM进行序列比对
- 生成SAM文件

### 3. SAM文件排序 (sort_sam)
```bash
gatk-snp-pipeline run --config config.yaml --step sort_sam
```
- 将SAM文件转换为BAM格式
- 按坐标排序

### 4. 标记重复序列 (mark_duplicates)
```bash
gatk-snp-pipeline run --config config.yaml --step mark_duplicates
```
- 使用Picard标记重复序列
- 生成去重后的BAM文件

### 5. BAM文件索引 (index_bam)
```bash
gatk-snp-pipeline run --config config.yaml --step index_bam
```
- 为BAM文件创建索引
- 生成.bai索引文件

### 6. GATK HaplotypeCaller (haplotype_caller)
```bash
gatk-snp-pipeline run --config config.yaml --step haplotype_caller
```
- 使用GATK HaplotypeCaller进行变异检测
- 生成GVCF文件

### 7. 合并GVCF文件 (combine_gvcfs)
```bash
gatk-snp-pipeline run --config config.yaml --step combine_gvcfs
```
- 合并所有样本的GVCF文件
- 生成合并后的GVCF文件

### 8. 基因型分型 (genotype_gvcfs)
```bash
gatk-snp-pipeline run --config config.yaml --step genotype_gvcfs
```
- 对合并的GVCF文件进行基因型分型
- 生成VCF文件

### 9. VCF过滤 (vcf_filter)
```bash
gatk-snp-pipeline run --config config.yaml --step vcf_filter
```
- 应用硬过滤标准
- 过滤低质量变异位点

### 10. 选择SNP (select_snp)
```bash
gatk-snp-pipeline run --config config.yaml --step select_snp
```
- 从VCF文件中提取SNP
- 过滤非SNP变异

### 11. SNP软过滤 (soft_filter_snp)
```bash
gatk-snp-pipeline run --config config.yaml --step soft_filter_snp
```
- 应用软过滤标准
- 进一步过滤SNP

### 12. 获取GWAS数据 (get_gwas_data)
```bash
gatk-snp-pipeline run --config config.yaml --step get_gwas_data
```
- 生成GWAS分析所需的数据格式
- 准备表型数据关联

## 常见问题 / FAQ

### 1. 程序无法运行怎么办？/ What if the program doesn't run?

- 检查是否已正确安装
- 运行 `gatk-snp-pipeline check-deps` 检查依赖
- 查看日志文件了解详细错误信息

### 2. 分析过程很慢怎么办？/ What if the analysis is slow?

- 增加配置文件中的线程数（threads）
- 增加内存分配（max_memory）
- 确保有足够的磁盘空间

### 3. 如何查看运行进度？/ How to check progress?

- 查看日志文件
- 检查输出目录中的进度文件
- 使用 `--verbose` 参数获取详细输出

## 系统要求 / System Requirements

### 硬件要求 / Hardware Requirements

- CPU: 8核心或更多
- 内存: 最小16GB，推荐32GB
- 硬盘: 原始数据大小的5-10倍空间

### 软件要求 / Software Requirements

- 操作系统: Linux (Ubuntu 18.04+, CentOS 7+)
- Python 3.6+
- Java 1.8+

## 许可证 / License

MIT License

## 作者 / Author

Craftor18

## 致谢 / Acknowledgments

感谢所有贡献者和测试者。/ Thanks to all contributors and testers.
特别感谢GATK、BWA、Samtools等工具的开发团队。/ Special thanks to GATK, BWA, Samtools development teams.

---

<a name="english"></a>

# GATK SNP Pipeline

A user-friendly tool for SNP detection and analysis based on GATK best practices.

[返回顶部 / Back to Top](#gatk-snp-pipeline--gatk-snp-检测流水线)
