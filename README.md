# GATK SNP Pipeline / GATK SNP 检测流水线

[English](#english) | [中文](#chinese)

<a name="chinese"></a>

# GATK SNP 检测流水线

一个基于GATK最佳实践开发的SNP检测和分析流水线。

## 目录 / Table of Contents

- [功能特点 / Features](#features)
- [系统要求 / System Requirements](#system-requirements)
- [安装 / Installation](#installation)
- [快速入门 / Quick Start](#quick-start)
- [最佳实践 / Best Practices](#best-practices)
- [问题排查 / Troubleshooting](#troubleshooting)
- [许可证 / License](#license)

## 功能特点 / Features

- 参考基因组索引创建 / Reference genome indexing
- 使用BWA进行序列比对 / Sequence alignment using BWA
- SAM文件排序 / SAM file sorting
- 标记重复序列 / Duplicate marking
- BAM文件索引 / BAM file indexing
- 变异位点检测 / Variant calling (HaplotypeCaller)
- GVCF文件合并 / GVCF file merging
- 基因型分型 / Genotyping
- VCF过滤 / VCF filtering
- SNP提取和过滤 / SNP extraction and filtering
- 生成GWAS分析数据 / GWAS data generation
- 内置测试数据生成 / Built-in test data generation
- 自动性能优化 / Automatic performance optimization
- 断点续运行支持 / Checkpoint and resume support
- 文件格式转换功能 / File format conversion
- 日志级别控制 / Log level control
- 进度跟踪与摘要报告 / Progress tracking and summary reports
- 自动错误处理与恢复 / Automatic error handling and recovery

## 系统要求 / System Requirements

### 软件要求 / Software Requirements

- Linux操作系统 (支持Ubuntu 18.04+, CentOS 7+) / Linux OS (Ubuntu 18.04+, CentOS 7+)
- Python 3.6+ / Python 3.6+
- Java 1.8+ / Java 1.8+

### 依赖软件 / Required Software


| 软件 / Software | 最低版本 / Minimum Version |
| --------------- | -------------------------- |
| gatk            | 4.0.0.0                    |
| bwa             | 0.7.17                     |
| samtools        | 1.10                       |
| picard          | 2.27.0                     |
| vcftools        | 0.1.16                     |
| bcftools        | 1.10                       |
| fastp           | 0.20.0                     |
| qualimap        | 2.2.2                      |
| multiqc         | 1.9                        |

## 安装 / Installation

### step1. 创建环境 / Create Environment

1. 安装Mamba（推荐）或Conda / Install Mamba (recommended) or Conda：

```bash
# 安装Mamba / Install Mamba
conda install -n base -c conda-forge mamba

# 或安装Conda / Or install Conda
# 从 https://docs.conda.io/en/latest/miniconda.html 下载并安装 / Download from https://docs.conda.io/en/latest/miniconda.html
```

2. 创建并激活环境 / Create and activate environment：

```bash
# 使用Mamba（推荐，更快）/ Using Mamba (recommended, faster)
mamba env create -f environment.yml
mamba activate gatk-snp-pipeline

# 或使用Conda / Or using Conda
conda env create -f environment.yml
conda activate gatk-snp-pipeline
```

### step2. 安装可执行程序 / Install Executable

```bash
# 下载最新版本 / Download latest version
wget https://github.com/craftor18/gatk_callSNP_workflow_package/releases/download/v4/gatk-snp-pipeline-linux-x64

# 添加执行权限 / Add execution permission
chmod +x gatk-snp-pipeline-linux-x64

# 移动到PATH路径 / Move to PATH
sudo mv gatk-snp-pipeline-linux-x64 /usr/local/bin/gatk-snp-pipeline

# 验证安装 / Verify installation
gatk-snp-pipeline --version
```

## 快速入门 / Quick Start

### 检查依赖 / Check Dependencies

```bash
gatk-snp-pipeline check-deps
```

### 创建配置文件 / Create Configuration File

```bash
# 创建配置文件模板 / Create configuration template
gatk-snp-pipeline init --config config.yaml
```

### 编辑配置文件 / Edit Configuration

编辑生成的`config.yaml`文件 / Edit the generated `config.yaml` file：

```yaml
# 必需参数 / Required parameters
reference: /path/to/your/reference.fasta
samples_dir: /path/to/your/samples
output_dir: results
sequencing_type: paired

# 推荐设置 / Recommended settings
threads: 8
max_memory: 16
memory_per_thread: 2
```

### 运行流水线 / Run Pipeline

```bash
# 运行完整流程 / Run complete pipeline
gatk-snp-pipeline run --config config.yaml

# 运行特定步骤 / Run specific step
gatk-snp-pipeline run --config config.yaml --step ref_index

# 从特定步骤开始运行 / Run from specific step
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

## 最佳实践 / Best Practices

### 1. 初次使用流程 / First-time Usage

```bash
# 1. 检查依赖 / Check dependencies
gatk-snp-pipeline check-deps

# 2. 运行测试模式 / Run test mode
gatk-snp-pipeline run --test-mode

# 3. 创建项目配置 / Create project config
gatk-snp-pipeline init --config my_project.yaml

# 4. 编辑配置文件 / Edit config file
# 5. 运行项目 / Run project
gatk-snp-pipeline run --config my_project.yaml
```

### 2. 性能优化建议 / Performance Optimization

- **线程数 / Thread Count**：推荐8-16线程 / 8-16 threads recommended
- **内存分配 / Memory Allocation**：大型数据集至少16GB / Minimum 16GB for large datasets
- **存储空间 / Storage Space**：原始FASTQ文件大小的5-10倍 / 5-10x original FASTQ size

### 3. 大规模数据处理 / Large-scale Data Processing

```bash
# 步骤1：运行到变异检测 / Step 1: Run to variant calling
gatk-snp-pipeline run --config my_project.yaml --from-step ref_index --to-step haplotype_caller

# 步骤2：完成剩余流程 / Step 2: Complete remaining steps
gatk-snp-pipeline run --config my_project.yaml --from-step combine_gvcfs
```

## 问题排查 / Troubleshooting

### 常见问题 / Common Issues

1. **软件缺失 / Missing Software**

   - 确保已安装所需软件 / Ensure all required software is installed
   - 确保软件在系统PATH中 / Verify software is in system PATH
   - 使用`which <软件名>`确认位置 / Use `which <software>` to verify location
2. **版本检查失败 / Version Check Failures**

   - 更新软件到所需版本 / Update software to required versions
   - 必要时使用`--skip-version-check` / Use `--skip-version-check` if needed
   - 手动验证版本 / Verify version manually

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

A comprehensive pipeline for SNP detection and analysis based on GATK best practices.

[返回顶部 / Back to Top](#gatk-snp-pipeline--gatk-snp-检测流水线)
