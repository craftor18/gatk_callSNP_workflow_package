from setuptools import setup, find_packages

# 使用utf-8编码读取README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gatk-snp-pipeline",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyyaml>=6.0",
        "setuptools>=45.0.0",
        "wheel>=0.34.0",
        "psutil>=5.8.0",
    ],
    entry_points={
        "console_scripts": [
            "gatk-snp-pipeline=gatk_snp_pipeline.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A GATK SNP Calling Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gatk_callSNP_workflow_package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 