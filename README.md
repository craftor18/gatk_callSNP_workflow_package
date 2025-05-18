# GATK SNP Pipeline / GATK SNP 检测流水线

[English](#english) | [中文](#chinese)

<a name="english"></a>
# GATK SNP Pipeline

A comprehensive pipeline for SNP detection and analysis based on GATK best practices.

## Table of Contents / 目录
- [Features / 功能特点](#features)
- [System Requirements / 系统要求](#system-requirements)
- [Installation / 安装](#installation)
- [Quick Start / 快速入门](#quick-start)
- [Best Practices / 最佳实践](#best-practices)
- [Troubleshooting / 问题排查](#troubleshooting)
- [License / 许可证](#license)

## Features / 功能特点

- Reference genome indexing / 参考基因组索引创建
- Sequence alignment using BWA / 使用BWA进行序列比对
- SAM file sorting / SAM文件排序
- Duplicate marking / 标记重复序列
- BAM file indexing / BAM文件索引
- Variant calling (HaplotypeCaller) / 变异位点检测
- GVCF file merging / GVCF文件合并
- Genotyping / 基因型分型
- VCF filtering / VCF过滤
- SNP extraction and filtering / SNP提取和过滤
- GWAS data generation / 生成GWAS分析数据
- Built-in test data generation / 内置测试数据生成
- Automatic performance optimization / 自动性能优化
- Checkpoint and resume support / 断点续运行支持
- File format conversion / 文件格式转换功能
- Log level control / 日志级别控制
- Progress tracking and summary reports / 进度跟踪与摘要报告
- Automatic error handling and recovery / 自动错误处理与恢复

## System Requirements / 系统要求

### Software Requirements / 软件要求
- Linux OS (Ubuntu 18.04+, CentOS 7+) / Linux操作系统 (支持Ubuntu 18.04+, CentOS 7+)
- Python 3.6+ / Python 3.6+
- Java 1.8+ / Java 1.8+

### Required Software / 依赖软件
| Software / 软件 | Minimum Version / 最低版本 |
|----------------|------------------------|
| gatk | 4.0.0.0 |
| bwa | 0.7.17 |
| samtools | 1.10 |
| picard | 2.27.0 |
| vcftools | 0.1.16 |
| bcftools | 1.10 |
| fastp | 0.20.0 |
| qualimap | 2.2.2 |
| multiqc | 1.9 |

## Installation / 安装

### Method 1: Using Pre-compiled Binary (Recommended) / 方法1：使用预编译二进制文件（推荐）

```bash
# Download latest version / 下载最新版本
wget https://github.com/craftor18/gatk_callSNP_workflow_package/releases/download/v4/gatk-snp-pipeline-linux-x64

# Add execution permission / 添加执行权限
chmod +x gatk-snp-pipeline-linux-x64

# Move to PATH / 移动到PATH路径
sudo mv gatk-snp-pipeline-linux-x64 /usr/local/bin/gatk-snp-pipeline
```

### Method 2: Using Conda/Mamba / 方法2：使用Conda/Mamba

1. Install Mamba (recommended) or Conda / 安装Mamba（推荐）或Conda：
```bash
# Install Mamba / 安装Mamba
conda install -n base -c conda-forge mamba

# Or install Conda / 或安装Conda
# Download from https://docs.conda.io/en/latest/miniconda.html
```

2. Create and activate environment / 创建并激活环境：
```bash
# Using Mamba (recommended, faster) / 使用Mamba（推荐，更快）
mamba env create -f environment.yml
mamba activate gatk-snp-pipeline

# Or using Conda / 或使用Conda
conda env create -f environment.yml
conda activate gatk-snp-pipeline
```

3. Verify installation / 验证安装：
```bash
gatk-snp-pipeline --version
```

## Quick Start / 快速入门

### Check Dependencies / 检查依赖

```bash
gatk-snp-pipeline check-deps
```

### Create Configuration File / 创建配置文件

```bash
# Create configuration template / 创建配置文件模板
gatk-snp-pipeline init --config config.yaml
```

### Edit Configuration / 编辑配置文件

Edit the generated `config.yaml` file / 编辑生成的`config.yaml`文件：

```yaml
# Required parameters / 必需参数
reference: /path/to/your/reference.fasta
samples_dir: /path/to/your/samples
output_dir: results
sequencing_type: paired

# Recommended settings / 推荐设置
threads: 8
max_memory: 16
memory_per_thread: 2
```

### Run Pipeline / 运行流水线

```bash
# Run complete pipeline / 运行完整流程
gatk-snp-pipeline run --config config.yaml

# Run specific step / 运行特定步骤
gatk-snp-pipeline run --config config.yaml --step ref_index

# Run from specific step / 从特定步骤开始运行
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

## Best Practices / 最佳实践

### 1. First-time Usage / 初次使用流程

```bash
# 1. Check dependencies / 检查依赖
gatk-snp-pipeline check-deps

# 2. Run test mode / 运行测试模式
gatk-snp-pipeline run --test-mode

# 3. Create project config / 创建项目配置
gatk-snp-pipeline init --config my_project.yaml

# 4. Edit config file / 编辑配置文件
# 5. Run project / 运行项目
gatk-snp-pipeline run --config my_project.yaml
```

### 2. Performance Optimization / 性能优化建议

- **Thread Count / 线程数**：8-16 threads recommended / 推荐8-16线程
- **Memory Allocation / 内存分配**：Minimum 16GB for large datasets / 大型数据集至少16GB
- **Storage Space / 存储空间**：5-10x original FASTQ size / 原始FASTQ文件大小的5-10倍

### 3. Large-scale Data Processing / 大规模数据处理

```bash
# Step 1: Run to variant calling / 步骤1：运行到变异检测
gatk-snp-pipeline run --config my_project.yaml --from-step ref_index --to-step haplotype_caller

# Step 2: Complete remaining steps / 步骤2：完成剩余流程
gatk-snp-pipeline run --config my_project.yaml --from-step combine_gvcfs
```

## Troubleshooting / 问题排查

### Common Issues / 常见问题

1. **Missing Software / 软件缺失**
   - Ensure all required software is installed / 确保已安装所需软件
   - Verify software is in system PATH / 确保软件在系统PATH中
   - Use `which <software>` to verify location / 使用`which <软件名>`确认位置

2. **Version Check Failures / 版本检查失败**
   - Update software to required versions / 更新软件到所需版本
   - Use `--skip-version-check` if needed / 必要时使用`--skip-version-check`
   - Verify version manually / 手动验证版本

3. **Conda Environment Issues / Conda环境问题**
   ```bash
   # Activate environment / 激活环境
   conda activate your_env_name
   
   # Install with PEP 517 / 使用PEP 517安装
   pip install -e . --use-pep517
   ```

## License / 许可证

MIT License

## Author / 作者

Craftor18

## Acknowledgments / 致谢

Thanks to all contributors and testers. / 感谢所有贡献者和测试者。
Special thanks to GATK, BWA, Samtools development teams. / 特别感谢GATK、BWA、Samtools等工具的开发团队。

---

<a name="chinese"></a>
# GATK SNP 检测流水线

一个基于GATK最佳实践开发的SNP检测和分析流水线。

[返回顶部 / Back to Top](#gatk-snp-pipeline--gatk-snp-检测流水线)
