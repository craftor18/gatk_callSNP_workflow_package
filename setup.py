#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATK SNP Pipeline 安装配置
"""

from setuptools import setup, find_packages
import os
from pathlib import Path
from typing import List

def read_requirements() -> List[str]:
    """
    读取requirements.txt文件
    
    Returns:
        List[str]: 依赖包列表
    """
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def get_package_data() -> List[str]:
    """
    获取需要包含的包数据文件
    
    Returns:
        List[str]: 数据文件列表
    """
    return [
        'hooks/*.py',
        'lib/*',
        'templates/*',
        'config/*.yaml',
        'config/*.json'
    ]

# 使用utf-8编码读取README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gatk-snp-pipeline",
    version="2.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'gatk_snp_pipeline': get_package_data()
    },
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'gatk-snp-pipeline=gatk_snp_pipeline.main:main',
        ],
    },
    author="Craftor",
    author_email="craftor18@example.com",
    description="GATK SNP Calling Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/craftor18/gatk_callSNP_workflow_package",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
    project_urls={
        "Bug Reports": "https://github.com/craftor18/gatk_callSNP_workflow_package/issues",
        "Source": "https://github.com/craftor18/gatk_callSNP_workflow_package",
        "Documentation": "https://github.com/craftor18/gatk_callSNP_workflow_package/wiki",
    },
    keywords=[
        "bioinformatics",
        "genomics",
        "SNP",
        "GATK",
        "variant-calling",
        "pipeline"
    ],
) 