# GATK SNP Calling Pipeline

基于Python实现的GATK SNP Calling流程，提供从参考基因组索引到SNP过滤的完整流程。

## 环境要求

### 系统要求

- 操作系统：Windows/Linux/macOS
- 内存：建议至少32GB
- 存储：根据数据量确定，建议至少100GB可用空间
- Java：Java 8或更高版本

### Python依赖

- Python >=3.6+
- pyyaml>=6.0
- setuptools>=45.0.0
- wheel>=0.34.0

### 生物信息学软件依赖

#### 可以通过conda/mamba安装的软件

```bash
mamba install -c bioconda:
- gatk4 (>=4.0.0.0)
- bwa (>=0.7.17)
- samtools (>=1.10)
- picard (>=2.27.0)
- vcftools (>=0.1.16)
- bcftools
- fastp (>=0.20.0)
- qualimap (>=2.2.2)
- multiqc (>=1.9)
```

#### 需要手动安装的软件

- bwa-mem2 (https://github.com/bwa-mem2/bwa-mem2)

## 安装方法

### 方法一：使用pip安装（推荐）

```bash
# 从PyPI安装
pip install gatk-snp-pipeline

# 或者从本地安装
pip install .
```

### 方法二：从源码安装

1. 克隆仓库

   ```bash
   git clone https://github.com/yourusername/gatk_callSNP_workflow_package.git
   cd gatk_callSNP_workflow_package
   ```
2. 安装Python依赖

   ```bash
   pip install -r requirements.txt
   ```
3. 安装生物信息学软件

   ```bash
   # 使用conda/mamba安装大部分依赖
   mamba create -n gatkPipeline
   mamba activate gatkPipeline
   mamba install -c bioconda gatk4 bwa samtools picard vcftools fastp qualimap multiqc bcftools

   # 手动安装bwa-mem2
   # 请参考 https://github.com/bwa-mem2/bwa-mem2 的安装说明
   ```

### 方法三：使用conda安装

```bash
# 创建并激活conda环境
conda create -n gatkPipeline
conda activate gatkPipeline

# 安装依赖
conda install -c bioconda gatk4 bwa samtools picard vcftools fastp qualimap multiqc bcftools

# 安装gatk-snp-pipeline
pip install gatk-snp-pipeline
```

## 使用方法

### 方法一：命令行方式

#### 1. 检查依赖

在开始之前，建议先检查所有依赖是否已正确安装：

```bash
gatk-snp-pipeline check-deps
```

#### 2. 创建配置文件

```bash
gatk-snp-pipeline init --config path/to/your/config.yaml
```

#### 3. 运行完整流程

```bash
gatk-snp-pipeline run --config path/to/your/config.yaml
```

#### 4. 运行单个步骤

```bash
gatk-snp-pipeline run --config path/to/your/config.yaml --step step_name
```

#### 5. 从特定步骤开始运行

```bash
gatk-snp-pipeline run --config path/to/your/config.yaml --from-step step_name
```

### 方法二：Python脚本方式

```python
from gatk_snp_pipeline import Pipeline, ConfigManager

# 创建配置管理器
config = ConfigManager("path/to/config.yaml")

# 创建并运行流程
pipeline = Pipeline(config)
result = pipeline.run_all()

# 或者只运行特定步骤
result = pipeline.run_step("ref_index")
```

### 方法三：Jupyter Notebook方式

```python
# 在Jupyter Notebook中
from gatk_snp_pipeline import Pipeline, ConfigManager

# 创建配置管理器
config = ConfigManager("path/to/config.yaml")

# 创建并运行流程
pipeline = Pipeline(config)

# 运行完整流程
result = pipeline.run_all()

# 或者运行特定步骤
result = pipeline.run_step("ref_index")

# 查看结果
print(result)
```

## 配置文件说明

配置文件使用YAML格式，包含以下主要部分：

```yaml
# 基本配置
samples_dir: /path/to/samples        # 测序数据目录
output_dir: /path/to/output         # 输出目录
reference_genome: /path/to/ref.fa   # 参考基因组路径

# 性能配置
threads_per_job: 8                  # 每个任务使用的线程数
max_parallel_jobs: 3                # 最大并行任务数
max_memory: 32                      # 最大内存使用量(GB)

# 软件路径配置（可选，如果软件在PATH中则不需要）
software_paths:
  gatk: /path/to/gatk
  bwa: /path/to/bwa
  samtools: /path/to/samtools
  # ... 其他软件路径
```

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
   - 检查软件版本是否满足要求
   - 确保软件路径已添加到系统PATH
2. **内存不足**

   - 增加系统内存
   - 调整配置文件中的`max_memory`参数
   - 减少`max_parallel_jobs`参数
3. **运行速度慢**

   - 增加`threads_per_job`参数
   - 增加`max_parallel_jobs`参数
   - 使用SSD存储

## 许可证

[许可证名称] - 查看 LICENSE 文件了解详情
