# GATK SNP Calling Workflow Package
# 初始化文件

# 导入主要模块
from .pipeline import Pipeline
from .logger import Logger
from .config_manager import ConfigManager

# 导入所有步骤类，方便直接导入
from .steps import (
    BaseStep,
    RefIndex,
    BwaMap,
    SortSam,
    MarkDuplicates,
    IndexBam,
    HaplotypeCaller,
    CombineGvcfs,
    GenotypeGvcfs,
    VcfFilter,
    SelectSnp,
    SoftFilterSnp,
    GetGwasData
)

# 定义公开的API
__all__ = [
    'Pipeline',
    'Logger',
    'ConfigManager',
    'BaseStep',
    'RefIndex',
    'BwaMap',
    'SortSam',
    'MarkDuplicates',
    'IndexBam',
    'HaplotypeCaller',
    'CombineGvcfs',
    'GenotypeGvcfs',
    'VcfFilter',
    'SelectSnp',
    'SoftFilterSnp',
    'GetGwasData'
]

# 版本信息
__version__ = '1.0.0' 