# GATK SNP Calling Pipeline

一个基于Python的GATK SNP Calling流程自动化工具，支持Linux和macOS平台。

## 项目结构

```
gatk_callSNP_workflow_package/
├── .github/                    # GitHub Actions工作流配置
│   └── workflows/
│       └── build.yml          # 自动构建配置
├── gatk_snp_pipeline/         # 主程序包
│   ├── __init__.py
│   ├── cli.py                # 命令行接口
│   ├── pipeline.py           # 流程控制
│   ├── config.py             # 配置管理
│   ├── dependency_checker.py # 依赖检查
│   └── logger.py             # 日志管理
├── src/                      # 源代码目录
│   └── steps/               # 流程步骤实现
├── build.py                 # 构建脚本
├── setup.py                # 安装配置
├── requirements.txt        # 依赖列表
├── README.md              # 项目说明
└── DEPENDENCY_TROUBLESHOOTING.md  # 依赖问题排查指南
```

## 环境要求

- Python 3.11+
- Linux/macOS操作系统
- 以下软件需要预先安装并添加到PATH：
  - GATK
  - BWA
  - samtools
  - bcftools
  - vcftools

## 安装方法

### 1. pip安装（推荐）

```bash
pip install gatk-snp-pipeline
```

### 2. 源码安装

```bash
git clone https://github.com/craftor18/gatk_callSNP_workflow_package.git
cd gatk_callSNP_workflow_package
pip install -e .
```

### 3. conda安装

```bash
conda install -c bioconda gatk-snp-pipeline
```

## 使用方法

### 1. 命令行接口

```bash
# 初始化配置文件
gatk-snp-pipeline init --config config.yaml

# 检查依赖
gatk-snp-pipeline check-deps

# 运行完整流程
gatk-snp-pipeline run --config config.yaml

# 运行特定步骤
gatk-snp-pipeline run --config config.yaml --step bwa_map

# 从特定步骤开始运行
gatk-snp-pipeline run --config config.yaml --from-step mark_duplicates
```

### 2. Python脚本

```python
from gatk_snp_pipeline import Pipeline, ConfigManager

# 加载配置
config = ConfigManager("config.yaml")

# 创建并运行流程
pipeline = Pipeline(config)
pipeline.run_all()
```

### 3. Jupyter Notebook

```python
from gatk_snp_pipeline import Pipeline, ConfigManager

# 加载配置
config = ConfigManager("config.yaml")

# 创建流程实例
pipeline = Pipeline(config)

# 运行单个步骤
pipeline.run_step("bwa_map")

# 运行从特定步骤开始
pipeline.run_from_step("mark_duplicates")
```

## 配置文件说明

配置文件使用YAML格式，包含以下主要部分：

```yaml
# 样本数据路径
samples:
  - path: /path/to/sample1.fastq
    name: sample1
  - path: /path/to/sample2.fastq
    name: sample2

# 输出目录
output_dir: /path/to/output

# 参考基因组
reference:
  fasta: /path/to/reference.fasta
  index: /path/to/reference.fasta.fai

# 性能设置
performance:
  threads_per_job: 4
  max_parallel_jobs: 2
  max_memory: 8G

# 任务优先级映射
priority_map:
  bwa_map: 1
  sort_sam: 2
  mark_duplicates: 3
  base_recalibrator: 4
  apply_bqsr: 5
  haplotype_caller: 6
  genotype_gvcfs: 7
  hard_filter_snps: 8
  soft_filter_snps: 9
```

## 依赖问题排查

如果遇到依赖问题，请参考 [DEPENDENCY_TROUBLESHOOTING.md](DEPENDENCY_TROUBLESHOOTING.md) 文件。

## 许可证

MIT License

## 流程步骤说明

1. **参考基因组索引** (`ref_index`)

   - 使用BWA创建索引
   - 使用GATK创建序列字典
   - 使用Samtools创建faidx索引
2. **BWA比对** (`bwa_map`)

   - 将测序数据比对到参考基因组
   - 生成SAM文件
3. **排序SAM文件** (`sort_sam`)

   - 使用Samtools或GATK排序SAM文件
   - 生成BAM文件
4. **标记重复序列** (`mark_duplicates`)

   - 使用GATK MarkDuplicates工具标记PCR重复序列
5. **索引BAM文件** (`index_bam`)

   - 为BAM文件创建索引
6. **GATK HaplotypeCaller** (`haplotype_caller`)

   - 使用GATK HaplotypeCaller检测变异
   - 生成GVCF文件
7. **合并GVCF文件** (`combine_gvcfs`)

   - 合并多个样本的GVCF文件
8. **基因型分型** (`genotype_gvcfs`)

   - 对合并的GVCF文件进行基因型分型
   - 生成VCF文件
9. **VCF过滤** (`vcf_filter`)

   - 使用GATK进行硬过滤
   - 删除不符合质量标准的变异
10. **选择SNP** (`select_snp`)

    - 从VCF文件中选择SNP变异
11. **SNP软过滤** (`soft_filter_snp`)

    - 使用vcftools进行软过滤
    - 在FILTER字段标记不符合标准的变异
    - 保留所有变异，便于后续分析
12. **获取GWAS数据** (`get_gwas_data`)

    - 准备GWAS分析所需的数据

## 错误处理

程序提供详细的错误信息和解决方案：

1. **依赖错误**

   - 显示缺失的软件
   - 提供安装命令
   - 建议替代方案
2. **配置错误**

   - 指出配置文件中错误的部分
   - 提供正确的配置示例
   - 自动修复常见错误
3. **运行时错误**

   - 记录详细的错误日志
   - 提供错误恢复建议
   - 支持断点续传

## 常见问题

1. **依赖检查失败**
   - 确保所有软件都已正确安装
   - 确保软件路径已添加到系统PATH
   - 如果依赖检测显示错误但软件已正确安装，可以手动验证：
     ```bash
     # 检查软件是否存在
     which software_name
     ```

2. **内存不足**
   - 增加系统内存
   - 调整配置文件中的`max_memory`参数
   - 减少`max_parallel_jobs`参数

3. **运行速度慢**
   - 增加`threads_per_job`参数
   - 增加`max_parallel_jobs`参数
   - 使用SSD存储

## 高级选项

### 依赖检查控制

GATK SNP Calling Pipeline提供了选项来控制依赖检查行为：

- `--skip-deps`: 完全跳过依赖检查，直接运行流程

例如：

```bash
# 完全跳过依赖检查
gatk-snp-pipeline run --config config.yaml --skip-deps
```

### 依赖问题排查

如果您在依赖检查中遇到问题，请参阅 [依赖问题排查指南](DEPENDENCY_TROUBLESHOOTING.md)。
