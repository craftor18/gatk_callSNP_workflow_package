# GATK SNP Pipeline

一个用于SNP检测和分析的流水线，基于GATK最佳实践开发。

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
  - fastp 0.20.0+
  - QualiMap 2.2.2+
  - Java 1.8+

## 安装

### 方法1：使用预编译二进制文件

```bash
# 下载最新版本
wget https://github.com/craftor18/gatk_callSNP_workflow_package/releases/download/v2.0.0/gatk-snp-pipeline-linux-x64

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

```bash
gatk-snp-pipeline check-deps
```

### 创建配置文件

```bash
# 创建配置文件模板
gatk-snp-pipeline init --config config.yaml
```

### 编辑配置文件

编辑生成的`config.yaml`文件，设置参考基因组路径、样本路径和其他参数。

### 查看可用步骤

```bash
# 列出所有可用步骤
gatk-snp-pipeline list-steps
```

### 运行特定步骤

```bash
# 只运行参考基因组索引步骤
gatk-snp-pipeline run --config config.yaml --step ref_index

# 运行序列比对步骤
gatk-snp-pipeline run --config config.yaml --step bwa_map
```

### 运行完整流程

```bash
gatk-snp-pipeline run --config config.yaml
```

### 全局选项

流程支持多种全局选项，可以更灵活地控制运行方式：

```bash
# 强制覆盖所有已存在的输出文件
gatk-snp-pipeline run --config config.yaml --force

# 从上次中断的步骤继续运行
gatk-snp-pipeline run --config config.yaml --resume

# 显示详细输出信息
gatk-snp-pipeline run --config config.yaml --verbose

# 静默模式，只显示错误信息
gatk-snp-pipeline run --config config.yaml --quiet

# 支持简写形式
gatk-snp-pipeline run --config config.yaml -f -r -v
```

### 文件格式转换

支持将VCF文件转换为CSV、TSV或BED格式：

```bash
# 转换为CSV格式
gatk-snp-pipeline convert --input results/snps.vcf --output results/snps.csv --format csv

# 转换为TSV格式
gatk-snp-pipeline convert --input results/snps.vcf --output results/snps.tsv --format tsv

# 转换为BED格式
gatk-snp-pipeline convert --input results/snps.vcf --output results/snps.bed --format bed
```

## 测试模式

本程序内置了测试数据生成功能，可以生成模拟的参考基因组和测序数据，便于验证流程是否正常工作。

### 生成测试数据

```bash
# 生成测试数据
gatk-snp-pipeline generate-test-data --output-dir test_data

# 生成测试数据并创建配置文件
gatk-snp-pipeline generate-test-data --output-dir test_data --create-config test_config.yaml
```

### 测试模式运行

测试模式会自动生成测试数据并运行完整流程，无需额外提供参考基因组和样本:

```bash
# 测试模式运行
gatk-snp-pipeline run --config test_config.yaml --test-mode
```

测试模式生成的数据量小，可以迅速验证整个流程的功能，适合以下场景:

1. 验证软件安装和依赖配置是否正确
2. 测试新增功能或修改后的流程
3. 快速演示流程的工作方式
4. 培训和教学

### 测试流程示例

以下是使用模拟数据运行完整测试流程的示例命令：

```bash
# 1. 生成测试数据和配置文件
gatk-snp-pipeline generate-test-data --output-dir test_data --create-config test_config.yaml

# 2. 一步运行完整流程(所有步骤)
gatk-snp-pipeline run --config test_config.yaml
```

## 断点续运行功能

流程支持从上次中断的地方继续运行，非常适合长时间运行的任务：

```bash
# 启用断点续运行模式
gatk-snp-pipeline run --config config.yaml --resume
```

断点续运行功能会：
1. 自动记录已完成的步骤
2. 在中断后重新启动时跳过已完成的步骤
3. 从上次中断的步骤继续执行
4. 保持之前的输出文件不变

## 性能优化

流程自动进行性能优化，根据系统资源调整参数:

1. **自动调整线程数**：根据CPU核心数自动设置合适的线程数量
2. **内存优化**：为GATK和其他工具分配最佳内存，避免内存不足或浪费
3. **每线程内存分配**：根据总内存和线程数优化每个线程的内存使用量

可以在配置文件中控制这些参数：

```yaml
# 性能相关参数
threads: 8                 # 线程数
max_memory: 32             # 最大内存使用量(GB)
memory_per_thread: 2       # 每线程内存分配(GB)
```

## 日志级别控制

可以通过命令行选项控制日志的详细程度：

```bash
# 详细模式，显示更多调试信息
gatk-snp-pipeline run --config config.yaml --verbose

# 静默模式，只显示错误信息
gatk-snp-pipeline run --config config.yaml --quiet
```

## 配置文件说明

以下是配置文件的主要字段：

```yaml
# 参考基因组
reference: path/to/reference.fasta

# 样本目录
samples_dir: path/to/samples

# 输出目录
output_dir: results

# 线程数
threads: 8

# 最大内存使用量(GB)
max_memory: 16

# 日志目录
log_dir: logs

# 软件路径
software:
  gatk: gatk
  bwa: bwa
  samtools: samtools
  picard: picard
  vcftools: vcftools
  bcftools: bcftools
  fastp: fastp
  qualimap: qualimap
  multiqc: multiqc

# GATK参数
gatk:
  convert_to_hemizygous: false

# 质量控制参数
quality_control:
  min_base_quality: 20
  min_mapping_quality: 30

# 变异过滤参数
variant_filter:
  quality_filter: "QD < 2.0 || FS > 60.0 || MQ < 40.0"
  filter_name: "basic_filter"
```

### 必需字段

- `reference`: 参考基因组FASTA文件的路径
- `samples_dir`: 包含样本FASTQ文件的目录
- `output_dir`: 输出文件的目录

### 可选字段

- `threads`: 使用的线程数（默认为8）
- `max_memory`: 最大内存使用量，单位GB（默认为16）
- `log_dir`: 日志文件目录（默认为logs）
- `software`: 软件路径配置
- `quality_control`: 质量控制参数
- `variant_filter`: 变异过滤参数

## 分析报告

流程完成后，会在输出目录生成`summary_report.txt`摘要报告，包含以下信息：

- 运行信息（时间、配置文件、参考基因组等）
- 统计信息（样本数量、SNP数量等）
- 执行的步骤及状态
- 结果文件列表及大小

例如：

```
=== GATK SNP调用流程摘要报告 ===

运行信息:
日期时间: 2024-04-19 15:30:45
配置文件: config.yaml
参考基因组: path/to/reference.fasta
样本目录: path/to/samples
输出目录: results

统计信息:
样本数量: 3
检测到的SNP数量: 12345
过滤后的SNP数量: 10890

执行的步骤:
- 参考基因组索引: 已完成
- BWA比对: 已完成
- 排序SAM文件: 已完成
- 标记重复序列: 已完成
- 索引BAM文件: 已完成
- GATK HaplotypeCaller: 已完成
- 合并GVCF文件: 已完成
- 基因型分型: 已完成
- VCF过滤: 已完成
- 选择SNP: 已完成
- SNP软过滤: 已完成
- 获取GWAS数据: 已完成

结果文件:
- combined.vcf: 65432.15 KB
- genotyped.vcf: 54321.54 KB
- filtered.vcf: 52345.87 KB
- snps.vcf: 32456.12 KB
- soft_filtered_snps.recode.vcf: 29876.43 KB
- gwas_data.txt: 12345.67 KB
```

## 流程步骤

流水线包括以下步骤：

1. **ref_index**: 参考基因组索引
   - 创建BWA索引
   - 创建序列字典
   - 创建FASTA索引

2. **bwa_map**: 序列比对
   - 使用BWA mem将FASTQ文件比对到参考基因组
   - 输出SAM格式

3. **sort_sam**: SAM文件排序
   - 将SAM文件排序为BAM格式

4. **mark_duplicates**: 标记重复序列
   - 使用GATK MarkDuplicates标记PCR和光学重复

5. **index_bam**: BAM索引
   - 创建排序后BAM文件的索引

6. **haplotype_caller**: 变异位点检测
   - 使用GATK HaplotypeCaller检测变异

7. **combine_gvcfs**: 合并GVCF文件
   - 合并多个样本的GVCF文件

8. **genotype_gvcfs**: 基因型分型
   - 对合并的GVCF文件进行基因型分型

9. **vcf_filter**: VCF过滤
   - 过滤变异位点

10. **select_snp**: 选择SNP
    - 从VCF中提取SNP

11. **soft_filter_snp**: SNP软过滤
    - 根据质量应用过滤器

12. **get_gwas_data**: 获取GWAS数据
    - 准备GWAS分析数据

## 许可证

本项目采用 MIT 许可证。

## 作者

Craftor
