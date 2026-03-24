import pandas as pd
import numpy as np
from scipy import stats
import os

# --- 1. Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results", "all_params.csv"))
OUTPUT_REPORT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results", "statistical_report.txt"))

# Create results folder if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)

# --- 2. Load Data ---
if not os.path.exists(RESULTS_PATH):
    print(f"Error: {RESULTS_PATH} not found. Ensure raw data is processed first.")
    exit()

df = pd.read_csv(RESULTS_PATH)
# Log-transforming G0_prime and WSO is physically more sound due to order-of-magnitude differences
metrics = ['G0_prime', 'tan_delta0', 'gamma_y', 'WSO']
isolates = df['Isolate'].unique()

with open(OUTPUT_REPORT, "w") as f:
    f.write("============================================================\n")
    f.write("STATISTICAL ANALYSIS REPORT: BIOFILM THERMAL STABILITY\n")
    f.write("Note: Welch's T-test used for unequal variances.\n")
    f.write("Note: Log10 transformation applied to G0_prime and WSO for analysis.\n")
    f.write("============================================================\n\n")

    # --- PART A: Internal Thermal Sensitivity (30C vs 50C per Isolate) ---
    f.write("PART A: Internal Thermal Sensitivity (30C vs 50C per Isolate)\n")
    f.write("-" * 75 + "\n")
    f.write(f"{'Isolate':<10} | {'Metric':<12} | {'T-Stat':<10} | {'P-Value':<10} | {'Sig.'}\n")
    f.write("-" * 75 + "\n")

    for isolate in isolates:
        iso_df = df[df['Isolate'] == isolate]
        for metric in metrics:
            group30 = iso_df[iso_df['Temperature'] == '30C'][metric].dropna()
            group50 = iso_df[iso_df['Temperature'] == '50C'][metric].dropna()
            
            if len(group30) >= 2 and len(group50) >= 2:
                # Apply log transformation for G0 and WSO to handle exponential scale
                if metric in ['G0_prime', 'WSO']:
                    t_stat, p_val = stats.ttest_ind(np.log10(group30), np.log10(group50), equal_var=False)
                else:
                    t_stat, p_val = stats.ttest_ind(group30, group50, equal_var=False)
                
                sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
                f.write(f"{str(isolate):<10} | {metric:<12} | {t_stat:>10.4f} | {p_val:>10.4e} | {sig}\n")
        f.write("-" * 75 + "\n")

    f.write("\n\n")

    # --- PART B: Comparative Analysis at 50C (Isolates vs 3610) ---
    f.write("PART B: Comparative Analysis at 50C (Reference: 3610)\n")
    f.write("-" * 85 + "\n")
    f.write("Bonferroni Correction applied. Sig. if Adj. P-Value < 0.05\n")
    f.write(f"{'Comparison':<20} | {'Metric':<12} | {'Diff (%)':<10} | {'Adj. P-Val':<12} | {'Status'}\n")
    f.write("-" * 85 + "\n")

    df_50 = df[df['Temperature'] == '50C']
    control_id = 3610 
    
    if control_id in df_50['Isolate'].values:
        control_data = df_50[df_50['Isolate'] == control_id]
        other_isolates = [i for i in isolates if i != control_id]
        num_comparisons = len(other_isolates)

        for metric in metrics:
            ctrl_vals = control_data[metric].dropna()
            
            for target in other_isolates:
                target_vals = df_50[df_50['Isolate'] == target][metric].dropna()
                
                if len(target_vals) >= 2 and len(ctrl_vals) >= 2:
                    # T-test with Welch's correction
                    if metric in ['G0_prime', 'WSO']:
                        _, p_val = stats.ttest_ind(np.log10(target_vals), np.log10(ctrl_vals), equal_var=False)
                    else:
                        _, p_val = stats.ttest_ind(target_vals, ctrl_vals, equal_var=False)
                    
                    # Bonferroni-Adjusted P-Value (Capped at 1.0)
                    p_adj = min(p_val * num_comparisons, 1.0)
                    
                    diff_pct = ((target_vals.mean() - ctrl_vals.mean()) / ctrl_vals.mean()) * 100
                    
                    # Define Status based on adjusted p-value
                    if p_adj < 0.05:
                        status = "SUPERIOR" if diff_pct > 0 else "INFERIOR"
                    else:
                        status = "SIMILAR"
                    
                    f.write(f"{str(target) + ' vs 3610':<20} | {metric:<12} | {diff_pct:>9.1f}% | {p_adj:>10.4e} | {status}\n")
            f.write("-" * 85 + "\n")

print(f"Refined statistical report generated at: {OUTPUT_REPORT}")