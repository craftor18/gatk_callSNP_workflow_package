import pandas as pd
import gffpandas.gffpandas as gffpd
import argparse

# 命令行参数解析
parser = argparse.ArgumentParser(description='将GWAS中的显著SNP与基因关联起来。')
parser.add_argument('-s', '--snp_file', required=True, help='包含显著SNP的文件路径。')
parser.add_argument('-g', '--gff_file', required=True, help='GFF格式的基因注释文件路径。')
parser.add_argument('-o', '--output_file', required=True, help='输出文件的路径。')
parser.add_argument('-w', '--window_size', type=int, default=50000, help='SNP周围区域的大小（默认：50000bp）。')
args = parser.parse_args()

# 载入显著SNP数据
sig_snps = pd.read_csv(args.snp_file)

# 载入GFF文件中的基因注释数据
annotation = gffpd.read_gff3(args.gff_file)
genes = annotation.df[annotation.df['type'] == 'gene'].copy()

# 从attributes列中解析Gene_ID和Gene_Symbol
genes['Gene_ID'] = genes['attributes'].str.extract(r'ID=([^;]+)')
genes['Gene_Symbol'] = genes['attributes'].str.extract(r'Symbol=([^;]+)')

# 查找与SNP相关的最近基因及其方向和符号
def find_closest_gene_info(snp_chrom, snp_pos):
    # 计算距离并寻找最近的基因
    genes['distance_to_snp'] = genes.apply(lambda row: abs(row['start'] - snp_pos) if row['start'] > snp_pos else abs(row['end'] - snp_pos), axis=1)
    closest_gene = genes[
        (genes['seq_id'] == snp_chrom) & (genes['distance_to_snp'] <= args.window_size)
    ].nsmallest(1, 'distance_to_snp')

    if closest_gene.empty:
        return pd.Series({'Gene_ID': 'No nearby gene', 'Direction': None, 'Gene_Symbol': None})

    # 确定方向
    direction = 'upstream' if closest_gene['start'].iloc[0] > snp_pos else 'downstream'
    return pd.Series({
        'Gene_ID': closest_gene['Gene_ID'].iloc[0],
        'Direction': direction,
        'Gene_Symbol': closest_gene['Gene_Symbol'].iloc[0]
    })

# 应用函数到每个显著SNP并创建新列
sig_snps[['Gene_ID', 'Direction', 'Gene_Symbol']] = sig_snps.apply(lambda row: find_closest_gene_info(row['CHROM'], row['POS']), axis=1)

# 将结果保存到新的CSV文件
sig_snps.to_csv(args.output_file, index=False)
