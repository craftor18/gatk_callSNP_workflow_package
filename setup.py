from setuptools import setup, find_packages
import os

def read_requirements():
    """读取requirements.txt文件"""
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# 使用utf-8编码读取README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gatk-snp-pipeline",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'gatk-snp-pipeline=gatk_snp_pipeline.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="GATK SNP Calling Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gatk-snp-pipeline",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 