import os
import random
import gzip
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from .logger import Logger

# 随机碱基生成器
def random_base() -> str:
    """随机生成一个碱基：A, T, G, C"""
    return random.choice(['A', 'T', 'G', 'C'])

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, output_dir: str, logger: Optional[Logger] = None):
        self.output_dir = Path(output_dir)
        self.logger = logger
        
        # 测试数据参数
        self.reference_length = 10000  # 参考基因组长度
        self.chromosome_count = 2      # 染色体数量
        self.read_length = 100         # 读取长度
        self.sample_count = 3          # 样本数量
        self.coverage = 5              # 覆盖度
        
        # 创建输出目录
        self.reference_dir = self.output_dir / "reference"
        self.samples_dir = self.output_dir / "samples"
        
        # 创建目录
        self.reference_dir.mkdir(exist_ok=True, parents=True)
        self.samples_dir.mkdir(exist_ok=True, parents=True)
        
    def log(self, message: str):
        """日志记录"""
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
            
    def generate_all(self) -> Tuple[str, str]:
        """生成所有测试数据"""
        self.log("开始生成测试数据")
        
        # 生成参考基因组
        ref_path = self._generate_reference()
        
        # 生成样本数据
        self._generate_samples(ref_path)
        
        self.log(f"测试数据生成完成: 参考基因组位于 {ref_path}, 样本数据位于 {self.samples_dir}")
        return str(ref_path), str(self.samples_dir)
        
    def _generate_reference(self) -> Path:
        """生成参考基因组"""
        self.log("生成参考基因组")
        
        # 参考基因组文件路径
        ref_path = self.reference_dir / "reference.fasta"
        
        # 创建参考基因组
        with open(ref_path, 'w') as f:
            for chrom in range(1, self.chromosome_count + 1):
                # 染色体名称
                f.write(f">chr{chrom}\n")
                
                # 生成染色体序列
                sequence = ''.join(random_base() for _ in range(self.reference_length))
                
                # 写入序列，每行80个碱基
                for i in range(0, len(sequence), 80):
                    f.write(sequence[i:i+80] + '\n')
        
        self.log(f"参考基因组生成完成: {ref_path}")
        return ref_path
    
    def _generate_samples(self, reference_path: Path):
        """生成样本测序数据"""
        self.log("生成样本测序数据")
        
        # 加载参考基因组
        reference_sequences = self._load_reference(reference_path)
        
        for sample_idx in range(1, self.sample_count + 1):
            sample_name = f"sample_{sample_idx}"
            self.log(f"生成样本: {sample_name}")
            
            # 计算需要生成的读取数
            total_ref_length = sum(len(seq) for seq in reference_sequences.values())
            reads_count = (total_ref_length * self.coverage) // self.read_length
            
            # 样本文件路径
            sample_path = self.samples_dir / f"{sample_name}.fastq.gz"
            
            # 生成FASTQ数据
            with gzip.open(sample_path, 'wt') as f:
                for read_idx in range(reads_count):
                    # 随机选择一条染色体
                    chrom = random.choice(list(reference_sequences.keys()))
                    chrom_seq = reference_sequences[chrom]
                    
                    # 随机选择起始位置
                    start_pos = random.randint(0, len(chrom_seq) - self.read_length)
                    
                    # 提取序列
                    read_seq = chrom_seq[start_pos:start_pos + self.read_length]
                    
                    # 添加随机变异 (SNP)
                    if random.random() < 0.01:  # 1%的变异率
                        snp_pos = random.randint(0, len(read_seq) - 1)
                        base = read_seq[snp_pos]
                        # 选择一个不同的碱基
                        new_base = random.choice([b for b in ['A', 'T', 'G', 'C'] if b != base])
                        read_seq = read_seq[:snp_pos] + new_base + read_seq[snp_pos+1:]
                    
                    # 生成质量分数
                    quality = ''.join(chr(random.randint(33, 73)) for _ in range(len(read_seq)))
                    
                    # 写入FASTQ格式
                    f.write(f"@{sample_name}_read_{read_idx}\n")
                    f.write(f"{read_seq}\n")
                    f.write(f"+\n")
                    f.write(f"{quality}\n")
            
            self.log(f"样本 {sample_name} 生成完成: {sample_path}")
    
    def _load_reference(self, reference_path: Path) -> dict:
        """加载参考基因组"""
        sequences = {}
        current_chrom = None
        current_seq = []
        
        with open(reference_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # 如果有之前的染色体，先保存它
                    if current_chrom is not None:
                        sequences[current_chrom] = ''.join(current_seq)
                    
                    # 新染色体
                    current_chrom = line[1:]  # 去掉'>'前缀
                    current_seq = []
                else:
                    # 添加序列
                    current_seq.append(line)
        
        # 保存最后一条染色体
        if current_chrom is not None:
            sequences[current_chrom] = ''.join(current_seq)
            
        return sequences 