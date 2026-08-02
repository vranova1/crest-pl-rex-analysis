import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import pearsonr

# 1. Setup paths, change to yours
BASE_PATH = "/path/to/crest-pl-rex-analysis"
TABLES_DIR = os.path.join(BASE_PATH, "tables")
output_filename = os.path.join(TABLES_DIR, "lm5_vs_gfn2_by_series.png")
master_table_file = os.path.join(TABLES_DIR, 'master_energy_table.csv')

df_new = pd.read_csv(master_table_file)
df_new['Target'] = df_new['Target'].replace('006-BACE1', '006-BACE1-D3R')
df_orig = pd.read_csv(f'{TABLES_DIR}/SQM2.20_score_components.txt', sep=r'\s+', comment='#')
df_orig = df_orig.rename(columns={'-TS': 'SQM_TS'})
df_merged = pd.merge(df_orig, df_new, on=['Target', 'Ligand'])

# Here you can change the master table columns you want to correlate
cre_sconf = 'Minus_TS_gfn2_kcal'  
sqm_sconf = 'SQM_TS'    

df_merged[sqm_sconf] = pd.to_numeric(df_merged[sqm_sconf], errors='coerce')
df_merged[cre_sconf] = pd.to_numeric(df_merged[cre_sconf], errors='coerce')
df_clean = df_merged.dropna(subset=[cre_sconf, sqm_sconf])

df_clean = df_clean[np.abs(df_clean[sqm_sconf] - df_clean[sqm_sconf].mean()) <= (3 * df_clean[sqm_sconf].std())]

sns.set_theme(style="whitegrid", rc={"axes.facecolor": "#f9f9f9"})

g = sns.lmplot(
    data=df_clean, 
    x=cre_sconf, 
    y=sqm_sconf, 
    sharex=False, 
    sharey=False,
    col="Target", 
    col_wrap=3, 
    height=4.5, 
    aspect=1.1,
    scatter_kws={'alpha':0.5, 's': 40, 'edgecolor': 'white'},
    line_kws={'color': 'firebrick', 'lw': 2}
)

for ax in g.axes.flat:
    ax.tick_params(labelbottom=True, labelleft=True) # Forces X and Y numbers to show on all plots
    ax.set_xlabel("CREST $-TS_{conf}$ [kcal/mol]", fontsize=15)
    ax.set_ylabel("LM5 $-TS$ [kcal/mol]", fontsize=15)

for ax, title in zip(g.axes.flat, g.col_names):
    subset = df_clean[df_clean['Target'] == title]
    if len(subset) > 1:
        r_val, _ = pearsonr(subset[cre_sconf], subset[sqm_sconf])
        ax.set_title(f"{title}\n($r = {r_val:.2f}$)", fontsize=13, fontweight='bold', pad=15)

plt.subplots_adjust(top=0.9, hspace=0.6, wspace=0.4) 

plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Graph fixed and saved to {output_filename}")