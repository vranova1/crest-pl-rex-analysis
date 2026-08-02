import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Change to your project root directory
BASE_PATH = "/path/to/crest-pl-rex-analysis"
TABLES_DIR = os.path.join(BASE_PATH, "tables")
# Choose which master table to use
master_table_file = os.path.join(TABLES_DIR, 'master_energy_table.csv')

def correlate_new_score(df_merged):
    
    # 5. SERIES-BY-SERIES ANALYSIS
    results = []

    # Grouping by 'Target' (e.g., 001-CA2, 002-HIV-PR)
    for target, group in df_merged.groupby('Target'):
        # We need at least 3 points for a meaningful correlation
        if len(group) < 3:
            print(f"Skipping {target}: Not enough ligands ({len(group)})")
            continue
        
        # Calculate Correlation for Original vs New
        r_orig = group['dG_experiment'].corr(group['Score'])
        r_new  = group['dG_experiment'].corr(group['Score_new'])
        
        results.append({
            'Target': target,
            'Count': len(group),
            'R_Original': r_orig,
            'R_New': r_new,
            'R2_Original': r_orig**2 if not pd.isna(r_orig) else 0,
            'R2_New': r_new**2 if not pd.isna(r_new) else 0,
            'Improvement': (r_new**2 - r_orig**2) if (not pd.isna(r_orig) and not pd.isna(r_new)) else 0
        })

    # 6. DISPLAY AND SAVE SUMMARY
    df_results = pd.DataFrame(results)
    print("\n--- Correlation Results per Series ---")
    print(df_results[['Target', 'Count', 'R2_Original', 'R2_New', 'Improvement']].to_string(index=False))

    # Calculate global average improvement
    avg_imp = df_results['Improvement'].mean()
    print(f"\nAverage R2 Improvement across all series: {avg_imp:.4f}")
    return df_results

def drop_and_log_incomplete_rows(df_merged, required_columns):
    total_before = len(df_merged)
    # Drop rows where any of these columns are NaN
    df_merged_dropped = df_merged.dropna(subset=required_columns)
    total_after = len(df_merged_dropped)
    print(f"Filtered out {total_before - total_after} ligands due to missing data.")
    print(f"Proceeding with {total_after} ligands for correlation.")
    return df_merged_dropped

def score_from_columns(df, columns):
    df = df.copy()
    df['Score_new'] = 0.0

    for column in columns:
        if column.startswith("Delta"):
            df['Score_new'] -= df[column]
        else:
            df['Score_new'] += df[column]

    return df

# 1. READ ORIGINAL DATA
# This handles the text file format you shared
df_orig = pd.read_csv(f'{TABLES_DIR}/SQM2.20_score_components.txt', sep=r'\s+', comment='#')

# 2. LOAD YOUR DATA FROM MASTER TABLE
df_new = pd.read_csv(master_table_file)
df_new['Target'] = df_new['Target'].replace('006-BACE1', '006-BACE1-D3R')

# 3. MERGE
# This matches the 'Ligand' column in both files
df_merged = pd.merge(df_orig, df_new, on=['Target', 'Ligand'])

# 4. SUBSTITUTE AND COMPUTE NEW SCORE
# We take the original dG_conf and add your new components
print("\n--- -TS term from CREST gfn2 ---")
required_columns = ['dG_int', 'dG_conf(L)', 'dG_H+', 'Minus_TS_gfn2_kcal']

df_merged_dropped = drop_and_log_incomplete_rows(df_merged, required_columns)
df_final = score_from_columns(df_merged_dropped, required_columns)
df_results = correlate_new_score(df_final)


print("\n--- dG_conf(L) corrected by xTB derived correction ---")
required_columns = ['dG_int', 'dG_conf(L)', 'dG_H+', '-TS', 'Delta_gfn2_xtb_kcal']

df_merged_dropped = drop_and_log_incomplete_rows(df_merged, required_columns)
df_final = score_from_columns(df_merged_dropped, required_columns)
df_results = correlate_new_score(df_final)


print("\n--- dG_conf(L) corrected by PM6 derived correction ---")
required_columns = ['dG_int', 'dG_conf(L)', 'dG_H+', '-TS', 'Delta_pm6_on_gfn2']

df_merged_dropped = drop_and_log_incomplete_rows(df_merged, required_columns)
df_final = score_from_columns(df_merged_dropped, required_columns)
df_results = correlate_new_score(df_final)


print("\n--- Number of rotatable bonds vs gfn2 S_conf correlation ---")
required_columns = ['GFN2_S_conf', 'TS_nrb' ]#, 'dG_conf(L)'#, 'Delta_gfn2_xtb_kcal', 'Minus_TS_gfn2_kcal']
df_merged_dropped = drop_and_log_incomplete_rows(df_merged, required_columns)

total_corr = df_merged_dropped['GFN2_S_conf'].corr(df_merged_dropped['TS_nrb'])

print(f"Total Pearson Correlation: {total_corr:.3f}")

# 2. Calculate Correlation Per Series
# Replace 'series' with your actual grouping column name (e.g., 'target' or 'series_id')
series_correlations = df_merged_dropped.groupby('Target').apply(
    lambda x: x['GFN2_S_conf'].corr(x['TS_nrb']), include_groups=False
).reset_index()

# Rename the column for clarity
series_correlations.columns = ['Series', 'Pearson_r']

# 3. Sort by correlation to see where the models disagree the most
series_correlations = series_correlations.sort_values(by='Pearson_r', ascending=False)

print("\n--- Correlation Per Series ---")
print(series_correlations)

print("\n--- -TS from LM5 vs gfn2 S_conf correlation ---")
required_columns = ['Minus_TS_gfn2_kcal', '-TS' ]#, 'dG_conf(L)'#, 'Delta_gfn2_xtb_kcal', 'Minus_TS_gfn2_kcal']
df_merged_dropped = drop_and_log_incomplete_rows(df_merged, required_columns)

total_corr = df_merged_dropped['Minus_TS_gfn2_kcal'].corr(df_merged_dropped['TS_nrb'])

print(f"Total Pearson Correlation: {total_corr:.3f}")

# 2. Calculate Correlation Per Series
# Replace 'series' with your actual grouping column name (e.g., 'target' or 'series_id')
series_correlations = df_merged_dropped.groupby('Target').apply(
    lambda x: x['GFN2_S_conf'].corr(x['-TS']), include_groups=False
).reset_index()

# Rename the column for clarity
series_correlations.columns = ['Series', 'Pearson_r']

# 3. Sort by correlation to see where the models disagree the most
series_correlations = series_correlations.sort_values(by='Pearson_r', ascending=False)

print("\n--- Correlation Per Series ---")
print(series_correlations)


print("\n--- 001 dG_conf(L) replaced by energy from crest on protonated structures + xtb energy on 020 structures ---")
required_columns = ['dG_int', 'dG_conf(L)', '-TS', 'dG_H+', 'Delta_gfn2_xtb_protonated']

df_merged_dropped = drop_and_log_incomplete_rows(df_merged, required_columns)
df_final = score_from_columns(df_merged_dropped, required_columns)
df_results = correlate_new_score(df_final)

# Save detailed results
df_merged.to_csv('final_comparison_results.csv', index=False)
df_results.to_csv(os.path.join(TABLES_DIR,'series_correlation_summary.csv'), index=False)