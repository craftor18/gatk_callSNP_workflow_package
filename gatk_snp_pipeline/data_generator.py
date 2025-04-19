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

# GC偏好的随机碱基生成器
def gc_biased_base(gc_content: float = 0.5) -> str:
    """根据GC含量偏好生成一个碱基"""
    if random.random() < gc_content:
        return random.choice(['G', 'C'])
    else:
        return random.choice(['A', 'T'])

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, output_dir: str, logger: Optional[Logger] = None, sequencing_type: str = "single"):
        self.output_dir = Path(output_dir)
        self.logger = logger
        self.sequencing_type = sequencing_type  # 测序类型: "single"(单端) 或 "paired"(双端)
        
        # 测试数据参数 - 改进以更接近真实数据
        self.reference_length = 50000    # 参考基因组长度增加到50kb
        self.chromosome_count = 3        # 染色体数量增加到3条
        self.read_length = 150           # 读取长度增加到150，更接近现代测序技术
        self.sample_count = 3            # 样本数量
        self.coverage = 15               # 覆盖度提高到15x，更接近真实数据要求
        self.snp_rate = 0.03             # SNP变异率提高到3%
        self.indel_rate = 0.01           # 添加1%的indel变异
        self.repeat_rate = 0.05          # 添加5%的重复区域
        self.repeat_length = 20          # 重复序列长度
        
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
                
                # 生成染色体序列，添加GC含量变化和重复区域
                sequence = []
                
                current_pos = 0
                while current_pos < self.reference_length:
                    # 随机决定当前区块的GC含量
                    gc_content = random.uniform(0.3, 0.7)
                    
                    # 生成区块长度
                    block_length = min(random.randint(500, 2000), self.reference_length - current_pos)
                    
                    # 生成序列
                    block_seq = ''.join(gc_biased_base(gc_content) for _ in range(block_length))
                    
                    # 添加重复区域
                    if random.random() < self.repeat_rate and current_pos + block_length + self.repeat_length <= self.reference_length:
                        # 生成重复单元
                        repeat_unit = ''.join(random_base() for _ in range(random.randint(3, 10)))
                        repeat_count = random.randint(3, 10)
                        repeat_seq = repeat_unit * repeat_count
                        
                        # 将重复单元插入到区块中
                        insert_pos = random.randint(0, len(block_seq) - 1)
                        block_seq = block_seq[:insert_pos] + repeat_seq + block_seq[insert_pos:]
                        
                        # 确保不超出总长度
                        block_seq = block_seq[:self.reference_length - current_pos]
                    
                    sequence.append(block_seq)
                    current_pos += len(block_seq)
                
                final_sequence = ''.join(sequence)
                
                # 写入序列，每行80个碱基
                for i in range(0, len(final_sequence), 80):
                    f.write(final_sequence[i:i+80] + '\n')
        
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
            
            # 为每个样本生成固定的变异位点，确保样本之间的差异
            sample_variants = self._generate_sample_variants(reference_sequences, sample_idx)
            
            if self.sequencing_type == "paired":
                # 双端测序：生成R1和R2两个FASTQ文件
                self._generate_paired_end_sample(sample_name, reads_count, reference_sequences, sample_variants)
            else:
                # 单端测序：生成单个FASTQ文件
                self._generate_single_end_sample(sample_name, reads_count, reference_sequences, sample_variants)
            
            self.log(f"样本 {sample_name} 生成完成")
    
    def _generate_single_end_sample(self, sample_name, reads_count, reference_sequences, sample_variants):
        """生成单端测序样本数据"""
        # 样本文件路径
        sample_path = self.samples_dir / f"{sample_name}.fastq.gz"
        
        # 生成FASTQ数据
        with gzip.open(sample_path, 'wt') as f:
            for read_idx in range(reads_count):
                # 随机选择一条染色体
                chrom = random.choice(list(reference_sequences.keys()))
                chrom_seq = reference_sequences[chrom]
                
                # 随机选择起始位置
                start_pos = random.randint(0, max(0, len(chrom_seq) - self.read_length))
                
                # 获取读数序列
                read_seq = chrom_seq[start_pos:start_pos + self.read_length]
                
                # 应用预定义的样本变异到读数序列
                modified_read = self._apply_variants(chrom, start_pos, read_seq, sample_variants)
                
                # 确保读数长度足够
                if len(modified_read) < self.read_length:
                    modified_read += ''.join(random_base() for _ in range(self.read_length - len(modified_read)))
                
                # 添加测序错误
                modified_read, qual = self._add_sequencing_errors(modified_read)
                
                # 写入FASTQ格式
                f.write(f"@{sample_name}_read_{read_idx}\n")
                f.write(f"{modified_read}\n")
                f.write(f"+\n")
                f.write(f"{qual}\n")
        
        self.log(f"单端测序样本文件生成完成: {sample_path}")
    
    def _generate_paired_end_sample(self, sample_name, reads_count, reference_sequences, sample_variants):
        """生成双端测序样本数据"""
        # 样本文件路径 - R1和R2
        sample_path_r1 = self.samples_dir / f"{sample_name}_R1.fastq.gz"
        sample_path_r2 = self.samples_dir / f"{sample_name}_R2.fastq.gz"
        
        # 生成FASTQ数据
        with gzip.open(sample_path_r1, 'wt') as f1, gzip.open(sample_path_r2, 'wt') as f2:
            for read_idx in range(reads_count):
                # 随机选择一条染色体
                chrom = random.choice(list(reference_sequences.keys()))
                chrom_seq = reference_sequences[chrom]
                
                # 随机选择起始位置，考虑片段大小
                fragment_size = random.randint(300, 500)
                start_pos = random.randint(0, max(0, len(chrom_seq) - fragment_size))
                
                # 应用预定义的样本变异到片段序列
                fragment_seq = chrom_seq[start_pos:start_pos + fragment_size]
                modified_fragment = self._apply_variants(chrom, start_pos, fragment_seq, sample_variants)
                
                # 从片段中提取正向和反向读数
                forward_read = modified_fragment[:min(self.read_length, len(modified_fragment))]
                reverse_start = max(0, len(modified_fragment) - self.read_length)
                reverse_read = self._reverse_complement(modified_fragment[reverse_start:])
                
                # 确保读数长度足够
                if len(forward_read) < self.read_length:
                    forward_read += ''.join(random_base() for _ in range(self.read_length - len(forward_read)))
                if len(reverse_read) < self.read_length:
                    reverse_read += ''.join(random_base() for _ in range(self.read_length - len(reverse_read)))
                
                # 添加测序错误
                forward_read, forward_qual = self._add_sequencing_errors(forward_read)
                reverse_read, reverse_qual = self._add_sequencing_errors(reverse_read)
                
                # 写入R1文件
                f1.write(f"@{sample_name}_read_{read_idx}/1\n")
                f1.write(f"{forward_read}\n")
                f1.write(f"+\n")
                f1.write(f"{forward_qual}\n")
                
                # 写入R2文件
                f2.write(f"@{sample_name}_read_{read_idx}/2\n")
                f2.write(f"{reverse_read}\n")
                f2.write(f"+\n")
                f2.write(f"{reverse_qual}\n")
        
        self.log(f"双端测序样本文件生成完成: R1={sample_path_r1}, R2={sample_path_r2}")
    
    def _generate_sample_variants(self, reference_sequences, sample_idx):
        """为每个样本生成固定的变异位点集合"""
        variants = {}
        
        # 对每条染色体生成变异
        for chrom, seq in reference_sequences.items():
            chrom_variants = []
            
            # 生成SNP变异
            snp_count = int(len(seq) * self.snp_rate)
            # 确保不取太多位置
            max_positions = min(snp_count, len(seq) // 2)
            snp_positions = random.sample(range(len(seq)), max_positions)
            
            for pos in snp_positions:
                ref_base = seq[pos]
                # 确保每个样本有不同的变异
                alt_base = random.choice([b for b in ['A', 'T', 'G', 'C'] if b != ref_base])
                # 只有当样本序号是奇数或者位置是奇数时才添加变异，创造样本间差异
                if sample_idx % 2 == pos % 2:
                    chrom_variants.append(('SNP', pos, ref_base, alt_base))
            
            # 生成Indel变异
            indel_count = int(len(seq) * self.indel_rate)
            # 确保不取太多位置
            max_indel_positions = min(indel_count, len(seq) // 4)
            if max_indel_positions > 0:
                indel_positions = random.sample(range(len(seq) - 10), max_indel_positions)
                
                for pos in indel_positions:
                    if random.random() < 0.5:  # 插入
                        insert_length = random.randint(1, 5)
                        insert_seq = ''.join(random_base() for _ in range(insert_length))
                        if sample_idx % 3 == pos % 3:  # 创造样本间差异
                            chrom_variants.append(('INS', pos, "", insert_seq))
                    else:  # 删除
                        del_length = random.randint(1, 5)
                        if pos + del_length < len(seq):
                            del_seq = seq[pos:pos+del_length]
                            if sample_idx % 3 == (pos % 3 + 1) % 3:  # 创造样本间差异
                                chrom_variants.append(('DEL', pos, del_seq, ""))
            
            variants[chrom] = chrom_variants
        
        return variants
    
    def _apply_variants(self, chrom, start_pos, seq, variants):
        """将变异应用到给定的序列上"""
        if chrom not in variants:
            return seq
        
        # 转换为可变对象
        seq_list = list(seq)
        
        # 计算片段覆盖的范围
        end_pos = start_pos + len(seq)
        
        # 应用该区域内的所有变异
        # 注意：为简化处理，我们从后往前应用变异，避免位置改变问题
        applicable_variants = [v for v in variants[chrom] 
                              if start_pos <= v[1] < end_pos]
        
        # 按位置降序排列
        applicable_variants.sort(key=lambda v: v[1], reverse=True)
        
        for var_type, pos, ref, alt in applicable_variants:
            rel_pos = pos - start_pos  # 相对位置
            
            # 确保rel_pos在有效范围内
            if rel_pos < 0 or rel_pos >= len(seq_list):
                continue
                
            if var_type == 'SNP':
                seq_list[rel_pos] = alt
            elif var_type == 'INS':
                seq_list.insert(rel_pos, alt)
            elif var_type == 'DEL':
                del_end = min(rel_pos + len(ref), len(seq_list))
                for i in range(rel_pos, del_end):
                    if i < len(seq_list):
                        seq_list[i] = ''  # 标记为删除
        
        # 过滤掉已删除的位置
        seq_list = [base for base in seq_list if base != '']
        
        return ''.join(seq_list)
    
    def _reverse_complement(self, seq):
        """生成序列的反向互补"""
        complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        return ''.join(complement.get(base, 'N') for base in reversed(seq))
    
    def _add_sequencing_errors(self, seq):
        """添加测序错误并生成质量分数"""
        # 错误率和质量分数参数
        base_error_rate = 0.001  # 基础错误率
        qual_range = (30, 40)    # 高质量范围
        error_qual_range = (5, 20)  # 错误位点质量范围
        
        # 处理序列和生成质量分数
        seq_with_errors = list(seq)
        quality_scores = []
        
        for i, base in enumerate(seq):
            # 随机决定是否引入错误
            if random.random() < base_error_rate:
                # 引入错误
                seq_with_errors[i] = random.choice([b for b in ['A', 'T', 'G', 'C'] if b != base])
                # 生成较低的质量分数
                quality_scores.append(chr(random.randint(*error_qual_range) + 33))
            else:
                # 生成高质量分数
                quality_scores.append(chr(random.randint(*qual_range) + 33))
        
        # 返回修改后的序列和质量分数
        return ''.join(seq_with_errors), ''.join(quality_scores)
    
    def _load_reference(self, reference_path: Path) -> dict:
        """加载参考基因组序列"""
        sequences = {}
        current_chrom = None
        current_seq = []
        
        with open(reference_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # 如果已经在读取某条染色体，保存之前的序列
                    if current_chrom:
                        sequences[current_chrom] = ''.join(current_seq)
                    
                    # 开始新的染色体
                    current_chrom = line[1:]
                    current_seq = []
                else:
                    current_seq.append(line)
        
        # 保存最后一条染色体
        if current_chrom:
            sequences[current_chrom] = ''.join(current_seq)
        
        return sequences 