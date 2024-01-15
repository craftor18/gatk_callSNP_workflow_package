import pandas as pd
import gffpandas.gffpandas as gffpd
import argparse

# 命令行参数解析
parser = argparse.ArgumentParser(description='将GWAS中的显著SNP与基因关联起来。')
parser.add_argument('-s','--snp_file', required=True, help='包含显著SNP的文件路径。')
parser.add_argument('-g','--gff_file', required=True, help='GFF格式的基因注释文件路径。')
parser.add_argument('-o','--output_file', required=True, help='输出文件的路径。')
parser.add_argument('-w', '--window_size', type=int, default=50000, help='SNP周围区域的大小（默认：50000bp）。')
args = parser.parse_args()

# 载入显著SNP数据
sig_snps = pd.read_csv(args.snp_file)

# 载入GFF文件中的基因注释数据
annotation = gffpd.read_gff3(args.gff_file)
genes = annotation.df[annotation.df['type'] == 'gene'].copy()

# 从attributes列中解析Gene_ID

genes['Gene_ID'] = genes['attributes'].str.extract(r'ID=([^;]+)')
# print(genes)
# 查找与SNP相关的基因
def find_related_genes(snp_chrom, snp_pos):
    nearby_genes = genes[
        (genes['seq_id'] == snp_chrom) &
        (genes['start'] <= snp_pos + args.window_size) &
        (genes['end'] >= snp_pos - args.window_size)
    ]
    containing_genes = genes[
        (genes['seq_id'] == snp_chrom) &
        (genes['start'] <= snp_pos) &
        (genes['end'] >= snp_pos)
    ]
    all_related_genes = pd.concat([nearby_genes, containing_genes]).drop_duplicates()
    #print(','.join(all_related_genes['Gene_ID']))
    return ','.join(all_related_genes['Gene_ID'][:2])

# 应用函数到每个显著SNP
sig_snps['related_genes'] = sig_snps.apply(lambda row: find_related_genes(row['CHROM'], row['POS']), axis=1)
# print(sig_snps)
# 将结果保存到新的CSV文件
sig_snps.to_csv(args.output_file, index=False)
