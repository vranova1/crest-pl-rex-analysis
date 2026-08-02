import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Change path to your project root
BASE_PATH = "/path/to/crest-pl-rex-analysis"
TABLES_DIR = os.path.join(BASE_PATH, "tables")
master_table_file = os.path.join(TABLES_DIR, 'master_energy_table.csv')
output_filename = os.path.join(TABLES_DIR, "pm6_on_gfn2_correction_distribution_boxplot_w_global.png")
df = pd.read_csv(master_table_file, sep=',', comment='#')

# 2. Set the aesthetic style of the plots
sns.set_theme(style="whitegrid")

# 3. Choose your columns
# 'x_col' is usually your categorical variable (e.g., Target or Ligand)
# 'y_col' is the numerical energy/number value you want to visualize
x_col = 'Target' 
y_col = 'Delta_pm6_on_gfn2'  # Change this to one of your numerical columns

# 3. Create a figure with two subplots (1 row, 2 columns)
# width_ratios makes the target-specific plot wider since it has more items
fig, axes = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [3, 1]})

# --- Plot 1: Per Target Distribution ---
# sns.violinplot(ax=axes[0], data=df, x=x_col, y=y_col, palette="muted", inner="quartile")
sns.boxplot(ax=axes[0], data=df, x=x_col, y=y_col, palette="muted")
axes[0].set_title(f'Distribution by {x_col}', fontsize=20)
axes[0].tick_params(axis='x', rotation=45, labelsize=18)
axes[0].tick_params(axis='y', labelsize=18)
axes[0].set_ylabel(r'$\Delta G_{\mathrm{corr}}^{\mathrm{PM6}}$ (kcal/mol)', fontsize=22)
axes[0].set_xlabel(r'Target', fontsize=20)
# --- Plot 2: Global Distribution ---
# sns.violinplot(ax=axes[1], data=df, y=y_col, color="lightgray", inner="quartile")
sns.boxplot(ax=axes[1], data=df, y=y_col, color="lightgray")

axes[1].set_title('Global Distribution', fontsize=20)
axes[1].set_ylabel('') # Remove y-label for the second plot to save space
axes[1].tick_params(axis='y', labelsize=18)

# 4. Final touches
plt.tight_layout()

# 5. Save
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Success! Combined plot saved as {output_filename}")