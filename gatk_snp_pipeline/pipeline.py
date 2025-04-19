from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import os
import glob
import psutil
from .config import ConfigManager
from .logger import Logger
import datetime

class Pipeline:
    """GATK SNP Calling流程控制类"""
    
    def __init__(self, config: ConfigManager, logger: Optional[Logger] = None):
        self.config = config
        self.logger = logger or Logger(config.get_log_path())
        self.steps = self._get_steps()
        
        # 自动优化性能参数
        self._optimize_performance_params()
    
    def _optimize_performance_params(self):
        """根据系统资源自动优化性能参数"""
        # 获取系统资源信息
        total_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False)
        total_memory_gb = psutil.virtual_memory().total / (1024 ** 3)  # 转换为GB
        
        # 记录系统资源信息
        self.logger.info(f"系统资源信息: CPU总核数={total_cores}, 物理核数={physical_cores}, 内存={total_memory_gb:.1f}GB")
        
        # 当前配置中的线程数
        current_threads = self.config.get("threads", 8)
        
        # 根据系统资源优化线程数
        if total_cores > 4:
            # 保留至少1个核心给系统
            recommended_threads = max(1, min(total_cores - 1, current_threads))
            if recommended_threads != current_threads:
                self.logger.info(f"根据系统资源优化线程数: {current_threads} -> {recommended_threads}")
                self.config.set("threads", recommended_threads)
                
        # 内存优化
        # GATK和其他工具的内存参数
        # 可用内存的70%，并保留至少2GB给系统
        available_memory_gb = max(2, total_memory_gb * 0.7)
        recommended_memory_gb = min(available_memory_gb, self.config.get("max_memory", 32))
        
        # 设置内存参数
        self.logger.info(f"设置最大内存使用: {recommended_memory_gb:.1f}GB")
        self.config.set("max_memory", recommended_memory_gb)
        
        # 为每个线程分配的内存
        memory_per_thread_gb = max(1, int(recommended_memory_gb / recommended_threads))
        self.logger.info(f"每线程内存分配: {memory_per_thread_gb}GB")
        self.config.set("memory_per_thread", memory_per_thread_gb)
    
    def _get_steps(self) -> Dict[str, Dict[str, Any]]:
        """获取所有步骤的配置"""
        return {
            "ref_index": {
                "name": "参考基因组索引",
                "command": self._get_ref_index_cmd,
                "dependencies": ["bwa", "gatk", "samtools"]
            },
            "bwa_map": {
                "name": "BWA比对",
                "command": self._get_bwa_map_cmd,
                "dependencies": ["bwa"]
            },
            "sort_sam": {
                "name": "排序SAM文件",
                "command": self._get_sort_sam_cmd,
                "dependencies": ["samtools"]
            },
            "mark_duplicates": {
                "name": "标记重复序列",
                "command": self._get_mark_duplicates_cmd,
                "dependencies": ["gatk"]
            },
            "index_bam": {
                "name": "索引BAM文件",
                "command": self._get_index_bam_cmd,
                "dependencies": ["samtools"]
            },
            "haplotype_caller": {
                "name": "GATK HaplotypeCaller",
                "command": self._get_haplotype_caller_cmd,
                "dependencies": ["gatk"]
            },
            "combine_gvcfs": {
                "name": "合并GVCF文件",
                "command": self._get_combine_gvcfs_cmd,
                "dependencies": ["gatk"]
            },
            "genotype_gvcfs": {
                "name": "基因型分型",
                "command": self._get_genotype_gvcfs_cmd,
                "dependencies": ["gatk"]
            },
            "vcf_filter": {
                "name": "VCF过滤",
                "command": self._get_vcf_filter_cmd,
                "dependencies": ["gatk"]
            },
            "select_snp": {
                "name": "选择SNP",
                "command": self._get_select_snp_cmd,
                "dependencies": ["gatk"]
            },
            "soft_filter_snp": {
                "name": "SNP软过滤",
                "command": self._get_soft_filter_snp_cmd,
                "dependencies": ["vcftools"]
            },
            "get_gwas_data": {
                "name": "获取GWAS数据",
                "command": self._get_gwas_data_cmd,
                "dependencies": ["bcftools"]
            }
        }
    
    def run_all(self) -> bool:
        """运行完整流程"""
        self.logger.info("开始运行完整流程")
        
        # 获取全局选项
        resume_mode = self.config.get_global_option("resume")
        
        # 如果是断点续运行模式，加载之前的进度
        if resume_mode:
            self.config.load_progress()
            self.logger.info(f"从断点处继续运行，已完成步骤: {', '.join(self.config.completed_steps)}")
        
        # 运行所有步骤
        for step_name, step in self.steps.items():
            # 如果断点续运行且此步骤已完成，则跳过
            if resume_mode and step_name in self.config.completed_steps:
                self.logger.info(f"跳过已完成步骤: {step['name']}")
                continue
                
            if not self.run_step(step_name):
                self.logger.error(f"步骤 {step_name} 执行失败")
                return False
            
            # 标记步骤为已完成
            self.config.mark_step_complete(step_name)
            
        self.logger.info("流程执行完成")
        self._generate_summary_report()
        return True
    
    def run_step(self, step_name: str) -> bool:
        """运行特定步骤"""
        if step_name not in self.steps:
            self.logger.error(f"未知的步骤: {step_name}")
            return False
        
        step = self.steps[step_name]
        self.logger.info(f"开始执行步骤: {step['name']}")
        
        # 设置当前步骤
        self.config.current_step = step_name
        
        try:
            cmd = step["command"]()
            cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd[0]
            self.logger.info(f"执行命令: {cmd_str}")
            
            # 处理单元素字符串列表的情况（如_get_combine_gvcfs_cmd返回的格式）
            if len(cmd) == 1 and isinstance(cmd[0], str):
                # 使用shell=True执行完整命令字符串
                result = subprocess.run(
                    cmd[0],
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
            # 检查命令中是否包含shell操作符
            elif any(op in cmd_str for op in ['&&', '||', '>', '<', '|', ';']):
                # 使用shell=True执行包含shell操作符的命令
                result = subprocess.run(
                    cmd_str,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
            else:
                # 使用普通方式执行不包含shell操作符的命令
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            self.logger.info(f"步骤 {step_name} 执行成功")
            
            # 如果启用了详细模式，输出命令结果
            if self.config.get_global_option("verbose"):
                self.logger.info(f"命令输出:\n{result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"步骤 {step_name} 执行失败: {e.stderr}")
            
            # 输出详细错误信息
            self.logger.error(f"命令返回码: {e.returncode}")
            self.logger.error(f"命令输出:\n{e.stdout}")
            self.logger.error(f"命令错误:\n{e.stderr}")
            
            return False
        except Exception as e:
            self.logger.error(f"步骤 {step_name} 执行出错: {str(e)}")
            import traceback
            self.logger.error(f"异常详情:\n{traceback.format_exc()}")
            return False
    
    def run_from_step(self, step_name: str) -> bool:
        """从特定步骤开始运行"""
        if step_name not in self.steps:
            self.logger.error(f"未知的步骤: {step_name}")
            return False
        
        step_names = list(self.steps.keys())
        step_index = step_names.index(step_name)
        
        # 如果是从中间步骤开始运行，检查依赖是否满足
        if step_index > 0:
            self.logger.info(f"从步骤 {step_name} 开始运行，检查依赖...")
            
            # 检查输入文件是否存在
            if not self._check_step_dependencies(step_name):
                self.logger.error(f"步骤 {step_name} 的依赖文件不存在，请先运行前置步骤")
                return False
        
        # 运行指定步骤及后续步骤
        for step in step_names[step_index:]:
            if not self.run_step(step):
                return False
            # 标记步骤为已完成
            self.config.mark_step_complete(step)
            
        return True
    
    def _check_step_dependencies(self, step_name: str) -> bool:
        """检查步骤的依赖是否满足
        
        Args:
            step_name: 步骤名称
            
        Returns:
            依赖是否满足
        """
        # 根据步骤名称检查相应的输入文件
        output_dir = self.config.get("output_dir", ".")
        
        if step_name == "bwa_map":
            # 检查参考基因组索引
            ref = self.config.get("reference")
            return all(os.path.exists(f"{ref}{ext}") for ext in [".amb", ".ann", ".bwt", ".pac", ".sa"])
            
        elif step_name == "sort_sam":
            # 检查SAM文件
            sam_pattern = f"{output_dir}/*.sam"
            return len(glob.glob(sam_pattern)) > 0
            
        elif step_name == "mark_duplicates":
            # 检查排序后的BAM文件
            bam_pattern = f"{output_dir}/*.sorted.bam"
            return len(glob.glob(bam_pattern)) > 0
            
        elif step_name == "index_bam":
            # 检查去重后的BAM文件
            bam_pattern = f"{output_dir}/*.dedup.bam"
            return len(glob.glob(bam_pattern)) > 0
            
        elif step_name == "haplotype_caller":
            # 检查索引后的BAM文件
            bam_pattern = f"{output_dir}/*.dedup.bam"
            bai_pattern = f"{output_dir}/*.dedup.bai"
            return len(glob.glob(bam_pattern)) > 0 and len(glob.glob(bai_pattern)) > 0
            
        elif step_name == "combine_gvcfs":
            # 检查GVCF文件
            gvcf_pattern = f"{output_dir}/*.g.vcf"
            return len(glob.glob(gvcf_pattern)) > 0
            
        elif step_name == "genotype_gvcfs":
            # 检查合并后的VCF文件
            vcf_path = f"{output_dir}/combined.vcf"
            return os.path.exists(vcf_path)
            
        elif step_name == "vcf_filter":
            # 检查基因型分型后的VCF文件
            vcf_path = f"{output_dir}/genotyped.vcf"
            return os.path.exists(vcf_path)
            
        elif step_name == "select_snp":
            # 检查过滤后的VCF文件
            vcf_path = f"{output_dir}/filtered.vcf"
            return os.path.exists(vcf_path)
            
        elif step_name == "soft_filter_snp":
            # 检查SNP VCF文件
            vcf_path = f"{output_dir}/snps.vcf"
            return os.path.exists(vcf_path)
            
        elif step_name == "get_gwas_data":
            # 检查软过滤后的SNP VCF文件
            vcf_path = f"{output_dir}/soft_filtered_snps.recode.vcf"
            if not os.path.exists(vcf_path):
                vcf_path = f"{output_dir}/soft_filtered_snps.vcf"
            return os.path.exists(vcf_path)
            
        # 默认情况下，如果不知道如何检查依赖，返回True
        return True
    
    def _generate_summary_report(self) -> None:
        """生成分析摘要报告"""
        output_dir = self.config.get("output_dir", ".")
        report_path = os.path.join(output_dir, "summary_report.txt")
        
        try:
            with open(report_path, 'w') as f:
                f.write("=== GATK SNP调用流程摘要报告 ===\n\n")
                
                # 写入运行信息
                f.write("运行信息:\n")
                f.write(f"日期时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"配置文件: {self.config.config_path}\n")
                f.write(f"参考基因组: {self.config.get('reference')}\n")
                f.write(f"样本目录: {self.config.get('samples_dir')}\n")
                f.write(f"输出目录: {self.config.get('output_dir')}\n\n")
                
                # 统计信息
                f.write("统计信息:\n")
                
                # 样本数量
                sample_pattern = f"{self.config.get('samples_dir')}/*.fastq.gz"
                sample_count = len(glob.glob(sample_pattern))
                f.write(f"样本数量: {sample_count}\n")
                
                # SNP数量
                snp_vcf = os.path.join(output_dir, "snps.vcf")
                if os.path.exists(snp_vcf):
                    snp_count = self._count_variants(snp_vcf)
                    f.write(f"检测到的SNP数量: {snp_count}\n")
                
                # 过滤后的SNP数量
                filtered_snp_vcf = os.path.join(output_dir, "soft_filtered_snps.recode.vcf")
                if not os.path.exists(filtered_snp_vcf):
                    filtered_snp_vcf = os.path.join(output_dir, "soft_filtered_snps.vcf")
                
                if os.path.exists(filtered_snp_vcf):
                    filtered_snp_count = self._count_variants(filtered_snp_vcf)
                    f.write(f"过滤后的SNP数量: {filtered_snp_count}\n")
                
                f.write("\n执行的步骤:\n")
                for step_name, step_info in self.steps.items():
                    status = "已完成" if step_name in self.config.completed_steps else "未执行"
                    f.write(f"- {step_info['name']}: {status}\n")
                
                f.write("\n结果文件:\n")
                result_files = [
                    f"{output_dir}/combined.vcf",
                    f"{output_dir}/genotyped.vcf",
                    f"{output_dir}/filtered.vcf",
                    f"{output_dir}/snps.vcf",
                    f"{output_dir}/soft_filtered_snps.recode.vcf",
                    f"{output_dir}/gwas_data.txt"
                ]
                
                for file_path in result_files:
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path) / 1024  # KB
                        f.write(f"- {os.path.basename(file_path)}: {size:.2f} KB\n")
            
            self.logger.info(f"分析摘要报告已生成: {report_path}")
        
        except Exception as e:
            self.logger.error(f"生成摘要报告失败: {str(e)}")
    
    def _count_variants(self, vcf_path: str) -> int:
        """统计VCF文件中的变异数量
        
        Args:
            vcf_path: VCF文件路径
            
        Returns:
            变异数量
        """
        count = 0
        
        try:
            with open(vcf_path, 'r') as f:
                for line in f:
                    if not line.startswith('#'):
                        count += 1
        except Exception as e:
            self.logger.error(f"统计变异数量失败: {str(e)}")
        
        return count
    
    def _get_ref_index_cmd(self) -> List[str]:
        """获取参考基因组索引命令"""
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        bwa = self.config.get_software_path("bwa")
        gatk = self.config.get_software_path("gatk")
        samtools = self.config.get_software_path("samtools")
        
        # 获取字典文件路径和目录
        ref_path = Path(ref)
        dict_path = ref_path.with_suffix('.dict')
        
        # 根据force选项决定是否删除已有文件
        commands = []
        
        # 如果启用了强制覆盖，添加删除已有索引文件的命令
        if self.config.get_global_option("force"):
            commands.extend([
                f"rm -f {ref}.amb {ref}.ann {ref}.bwt {ref}.pac {ref}.sa {dict_path} {ref}.fai",
                "&&"
            ])
        else:
            # 只删除dict文件，避免冲突
            commands.extend([
                f"rm -f {dict_path}",
                "&&"
            ])
        
        # 添加创建索引的命令
        commands.extend([
            bwa, "index", ref,
            "&&",
            gatk, "CreateSequenceDictionary",
            "-R", ref,
            "-O", str(dict_path),
            "&&",
            samtools, "faidx", ref
        ])
        
        return commands
    
    def _get_bwa_map_cmd(self) -> List[str]:
        """获取BWA比对命令"""
        bwa = self.config.get_software_path("bwa")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        samples_dir = self.config.get("samples_dir")
        if not samples_dir:
            raise ValueError("配置文件中缺少 samples_dir 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        threads = str(self.config.get("threads", 8))
        
        # 获取样本文件列表，处理通配符路径
        sample_pattern = f"{samples_dir}/*.fastq.gz"
        sample_files = glob.glob(sample_pattern)
        
        if not sample_files:
            raise FileNotFoundError(f"未找到与模式 {sample_pattern} 匹配的样本文件")
        
        # 处理多个样本的情况
        cmds = []
        for sample_file in sample_files:
            sample_name = os.path.basename(sample_file).split('.')[0]
            output_sam = f"{output_dir}/{sample_name}.sam"
            
            # 添加读组信息，这对GATK至关重要
            read_group = f"@RG\\tID:{sample_name}\\tSM:{sample_name}\\tPL:ILLUMINA\\tLB:{sample_name}_lib\\tPU:unit1"
            
            cmd = [
                bwa, "mem",
                "-t", threads,
                "-M",  # 添加-M参数，标记短分割比对
                "-R", f"'{read_group}'",  # 添加读组信息
                ref,
                sample_file,
                ">", output_sam
            ]
            cmds.append(' '.join(cmd))
            
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_sort_sam_cmd(self) -> List[str]:
        """获取排序SAM文件命令"""
        samtools = self.config.get_software_path("samtools")
        
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有SAM文件
        sam_pattern = f"{output_dir}/*.sam"
        sam_files = glob.glob(sam_pattern)
        
        if not sam_files:
            raise FileNotFoundError(f"未找到与模式 {sam_pattern} 匹配的SAM文件")
        
        # 处理多个SAM文件的情况
        cmds = []
        for sam_file in sam_files:
            sample_name = os.path.basename(sam_file).split('.')[0]
            output_bam = f"{output_dir}/{sample_name}.sorted.bam"
            threads = str(self.config.get("threads", 8))
            memory_per_thread = str(self.config.get("memory_per_thread", 2))
            
            cmd = [
                samtools, "sort",
                "-@", threads,
                "-m", f"{memory_per_thread}G",  # 每个线程使用的内存
                "-o", output_bam,
                sam_file
            ]
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_mark_duplicates_cmd(self) -> List[str]:
        """获取标记重复序列命令"""
        gatk = self.config.get_software_path("gatk")
        
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有排序后的BAM文件
        bam_pattern = f"{output_dir}/*.sorted.bam"
        bam_files = glob.glob(bam_pattern)
        
        if not bam_files:
            raise FileNotFoundError(f"未找到与模式 {bam_pattern} 匹配的BAM文件")
        
        # 处理多个BAM文件的情况
        cmds = []
        for bam_file in bam_files:
            sample_name = os.path.basename(bam_file).split('.')[0]
            output_bam = f"{output_dir}/{sample_name}.dedup.bam"
            metrics = f"{output_dir}/{sample_name}.metrics.txt"
            
            # 设置Java最大内存
            max_memory_gb = int(self.config.get("max_memory", 32))
            java_mem = f"-Xmx{max_memory_gb}g"
            
            cmd = [
                gatk, "--java-options", java_mem, "MarkDuplicates",
                "-I", bam_file,
                "-O", output_bam,
                "-M", metrics,
                "--CREATE_INDEX", "true",
                "--VALIDATION_STRINGENCY", "SILENT",
                "--REMOVE_DUPLICATES", "false"
            ]
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_index_bam_cmd(self) -> List[str]:
        """获取索引BAM文件命令"""
        samtools = self.config.get_software_path("samtools")
        
        output_dir = self.config.get("output_dir", ".")
        
        # 获取所有去重后的BAM文件
        bam_pattern = f"{output_dir}/*.dedup.bam"
        bam_files = glob.glob(bam_pattern)
        
        if not bam_files:
            raise FileNotFoundError(f"未找到与模式 {bam_pattern} 匹配的BAM文件")
        
        # 构建索引命令
        cmds = []
        for bam_file in bam_files:
            cmd = [samtools, "index", bam_file]
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_haplotype_caller_cmd(self) -> List[str]:
        """获取HaplotypeCaller命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有去重和索引后的BAM文件
        bam_pattern = f"{output_dir}/*.dedup.bam"
        bam_files = glob.glob(bam_pattern)
        
        if not bam_files:
            raise FileNotFoundError(f"未找到与模式 {bam_pattern} 匹配的BAM文件")
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        # 处理多个BAM文件的情况
        cmds = []
        for bam_file in bam_files:
            sample_name = os.path.basename(bam_file).split('.')[0]
            output_gvcf = f"{output_dir}/{sample_name}.g.vcf"
            
            # 确保参数格式正确，使用空格分隔每个参数
            cmd = [
                gatk, "--java-options", java_mem, "HaplotypeCaller",
                "-R", ref,
                "-I", bam_file,
                "-O", output_gvcf
            ]
            
            # 添加额外参数，确保它们是正确分隔的独立参数
            cmd.extend(["--emit-ref-confidence", "GVCF"])
            
            cmds.append(' '.join(cmd))
        
        # 连接所有命令
        return [' && '.join(cmds)]
    
    def _get_combine_gvcfs_cmd(self) -> List[str]:
        """获取合并GVCF文件命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # 获取所有GVCF文件
        gvcf_pattern = f"{output_dir}/*.g.vcf"
        gvcf_files = glob.glob(gvcf_pattern)
        
        if not gvcf_files:
            raise FileNotFoundError(f"未找到与模式 {gvcf_pattern} 匹配的GVCF文件")
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        # 构建命令，为每个GVCF文件添加-V参数
        cmd = [
            gatk, "--java-options", f'"{java_mem}"', "CombineGVCFs", "-R", ref
        ]
        
        for gvcf_file in gvcf_files:
            cmd.extend(["-V", gvcf_file])
        
        cmd.extend(["-O", f"{output_dir}/combined.vcf"])
        
        # 添加可选参数
        if self.config.get("gatk", {}).get("convert_to_hemizygous", False):
            cmd.extend(["--convert-to-hemizygous"])
            
        # 返回字符串列表而不是命令列表
        return [' '.join(cmd)]
    
    def _get_genotype_gvcfs_cmd(self) -> List[str]:
        """获取基因型分型命令"""
        gatk = self.config.get_software_path("gatk")
        ref = self.config.get("reference")
        if not ref:
            raise ValueError("配置文件中缺少 reference 字段")
            
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/combined.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_vcf = f"{output_dir}/genotyped.vcf"
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        return [
            gatk, "--java-options", java_mem, "GenotypeGVCFs",
            "-R", ref,
            "-V", input_vcf,
            "-O", output_vcf
        ]
    
    def _get_vcf_filter_cmd(self) -> List[str]:
        """获取VCF过滤命令"""
        gatk = self.config.get_software_path("gatk")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/genotyped.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_vcf = f"{output_dir}/filtered.vcf"
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        # 为过滤表达式添加引号，防止shell特殊字符被误解
        cmd = [
            gatk, "--java-options", f'"{java_mem}"', "VariantFiltration",
            "-V", input_vcf,
            "-O", output_vcf,
            "--filter-expression", '"QD < 2.0 || FS > 60.0 || MQ < 40.0"',
            "--filter-name", "my_filter"
        ]
        
        # 返回字符串列表而不是命令列表
        return [' '.join(cmd)]
    
    def _get_select_snp_cmd(self) -> List[str]:
        """获取选择SNP命令"""
        gatk = self.config.get_software_path("gatk")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/filtered.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_vcf = f"{output_dir}/snps.vcf"
        
        # 设置Java最大内存
        max_memory_gb = int(self.config.get("max_memory", 32))
        java_mem = f"-Xmx{max_memory_gb}g"
        
        return [
            gatk, "--java-options", java_mem, "SelectVariants",
            "-V", input_vcf,
            "-O", output_vcf,
            "-select-type", "SNP"
        ]
    
    def _get_soft_filter_snp_cmd(self) -> List[str]:
        """获取SNP软过滤命令"""
        vcftools = self.config.get_software_path("vcftools")
        output_dir = self.config.get("output_dir", ".")
        input_vcf = f"{output_dir}/snps.vcf"
        if not os.path.exists(input_vcf):
            raise FileNotFoundError(f"找不到输入文件: {input_vcf}")
        
        output_prefix = f"{output_dir}/soft_filtered_snps"
        
        # 对于测试数据使用更宽松的过滤条件
        # --max-missing: 允许的最小非缺失数据比例（0-1），设置为0.3表示每个位点至少有30%的样本有基因型
        # --maf: 最小等位基因频率，设置为0.01表示保留至少有1%频率的变异
        # 注意：此版本的vcftools不支持--threads和--geno选项
        cmd = [
            vcftools,
            "--vcf", input_vcf,
            "--max-missing", "0.3",   # 允许最多70%的缺失率
            "--maf", "0.01",         # 非常宽松的最小等位基因频率
            "--recode",
            "--recode-INFO-all",
            "--out", output_prefix
        ]
        
        # 返回字符串列表格式
        return [' '.join(cmd)]
    
    def _get_gwas_data_cmd(self) -> List[str]:
        """获取GWAS数据命令"""
        # 明确记录警告信息：bcftools query 不支持 --threads 选项
        self.logger.warning("注意: bcftools query 命令不支持 --threads 选项，确保命令执行时不会添加此参数")
        
        bcftools = self.config.get_software_path("bcftools")
        output_dir = self.config.get("output_dir", ".")
        
        # 首先尝试使用软过滤后的文件
        possible_input_files = [
            # 按优先级排序
            f"{output_dir}/soft_filtered_snps.recode.vcf",  # vcftools标准输出
            f"{output_dir}/soft_filtered_snps.vcf",         # 可能的替代名称
            f"{output_dir}/soft_filtered_snps.recode.vcf.gz" # 压缩版本
        ]
        
        # 如果无法找到软过滤文件，回退使用原始SNP文件
        fallback_files = [
            f"{output_dir}/snps.vcf",
            f"{output_dir}/snps.vcf.gz"
        ]
        
        # 合并所有可能的文件列表
        all_possible_files = possible_input_files + fallback_files
        
        # 尝试查找可用的输入文件
        input_vcf = None
        for file_path in all_possible_files:
            if os.path.exists(file_path):
                input_vcf = file_path
                break
        
        if input_vcf is None:
            raise FileNotFoundError(f"找不到任何可用的SNP文件，已尝试: {', '.join(all_possible_files)}")
        
        # 记录使用的文件路径
        is_fallback = input_vcf in fallback_files
        if is_fallback:
            self.logger.warning(f"未找到软过滤SNP文件，回退使用原始SNP文件: {input_vcf}")
        else:
            self.logger.info(f"使用软过滤SNP文件: {input_vcf}")
        
        output_file = f"{output_dir}/gwas_data.txt"
        
        # 手动构建命令字符串，确保不包含 --threads 选项
        cmd_str = f"{bcftools} query -f \"%CHROM\\t%POS\\t%REF\\t%ALT[\\t%GT]\\n\" {input_vcf} > {output_file}"
        
        # 返回字符串列表
        return [cmd_str] 