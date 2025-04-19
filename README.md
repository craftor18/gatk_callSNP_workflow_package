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

如果有缺失的软件，会显示相应的错误信息。你可以通过在配置文件中设置相应软件的完整路径来解决路径问题。

### 创建配置文件

```bash
# 创建配置文件模板
gatk-snp-pipeline init --config config.yaml
```

### 编辑配置文件

编辑生成的`config.yaml`文件，设置参考基因组路径、样本路径和其他参数：

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

### 查看可用步骤

在运行特定步骤前，可以查看所有可用的步骤列表：

```bash
# 列出所有可用步骤
gatk-snp-pipeline list-steps
```

这将显示以下步骤列表：

```
可用的流程步骤:
------------------------------------------------------------
步骤名称        描述                                      
------------------------------------------------------------
ref_index       参考基因组索引                            
bwa_map         BWA比对                                  
sort_sam        排序SAM文件                              
mark_duplicates 标记重复序列                              
index_bam       索引BAM文件                              
haplotype_caller GATK HaplotypeCaller                    
combine_gvcfs   合并GVCF文件                             
genotype_gvcfs  基因型分型                                
vcf_filter      VCF过滤                                  
select_snp      选择SNP                                  
soft_filter_snp SNP软过滤                                
get_gwas_data   获取GWAS数据                             
```

### 运行特定步骤

如果只需要运行流程中的特定步骤，可以使用`--step`选项：

```bash
# 只运行参考基因组索引步骤
gatk-snp-pipeline run --config config.yaml --step ref_index

# 运行序列比对步骤
gatk-snp-pipeline run --config config.yaml --step bwa_map
```

或者从特定步骤开始运行：

```bash
# 从标记重复序列步骤开始运行
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

### 运行完整流程

要运行从参考基因组索引到SNP分析的完整流程：

```bash
gatk-snp-pipeline run --config config.yaml
```

流程将按照以下顺序执行所有步骤：

1. 参考基因组索引
2. BWA比对
3. SAM文件排序
4. 标记重复序列
5. BAM文件索引
6. 变异位点检测
7. 合并GVCF文件
8. 基因型分型
9. VCF过滤
10. 选择SNP
11. SNP软过滤
12. 获取GWAS数据

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

# 跳过依赖检查
gatk-snp-pipeline run --config config.yaml --skip-deps

# 支持简写形式
gatk-snp-pipeline run --config config.yaml -f -r -v
```

### 文件格式转换

支持将VCF文件转换为CSV、TSV或BED格式，便于后续分析：

```bash
# 转换为CSV格式
gatk-snp-pipeline convert --input results/snps.vcf --output results/snps.csv --format csv

# 转换为TSV格式
gatk-snp-pipeline convert --input results/snps.vcf --output results/snps.tsv --format tsv

# 转换为BED格式
gatk-snp-pipeline convert --input results/snps.vcf --output results/snps.bed --format bed
```

## 测试模式

本程序内置了测试数据生成功能，可以生成模拟的参考基因组和测序数据，便于验证流程是否正常工作。支持生成单端测序和双端测序两种类型的测试数据。

### 生成测试数据

```bash
# 生成单端测序测试数据（默认）
gatk-snp-pipeline generate-test-data --output-dir test_data_single --sequencing-type single

# 生成双端测序测试数据
gatk-snp-pipeline generate-test-data --output-dir test_data_paired --sequencing-type paired

# 生成测试数据并创建配置文件
gatk-snp-pipeline generate-test-data --output-dir test_data_single --sequencing-type single --create-config test_config_single.yaml
gatk-snp-pipeline generate-test-data --output-dir test_data_paired --sequencing-type paired --create-config test_config_paired.yaml
```

测试数据包括：

- 小型模拟参考基因组（约10KB）
- 3个模拟样本的FASTQ文件
  - 单端测序：每个样本一个FASTQ文件 (sample_1.fastq.gz)
  - 双端测序：每个样本两个FASTQ文件 (sample_1_R1.fastq.gz, sample_1_R2.fastq.gz)
- 带有少量SNP和其他变异的序列

### 测试模式运行

测试模式会自动生成测试数据并运行完整流程，无需额外提供参考基因组和样本:

```bash
# 单端测序测试模式（默认）
gatk-snp-pipeline run --test-mode --test-sequencing-type single

# 双端测序测试模式
gatk-snp-pipeline run --test-mode --test-sequencing-type paired
```

或者使用已有的测试配置文件：

```bash
# 使用单端测序测试配置文件
gatk-snp-pipeline run --config test_config_single.yaml

# 使用双端测序测试配置文件
gatk-snp-pipeline run --config test_config_paired.yaml
```

### 单端和双端测序的区别

- **单端测序**：每个样本只有一个FASTQ文件，包含从DNA片段一端读取的序列。
- **双端测序**：每个样本有两个FASTQ文件（R1和R2），分别包含从DNA片段两端读取的序列。

在进行BWA比对时，软件会根据配置文件中的`sequencing_type`参数自动选择合适的比对命令：

- 单端测序：`bwa mem -t <threads> -R '<read_group>' <ref> <sample.fastq.gz>`
- 双端测序：`bwa mem -t <threads> -R '<read_group>' <ref> <sample_R1.fastq.gz> <sample_R2.fastq.gz>`

以下是单端和双端测序测试数据的命令行输出示例：

```
开始生成测试数据...
2025-04-19 22:49:51,958 - gatk_snp_pipeline - INFO - 开始生成测试数据
2025-04-19 22:49:51,959 - gatk_snp_pipeline - INFO - 生成参考基因组
2025-04-19 22:49:52,047 - gatk_snp_pipeline - INFO - 参考基因组生成完成: test_data_single/reference/reference.fasta
2025-04-19 22:49:52,048 - gatk_snp_pipeline - INFO - 生成样本测序数据
2025-04-19 22:49:52,049 - gatk_snp_pipeline - INFO - 生成样本: sample_1
2025-04-19 22:49:58,185 - gatk_snp_pipeline - INFO - 样本 sample_1 生成完成: test_data_single/samples/sample_1.fastq.gz
2025-04-19 22:49:58,186 - gatk_snp_pipeline - INFO - 生成样本: sample_2
2025-04-19 22:50:04,556 - gatk_snp_pipeline - INFO - 样本 sample_2 生成完成: test_data_single/samples/sample_2.fastq.gz
2025-04-19 22:50:04,557 - gatk_snp_pipeline - INFO - 生成样本: sample_3
2025-04-19 22:50:10,805 - gatk_snp_pipeline - INFO - 样本 sample_3 生成完成: test_data_single/samples/sample_3.fastq.gz
2025-04-19 22:50:10,807 - gatk_snp_pipeline - INFO - 测试数据生成完成: 参考基因组位于 test_data_single/reference/reference.fasta, 样本数据位于 test_data_single/samples
默认配置文件已生成: test_config_single.yaml
请编辑配置文件，设置参考基因组和样本目录等必要参数。
测试数据配置文件已创建: test_config_single.yaml
测试数据生成完成！参考基因组: test_data_single/reference/reference.fasta, 样本目录: test_data_single/samples
```

### 实际示例的运行时间

从上面的测试输出可以看到，使用测试数据运行完整流程的实际用时：

- 参考基因组索引：约6秒
- BWA比对：约2.5秒
- SAM文件排序：约1秒
- 标记重复序列：约73秒
- BAM文件索引：约0.1秒
- 变异位点检测：约223秒
- 合并GVCF文件：约16秒
- 基因型分型：约29秒
- VCF过滤：约12秒
- 选择SNP：约9秒
- SNP软过滤：约0.1秒
- 获取GWAS数据：约0.2秒

整个流程总用时约6分钟，这在普通服务器上是非常快的，适合快速验证。真实数据集处理时间会更长，取决于数据规模和系统性能。

### 测试流程示例

以下是使用模拟数据运行完整测试流程的示例命令：

```bash
# 1. 生成测试数据和配置文件
gatk-snp-pipeline generate-test-data --output-dir test_data_single --sequencing-type single --create-config test_config_single.yaml

# 2. 一步运行完整流程(所有步骤)
gatk-snp-pipeline run --config test_config_single.yaml
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

断点续运行会使用隐藏文件`.progress`来跟踪已完成的步骤，这个文件位于输出目录中。

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

注意：自动优化会尊重配置文件中的设置，但会根据系统资源做出合理调整。

## 日志级别控制

可以通过命令行选项控制日志的详细程度：

```bash
# 详细模式，显示更多调试信息
gatk-snp-pipeline run --config config.yaml --verbose

# 静默模式，只显示错误信息
gatk-snp-pipeline run --config config.yaml --quiet
```

日志文件默认保存在`logs`目录下，可以通过配置文件的`log_dir`参数修改。

## 工具兼容性说明

流程中使用的一些工具具有特定的兼容性要求：

1. **BCFtools**：在`get_gwas_data`步骤中，BCFtools的`query`命令**不支持**`--threads`选项。流程已自动处理此问题，不会向命令添加线程参数。
2. **VCFtools**：在`soft_filter_snp`步骤中，VCFtools的某些版本不支持`--threads`和`--geno`选项。

如果在运行过程中遇到工具兼容性问题，可以查看日志文件以获取详细错误信息，同时流程会尝试自适应调整命令参数以适应不同版本的工具。

## 配置文件详细说明

以下是配置文件的完整字段说明：

```yaml
# 基本参数
reference: path/to/reference.fasta         # 参考基因组路径（必需）
samples_dir: path/to/samples               # 样本目录路径（必需）
output_dir: results                        # 输出目录（必需）
sequencing_type: paired                    # 测序类型：paired(双端测序)或single(单端测序)，默认为paired

# 性能参数
threads: 8                                 # 线程数
max_memory: 16                             # 最大内存使用量(GB)
memory_per_thread: 2                       # 每线程内存分配(GB)

# 日志设置
log_dir: logs                              # 日志目录

# 软件路径（如果软件不在PATH中，需要提供完整路径）
software:
  gatk: gatk                               # GATK路径
  bwa: bwa                                 # BWA路径
  samtools: samtools                       # Samtools路径
  picard: picard                           # Picard路径
  vcftools: vcftools                       # VCFtools路径
  bcftools: bcftools                       # BCFtools路径
  fastp: fastp                             # fastp路径（可选）
  qualimap: qualimap                       # QualiMap路径（可选）
  multiqc: multiqc                         # MultiQC路径（可选）

# GATK特定参数
gatk:
  convert_to_hemizygous: false             # 是否转换为半合子（适用于单倍体生物）

# 质量控制参数
quality_control:
  min_base_quality: 20                     # 最小碱基质量
  min_mapping_quality: 30                  # 最小比对质量

# 变异过滤参数
variant_filter:
  quality_filter: "QD < 2.0 || FS > 60.0 || MQ < 40.0"  # 质量过滤表达式
  filter_name: "basic_filter"              # 过滤器名称
```

### 必需字段

以下字段是运行流程必需的：

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

## 输入文件要求

### 参考基因组

- 格式：FASTA (.fasta 或 .fa)
- 要求：序列应该有唯一的ID
- 建议：较长的连续序列（染色体或scaffold），避免过多小片段

### 样本文件

- 格式：FASTQ (.fastq 或 .fastq.gz)
- 命名：每个样本应有唯一的前缀，如 sample1.fastq.gz
- 支持的压缩：gzip
- 目录结构：所有FASTQ文件应位于配置文件中指定的samples_dir目录下
- 测序类型：支持Illumina双端或单端测序数据
  - 双端测序数据：文件名格式为`*_R1*.fastq.gz`和`*_R2*.fastq.gz`（如`sample1_R1.fastq.gz`和`sample1_R2.fastq.gz`）
  - 单端测序数据：文件名格式为`*.fastq.gz`（如`sample1.fastq.gz`）
- 配置设置：在配置文件中通过`sequencing_type`参数指定测序类型（"paired"或"single"）

## 输出文件说明

流程会在配置的输出目录中生成以下关键文件：

- `combined.vcf`: 合并的GVCF文件
- `genotyped.vcf`: 基因型分型后的VCF文件
- `filtered.vcf`: 质量过滤后的VCF文件
- `snps.vcf`: 提取的SNP变异位点
- `soft_filtered_snps.recode.vcf`: 软过滤后的SNP变异位点
- `gwas_data.txt`: 用于GWAS分析的数据文件
- `summary_report.txt`: 分析摘要报告

此外，流程还会生成每个样本的中间文件，如BAM文件、索引文件等。

## 分析报告

流程完成后，会在输出目录生成`summary_report.txt`摘要报告，包含以下信息：

- 运行信息（时间、配置文件、参考基因组等）
- 统计信息（样本数量、SNP数量等）
- 执行的步骤及状态
- 结果文件列表及大小

### 实际测试案例的摘要报告

以下是使用测试数据运行后实际生成的摘要报告示例：

```
=== GATK SNP调用流程摘要报告 ===

运行信息:
日期时间: 2025-04-19 22:56:49
配置文件: test_data_single/test_config_single.yaml
参考基因组: test_data_single/reference/reference.fasta
样本目录: test_data_single/samples
输出目录: test_data_single/results

统计信息:
样本数量: 3
检测到的SNP数量: 6600
过滤后的SNP数量: 6598

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
- combined.vcf: 9138.04 KB
- genotyped.vcf: 1854.87 KB
- filtered.vcf: 1880.27 KB
- snps.vcf: 1509.52 KB
- soft_filtered_snps.recode.vcf: 1517.84 KB
- gwas_data.txt: 172.85 KB
```

从上述报告可以看出，测试数据集生成了约6600个SNP位点，过滤后保留了6598个。主要生成的VCF文件大小从1.5MB到9MB不等，最终用于GWAS分析的数据文件大小约为172KB。

运行完整流程后，命令行界面也会直接显示此摘要信息：

```
=== 执行摘要 ===
=== GATK SNP调用流程摘要报告 ===
# 摘要报告内容...
流程执行成功
```

这使得用户可以快速了解流程执行的结果和产生的文件，方便后续分析。

## 流程步骤详细说明

### 1. ref_index: 参考基因组索引

创建参考基因组的多种索引，用于后续分析：

- BWA索引（用于序列比对）
- GATK序列字典（.dict文件）
- FASTA索引（.fai文件）

### 2. bwa_map: 序列比对

使用BWA mem算法将FASTQ格式的测序数据比对到参考基因组：

- 添加读组信息（@RG标签）
- 标记短分割比对（-M参数）
- 每个样本输出一个SAM文件

### 3. sort_sam: SAM文件排序

将SAM文件转换为排序后的BAM格式：

- 使用samtools进行排序
- 按照坐标排序
- 输出.sorted.bam文件

### 4. mark_duplicates: 标记重复序列

使用GATK MarkDuplicates标记PCR和光学重复：

- 默认不移除重复序列，仅标记
- 生成重复标记指标文件
- 输出.dedup.bam文件

### 5. index_bam: BAM索引

为排序后的BAM文件创建索引：

- 使用samtools index命令
- 生成.bai索引文件

### 6. haplotype_caller: 变异位点检测

使用GATK HaplotypeCaller检测变异：

- 使用GVCF模式（--emit-ref-confidence GVCF）
- 每个样本生成一个.g.vcf文件

### 7. combine_gvcfs: 合并GVCF文件

将多个样本的GVCF文件合并为一个文件：

- 使用GATK CombineGVCFs
- 输出combined.vcf文件

### 8. genotype_gvcfs: 基因型分型

对合并的GVCF文件进行基因型分型：

- 使用GATK GenotypeGVCFs
- 输出genotyped.vcf文件

### 9. vcf_filter: VCF过滤

对变异位点应用质量过滤器：

- 使用GATK VariantFiltration
- 应用配置文件中定义的过滤条件
- 输出filtered.vcf文件

### 10. select_snp: 选择SNP

从过滤后的VCF文件中提取SNP变异：

- 使用GATK SelectVariants
- 输出snps.vcf文件

### 11. soft_filter_snp: SNP软过滤

使用VCFtools对SNP应用更多过滤条件：

- 根据缺失率过滤（--max-missing）
- 根据最小等位基因频率过滤（--maf）
- 输出soft_filtered_snps.recode.vcf文件

### 12. get_gwas_data: 获取GWAS数据

将VCF文件转换为GWAS分析所需的格式：

- 使用BCFtools query提取必要的字段
- 输出gwas_data.txt文件
- **注意**: BCFtools的query命令不支持--threads选项

## 疑难解答

### 1. "依赖软件未找到"错误

**问题**：运行`check-deps`命令时报错，无法找到某些软件。

**解决方案**：

- 确保所有必需软件已安装并在PATH中
- 在配置文件的`software`部分指定完整路径
- 使用`--skip-deps`选项跳过依赖检查

### 2. 内存不足错误

**问题**：GATK工具报告内存不足错误。

**解决方案**：

- 减少`threads`值
- 增加`max_memory`值
- 确保系统有足够的可用内存

### 3. 找不到输入文件

**问题**：流程报错找不到输入文件。

**解决方案**：

- 检查配置文件中的路径是否正确
- 确保FASTQ文件位于`samples_dir`目录下
- 验证文件名格式是否正确

### 4. BCFtools query线程问题

**问题**：在`get_gwas_data`步骤报错"unrecognized option '--threads'"。

**解决方案**：

- 此问题已在v4版本中修复
- BCFtools的query命令不支持--threads选项
- 更新到最新版本的软件包

## 许可证

本项目采用 MIT 许可证。

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
