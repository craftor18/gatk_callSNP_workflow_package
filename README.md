# GATK SNP Pipeline / GATK SNP 检测流水线

[English](#english) | [中文](#chinese)

<a name="english"></a>
# GATK SNP Pipeline

A comprehensive pipeline for SNP detection and analysis based on GATK best practices.

## Features

- Reference genome indexing
- Sequence alignment using BWA
- SAM file sorting
- Duplicate marking
- BAM file indexing
- Variant calling (HaplotypeCaller)
- GVCF file merging
- Genotyping
- VCF filtering
- SNP extraction and filtering
- GWAS data generation
- Built-in test data generation
- Automatic performance optimization
- **Checkpoint and resume support**
- **File format conversion**
- **Log level control**
- **Progress tracking and summary reports**
- **Automatic error handling and recovery**

## System Requirements

- Linux OS (Ubuntu 18.04+, CentOS 7+)
- Python 3.6+
- Required software:
  - GATK 4.0+
  - BWA 0.7.17+
  - Samtools 1.9+
  - Picard 2.21.0+
  - VCFtools 0.1.16+
  - BCFtools 1.9+
  - fastp 0.20.0+ (optional)
  - QualiMap 2.2.2+ (optional)
  - Java 1.8+

## Installation

### Method 1: Using Pre-compiled Binary

```bash
# Download latest version
wget https://github.com/craftor18/gatk_callSNP_workflow_package/releases/download/v4/gatk-snp-pipeline-linux-x64

# Add execution permission
chmod +x gatk-snp-pipeline-linux-x64

# Move to PATH
sudo mv gatk-snp-pipeline-linux-x64 /usr/local/bin/gatk-snp-pipeline
```

### Method 2: Install from Source

```bash
# Clone repository
git clone https://github.com/craftor18/gatk_callSNP_workflow_package.git
cd gatk_callSNP_workflow_package

# Install dependencies
pip install -r requirements.txt

# Install package
pip install .
```

## Quick Start

### Check Dependencies

Check if all required software is installed and available:

```bash
gatk-snp-pipeline check-deps
```

### Create Configuration File

```bash
# Create configuration template
gatk-snp-pipeline init --config config.yaml
```

### Edit Configuration

Edit the generated `config.yaml` file:

```yaml
# Required parameters
reference: /path/to/your/reference.fasta
samples_dir: /path/to/your/samples
output_dir: results
sequencing_type: paired

# Recommended settings
threads: 8
max_memory: 16
memory_per_thread: 2
```

### Run Pipeline

```bash
# Run complete pipeline
gatk-snp-pipeline run --config config.yaml

# Run specific step
gatk-snp-pipeline run --config config.yaml --step ref_index

# Run from specific step
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

## Dependency Troubleshooting

### Common Issues

1. **Missing Software**
   - Ensure all required software is installed
   - Verify software is in system PATH
   - If using conda, ensure correct environment is activated
   - Use `which <software>` to verify software location

2. **Version Check Failures**
   - Update software to required versions
   - Use `--skip-version-check` if version detection is incorrect
   - Verify version manually with `<software> --version`

3. **Conda Environment Issues**
   ```bash
   # Activate environment
   conda activate your_env_name
   
   # Install with PEP 517
   pip install -e . --use-pep517
   ```

4. **Custom Installation Paths**
   - Add installation path to system PATH
   - Create symbolic links to system PATH directories
   - Use `--skip-deps` only if all dependencies are correctly installed

### Supported Software Versions

| Software | Minimum Version |
|----------|----------------|
| gatk | 4.0.0.0 |
| bwa | 0.7.17 |
| samtools | 1.10 |
| picard | 2.27.0 |
| vcftools | 0.1.16 |
| bcftools | 1.10 |
| fastp | 0.20.0 |
| qualimap | 2.2.2 |
| multiqc | 1.9 |
| java | 1.8 |

### Installing Dependencies

#### Using Conda (Recommended)

```bash
# Create conda environment
conda create -n gatk-pipeline python=3.9

# Activate environment
conda activate gatk-pipeline

# Install dependencies
conda install -c bioconda gatk4 bwa samtools picard vcftools bcftools fastp qualimap multiqc

# Install package
pip install -e . --use-pep517
```

#### Linux System Installation

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install bwa samtools vcftools bcftools

# CentOS/RHEL
sudo yum install bwa samtools vcftools bcftools
```

## License

MIT License

---

<a name="chinese"></a>
# GATK SNP 检测流水线

一个基于GATK最佳实践开发的SNP检测和分析流水线。

## 功能特点

- 参考基因组索引创建
- 使用BWA进行序列比对
- SAM文件排序
- 标记重复序列
- BAM文件索引
- 变异位点检测 (HaplotypeCaller)
- GVCF文件合并
- 基因型分型
- VCF过滤
- SNP提取和过滤
- 生成GWAS分析数据
- 内置测试数据生成
- 自动性能优化
- **断点续运行支持**
- **文件格式转换功能**
- **日志级别控制**
- **进度跟踪与摘要报告**
- **自动错误处理与恢复**

## 系统要求

- Linux操作系统 (支持Ubuntu 18.04+, CentOS 7+)
- Python 3.6+
- 依赖软件：
  - GATK 4.0+
  - BWA 0.7.17+
  - Samtools 1.9+
  - Picard 2.21.0+
  - VCFtools 0.1.16+
  - BCFtools 1.9+
  - fastp 0.20.0+ (可选)
  - QualiMap 2.2.2+ (可选)
  - Java 1.8+

## 安装

### 方法1：使用预编译二进制文件

```bash
# 下载最新版本
wget https://github.com/craftor18/gatk_callSNP_workflow_package/releases/download/v4/gatk-snp-pipeline-linux-x64

# 添加执行权限
chmod +x gatk-snp-pipeline-linux-x64

# 移动到PATH路径
sudo mv gatk-snp-pipeline-linux-x64 /usr/local/bin/gatk-snp-pipeline
```

### 方法2：从源码安装

```bash
# 克隆仓库
git clone https://github.com/craftor18/gatk_callSNP_workflow_package.git
cd gatk_callSNP_workflow_package

# 安装依赖
pip install -r requirements.txt

# 安装程序
pip install .
```

## 快速入门

### 检查依赖

检查所有必需软件是否已安装并可用：

```bash
gatk-snp-pipeline check-deps
```

### 创建配置文件

```bash
# 创建配置文件模板
gatk-snp-pipeline init --config config.yaml
```

### 编辑配置文件

编辑生成的`config.yaml`文件：

```yaml
# 必需参数
reference: /path/to/your/reference.fasta
samples_dir: /path/to/your/samples
output_dir: results
sequencing_type: paired

# 推荐设置
threads: 8
max_memory: 16
memory_per_thread: 2
```

### 运行流水线

```bash
# 运行完整流程
gatk-snp-pipeline run --config config.yaml

# 运行特定步骤
gatk-snp-pipeline run --config config.yaml --step ref_index

# 从特定步骤开始运行
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

## 依赖问题排查

### 常见问题

1. **无法找到必要软件**
   - 确保已安装所需软件
   - 确保软件在系统PATH中
   - 如果使用conda环境，请确保已激活正确的环境
   - 使用`which <软件名>`确认软件位置

2. **版本检查失败**
   - 更新软件到所需版本
   - 如果版本检测不正确，使用`--skip-version-check`
   - 使用`<软件名> --version`手动验证版本

3. **Conda环境问题**
   ```bash
   # 激活环境
   conda activate your_env_name
   
   # 使用PEP 517安装
   pip install -e . --use-pep517
   ```

4. **自定义安装路径**
   - 将安装路径添加到系统PATH
   - 创建到系统PATH目录的符号链接
   - 仅在确定所有依赖都正确安装时使用`--skip-deps`

### 支持的软件版本

| 软件 | 最低版本 |
|------|---------|
| gatk | 4.0.0.0 |
| bwa | 0.7.17 |
| samtools | 1.10 |
| picard | 2.27.0 |
| vcftools | 0.1.16 |
| bcftools | 1.10 |
| fastp | 0.20.0 |
| qualimap | 2.2.2 |
| multiqc | 1.9 |
| java | 1.8 |

### 安装依赖

#### 使用Conda安装（推荐）

```bash
# 创建conda环境
conda create -n gatk-pipeline python=3.9

# 激活环境
conda activate gatk-pipeline

# 安装依赖
conda install -c bioconda gatk4 bwa samtools picard vcftools bcftools fastp qualimap multiqc

# 安装软件包
pip install -e . --use-pep517
```

#### Linux系统安装

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install bwa samtools vcftools bcftools

# CentOS/RHEL
sudo yum install bwa samtools vcftools bcftools
```

## 许可证

MIT License

## 作者

Craftor18

## 致谢

感谢所有为本项目做出贡献的开发者和测试者。
感谢GATK、BWA、Samtools等工具的开发团队。

## 在Conda环境中运行

本软件可以在Conda环境中很好地运行，这提供了一种隔离且可重现的方式来管理依赖关系。

### 使用Conda环境配置依赖

建议使用Conda创建一个专用环境来安装所有必需的依赖：

```bash
# 创建一个名为gatkPipeline的新环境
conda create -n gatkPipeline python=3.8

# 激活环境
conda activate gatkPipeline

# 安装所需依赖
conda install -c bioconda gatk4 bwa samtools picard vcftools bcftools 
conda install -c bioconda fastp qualimap multiqc
```

### Conda环境中的依赖检测

该软件能够自动检测到它运行在Conda环境中，并相应地调整其依赖检查过程：

```
检测到conda环境: /home/user/miniconda3/envs/gatkPipeline
检测到Conda环境，且启用了版本检查跳过，仅检查软件是否存在
在conda环境中找到gatk: /home/user/miniconda3/envs/gatkPipeline/bin/gatk
在conda环境中找到bwa: /home/user/miniconda3/envs/gatkPipeline/bin/bwa
# 其他依赖检查...
```

### 自动使用Conda环境中的软件路径

当在Conda环境中运行时，软件会优先使用环境中的工具路径，无需在配置文件中明确指定完整路径。这简化了配置过程，特别是在不同系统间移植时。

实际使用中，Conda环境提供了一个稳定且独立的运行环境，能够避免系统级软件版本冲突，是运行此流程的推荐方式。

## 最佳实践与使用建议

基于实际运行测试，我们提供以下最佳实践建议：

### 1. 初次使用流程

如果您是首次使用该流程，建议按照以下步骤操作：

```bash
# 1. 先检查依赖
gatk-snp-pipeline check-deps

# 2. 运行测试模式验证安装
gatk-snp-pipeline run --test-mode

# 3. 如果测试成功，创建实际项目的配置文件
gatk-snp-pipeline init --config my_project.yaml

# 4. 编辑配置文件，设置参考基因组和样本路径
# 5. 运行实际项目
gatk-snp-pipeline run --config my_project.yaml
```

### 2. 性能优化建议

- **调整线程数**：测试表明，大多数步骤能有效利用8-16个线程。再增加线程数通常收益递减。
- **内存分配**：GATK工具（特别是HaplotypeCaller和CombineGVCFs）是内存密集型的。对大型数据集，建议至少分配16GB内存。
- **存储空间**：整个流程会生成多个中间文件。根据测试，建议为每个样本预留原始FASTQ文件大小5-10倍的存储空间。

### 3. 故障恢复与调试

当流程失败时：

```bash
# 使用详细模式查看更多信息
gatk-snp-pipeline run --config my_project.yaml --verbose

# 使用断点续运行恢复失败的流程
gatk-snp-pipeline run --config my_project.yaml --resume

# 只运行失败的步骤进行调试
gatk-snp-pipeline run --config my_project.yaml --step failed_step_name
```

### 4. 大规模数据处理

- 对于大型基因组或多样本数据集，推荐使用分阶段处理：

```bash
# 步骤1：运行到变异检测
gatk-snp-pipeline run --config my_project.yaml --from-step ref_index --to-step haplotype_caller

# 步骤2：完成剩余流程
gatk-snp-pipeline run --config my_project.yaml --from-step combine_gvcfs
```

### 5. 避免已知问题

- 确保bcftools版本支持query命令所需的参数
- 对于VCFtools，避免使用不支持的参数（如某些版本不支持--threads）
- 对于大文件，确保系统的文件描述符限制足够大

通过遵循这些最佳实践，您可以更高效地使用该SNP分析流程，并更轻松地解决可能遇到的问题。

## 环境配置

### 使用Conda/Mamba安装（推荐）

1. 安装Mamba（推荐）或Conda：
```bash
# 安装Mamba
conda install -n base -c conda-forge mamba

# 或使用Conda
# 从 https://docs.conda.io/en/latest/miniconda.html 下载并安装Miniconda
```

2. 创建并激活环境：
```bash
# 使用Mamba（推荐，更快）
mamba env create -f environment.yml
mamba activate gatk-snp-pipeline

# 或使用Conda
conda env create -f environment.yml
conda activate gatk-snp-pipeline
```

3. 验证安装：
```bash
gatk-snp-pipeline --version
```
