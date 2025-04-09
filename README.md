# GATK SNP 检测流程

这是一个基于 GATK 的 SNP 检测流程工具，用于处理高通量测序数据并检测 SNP。

## 功能特点

- 完整的 GATK 最佳实践流程
- 支持单样本和多样本分析
- 自动化的质量控制
- 详细的日志记录
- 可配置的分析参数

## 系统要求

- Linux 操作系统
- 以下软件需要预先安装：
  - bwa
  - samtools
  - picard
  - vcftools
  - fastp
  - qualimap
  - java

## 安装

1. 从 [Release 页面](https://github.com/craftor18/gatk_callSNP_workflow_package/releases) 下载最新版本的预构建二进制可执行文件
2. 将可执行文件移动到系统路径中，例如：
   ```bash
   sudo mv gatk-snp-pipeline /usr/local/bin/
   ```
3. 确保可执行文件具有执行权限：
   ```bash
   sudo chmod +x /usr/local/bin/gatk-snp-pipeline
   ```

## 使用方法

### 1. 检查依赖

```bash
gatk-snp-pipeline check-deps
```

### 2. 运行分析

```bash
gatk-snp-pipeline run \
    --input-dir /path/to/input \
    --output-dir /path/to/output \
    --reference /path/to/reference.fa \
    --threads 8
```

### 3. 查看帮助

```bash
gatk-snp-pipeline --help
```

## 配置文件

程序会在以下位置查找配置文件：

1. 当前目录下的 `config.yaml`
2. 用户主目录下的 `.gatk-snp-pipeline/config.yaml`
3. 程序内置的默认配置

配置文件示例：

```yaml
# 参考基因组
reference: /path/to/reference.fa

# 线程数
threads: 8

# 质量控制参数
quality_control:
  min_base_quality: 20
  min_mapping_quality: 30

# GATK 参数
gatk:
  min_allele_fraction: 0.2
  min_base_quality: 20
```

## 输出文件

分析完成后，将在输出目录中生成以下文件：

- `alignment/`: BAM 文件
- `variants/`: VCF 文件
- `qc/`: 质量控制报告
- `logs/`: 运行日志

## 许可证

MIT

## 作者

Craftor
