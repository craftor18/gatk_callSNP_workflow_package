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

### 2. 版本检查失败

如果依赖检查报告版本过低：
```
samtools 版本 0.0.0 低于要求的最低版本 1.10
```

**解决方案**：
- 更新软件到所需版本
- 如果使用conda环境且您确定版本正确但无法正确检测，可以使用`--skip-version-check`参数

### 3. Conda环境中的特殊问题

在Conda环境中可能会遇到PATH相关问题，导致无法正确检测软件。

**解决方案**：
1. 确保conda环境已正确激活
2. 运行命令时添加`--skip-version-check`参数：
   ```bash
   gatk-snp-pipeline check-deps --skip-version-check
   gatk-snp-pipeline run --config config.yaml --skip-version-check
   ```
   
3. 或者运行测试脚本验证：
   ```bash
   python test_deps.py --skip-version-check
   ```

### 4. 自定义安装路径的软件

如果您的软件安装在非标准位置，可能无法被检测到。

**解决方案**：
- 添加安装路径到系统PATH
- 创建符号链接到`/usr/local/bin`或其他系统PATH包含的目录
- 使用`--skip-deps`参数完全跳过依赖检查（不推荐，除非您确定所有依赖都已正确安装）

### 5. 完全跳过依赖检查

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

### 使用Conda安装依赖

推荐使用Conda创建环境并安装所有依赖：

```bash
# 创建conda环境
conda create -n gatk-pipeline python=3.9

# 激活环境
conda activate gatk-pipeline

# 安装依赖
conda install -c bioconda gatk4 bwa samtools picard vcftools bcftools fastp qualimap multiqc

# 安装本软件包
pip install .
```

### 手动安装依赖

如果您更喜欢手动安装，请访问每个工具的官方网站获取安装说明。 