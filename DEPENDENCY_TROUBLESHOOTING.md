# 依赖问题排查指南

## 常见依赖检查问题

使用GATK SNP Calling Pipeline时，您可能会遇到依赖检查相关的问题。本文档提供一些常见问题的解决方案。

### 1. 无法找到必要软件

如果您收到以下错误之一：
```
未找到 bwa，请安装 bwa 0.7.17 或更高版本
未找到 gatk，请安装 gatk 4.2.0 或更高版本
...
```

**解决方案**：
- 确保已安装所需软件
- 确保软件在系统PATH中
- 如果使用conda环境，请确保已激活正确的环境
- 在Linux系统下，可以使用`which <软件名>`确认软件是否可被找到

### 2. 版本检查失败

如果依赖检查报告版本过低：
```
samtools 版本 0.0.0 低于要求的最低版本 1.10
```

**解决方案**：
- 更新软件到所需版本
- 如果使用conda环境且您确定版本正确但无法正确检测，可以使用`--skip-version-check`参数
- 在Linux系统下，可以手动运行`<软件名> --version`确认版本信息

### 3. Conda环境中的特殊问题

在Conda环境中可能会遇到PATH相关问题，导致无法正确检测软件。

**解决方案**：
1. 确保conda环境已正确激活
   ```bash
   conda activate your_env_name
   ```

2. 运行命令时添加`--skip-version-check`参数：
   ```bash
   gatk-snp-pipeline check-deps --skip-version-check
   gatk-snp-pipeline run --config config.yaml --skip-version-check
   ```
   
3. 使用最新的pip安装方式：
   ```bash
   # 使用PEP 517模式安装（推荐）
   pip install -e . --use-pep517
   
   # 或者使用传统模式
   pip install -e .
   ```

4. 确认conda环境中的软件是否正确安装：
   ```bash
   # 列出当前环境中已安装的软件包
   conda list | grep <软件名>
   
   # 验证软件是否可执行
   which <软件名>
   <软件名> --version
   ```

5. 如果仍然遇到问题，检查PATH环境变量：
   ```bash
   echo $PATH
   # 确保conda环境的bin目录在PATH中且位置靠前
   ```

### 4. 特定软件的特殊处理

一些软件可能有特殊的命名或调用方式：

1. **GATK**
   - 在不同系统中可能被命名为`gatk`或`gatk4`
   - 有时需要通过`java -jar gatk.jar`调用
   - 在conda环境中，可能安装在`$CONDA_PREFIX/bin`目录下

2. **Picard**
   - 可能被命名为`picard`或作为`picard.jar`存在
   - 通常需要通过`java -jar picard.jar`调用
   - 在conda环境中，可能被整合到gatk4中

3. **BWA**
   - 标准安装通常为`bwa`命令
   - BWA-MEM2可能被命名为`bwa-mem2`

### 5. 自定义安装路径的软件

如果您的软件安装在非标准位置，可能无法被检测到。

**解决方案**：
- 添加安装路径到系统PATH
  ```bash
  export PATH=$PATH:/path/to/your/software/bin
  ```
- 创建符号链接到`/usr/local/bin`或其他系统PATH包含的目录
  ```bash
  sudo ln -s /path/to/your/software/bin/<软件名> /usr/local/bin/<软件名>
  ```
- 使用`--skip-deps`参数完全跳过依赖检查（不推荐，除非您确定所有依赖都已正确安装）

### 6. 完全跳过依赖检查

如果您确定所有依赖都已正确安装，但仍然遇到检查问题，可以完全跳过依赖检查。

```bash
gatk-snp-pipeline run --config config.yaml --skip-deps
```

**注意**: 仅在您确定所有依赖都已正确安装时使用此选项，否则可能会在运行中遇到更多问题。

## 支持的软件版本

以下是GATK SNP Calling Pipeline支持的最低软件版本：

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

## 安装依赖

### 使用Conda安装依赖（推荐）

推荐使用Conda创建环境并安装所有依赖，这是最简单的方法：

```bash
# 创建conda环境
conda create -n gatk-pipeline python=3.9

# 激活环境
conda activate gatk-pipeline

# 安装依赖
conda install -c bioconda gatk4 bwa samtools picard vcftools bcftools fastp qualimap multiqc

# 安装本软件包（使用PEP 517模式）
pip install -e . --use-pep517
```

### 在Linux系统上安装

在Linux系统上，可以使用以下命令安装大部分依赖：

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install bwa samtools vcftools bcftools

# CentOS/RHEL
sudo yum install bwa samtools vcftools bcftools

# 对于其他工具，可能需要手动下载和安装
# GATK: https://github.com/broadinstitute/gatk/releases
# Picard: https://github.com/broadinstitute/picard/releases
# fastp: https://github.com/OpenGene/fastp
# qualimap: http://qualimap.conesalab.org/
```

### 手动安装依赖

如果您更喜欢手动安装，请访问每个工具的官方网站获取安装说明：

- GATK: https://github.com/broadinstitute/gatk
- BWA: https://github.com/lh3/bwa
- Samtools: http://www.htslib.org/
- Picard: https://broadinstitute.github.io/picard/
- VCFtools: https://vcftools.github.io/
- BCFtools: http://www.htslib.org/
- fastp: https://github.com/OpenGene/fastp
- Qualimap: http://qualimap.conesalab.org/
- MultiQC: https://multiqc.info/ 