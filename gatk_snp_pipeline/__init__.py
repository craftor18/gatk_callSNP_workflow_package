"""
GATK SNP 调用流程包
==================

一个用于SNP检测和分析的流水线，基于GATK最佳实践开发。
"""

__version__ = "2.0.0"
__author__ = "Craftor"

from .pipeline import Pipeline
from .config import ConfigManager
from .logger import Logger
from .dependency_checker import DependencyChecker

__all__ = ["Pipeline", "ConfigManager", "Logger", "DependencyChecker"] 