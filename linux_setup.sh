#!/bin/bash

# GATK SNP Calling Pipeline - Linux 安装脚本
# 此脚本帮助在Linux系统中安装软件包并解决常见问题

echo "===== GATK SNP Calling Pipeline - Linux 安装助手 ====="
echo "这个脚本将帮助您在Linux系统上安装和配置GATK SNP Calling Pipeline"
echo ""

# 检查当前环境
if [ -n "$CONDA_PREFIX" ]; then
    echo "检测到conda环境: $CONDA_PREFIX"
    echo "当前Python版本: $(python --version 2>&1)"
    echo "当前PATH环境变量: $PATH"
    echo ""
else
    echo "未检测到conda环境。强烈建议在conda环境中运行本工具。"
    echo "您可以通过以下命令创建新的conda环境："
    echo "conda create -n gatk-pipeline python=3.9"
    echo "conda activate gatk-pipeline"
    echo ""
    read -p "是否继续安装？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安装软件包
echo "开始安装GATK SNP Calling Pipeline..."
pip install -e . --use-pep517
if [ $? -ne 0 ]; then
    echo "尝试备选安装方法..."
    pip install -e .
    if [ $? -ne 0 ]; then
        echo "安装失败，请检查错误信息并手动解决。"
        exit 1
    fi
fi
echo "软件包安装完成！"
echo ""

# 检查依赖
echo "现在将检查依赖（跳过版本检查）..."
gatk-snp-pipeline check-deps --skip-version-check

echo ""
echo "===== 安装完成 ====="
echo "如果上面显示了依赖问题，请参考DEPENDENCY_TROUBLESHOOTING.md文件解决"
echo ""
echo "推荐使用的命令："
echo "1. 检查依赖（跳过版本检查）："
echo "   gatk-snp-pipeline check-deps --skip-version-check"
echo ""
echo "2. 运行流程（跳过版本检查）："
echo "   gatk-snp-pipeline run --config your_config.yaml --skip-version-check"
echo ""
echo "3. 如果确定所有依赖已正确安装，也可以完全跳过依赖检查："
echo "   gatk-snp-pipeline run --config your_config.yaml --skip-deps"
echo ""
echo "详细文档请参考README.md和DEPENDENCY_TROUBLESHOOTING.md" 