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
    print(f"Error: {RESULTS_PATH} not found. Run script 01 first.")
    exit()

df = pd.read_csv(RESULTS_PATH)
metrics = ['G0_prime', 'tan_delta0', 'gamma_y', 'WSO']
isolates = df['Isolate'].unique()

with open(OUTPUT_REPORT, "w") as f:
    f.write("============================================================\n")
    f.write("STATISTICAL ANALYSIS REPORT: BIOFILM THERMAL STABILITY\n")
    f.write("============================================================\n\n")

    # --- PART A: T-Test (Internal Thermal Sensitivity) ---
    # Question: Does heat significantly change the properties of THIS isolate?
    f.write("PART A: Internal Thermal Sensitivity (30C vs 50C per Isolate)\n")
    f.write("-" * 60 + "\n")
    f.write(f"{'Isolate':<10} | {'Metric':<12} | {'T-Stat':<10} | {'P-Value':<10} | {'Significance'}\n")
    f.write("-" * 60 + "\n")

    for isolate in isolates:
        iso_df = df[df['Isolate'] == isolate]
        for metric in metrics:
            group30 = iso_df[iso_df['Temperature'] == '30C'][metric].dropna()
            group50 = iso_df[iso_df['Temperature'] == '50C'][metric].dropna()
            
            if len(group30) >= 2 and len(group50) >= 2:
                t_stat, p_val = stats.ttest_ind(group30, group50, equal_var=False)
                sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
                f.write(f"{str(isolate):<10} | {metric:<12} | {t_stat:>10.4f} | {p_val:>10.4e} | {sig}\n")
        f.write("-" * 60 + "\n")

    f.write("\n\n")

    # --- PART B: Comparative Analysis at 50C (Isolates vs 3610) ---
    # Question: Which soil isolates are significantly tougher than the control at high temp?
    f.write("PART B: Comparative Analysis at 50C (Control: 3610 vs Others)\n")
    f.write("-" * 60 + "\n")
    f.write("Note: Comparing soil isolates against 3610 at 50 degrees Celsius.\n")
    f.write(f"{'Comparison':<20} | {'Metric':<12} | {'Diff (%)':<10} | {'P-Value':<10} | {'Status'}\n")
    f.write("-" * 60 + "\n")

    df_50 = df[df['Temperature'] == '50C']
    control_id = 3610 # Standard reference
    
    # Check if control exists in 50C data
    if control_id in df_50['Isolate'].values:
        control_data = df_50[df_50['Isolate'] == control_id]
        other_isolates = [i for i in isolates if i != control_id]

        for metric in metrics:
            ctrl_vals = control_data[metric].dropna()
            ctrl_mean = ctrl_vals.mean()

            for target in other_isolates:
                target_vals = df_50[df_50['Isolate'] == target][metric].dropna()
                
                if len(target_vals) >= 2 and len(ctrl_vals) >= 2:
                    t_stat, p_val = stats.ttest_ind(target_vals, ctrl_vals, equal_var=False)
                    # Bonferroni correction (simple manual version)
                    # Significant if p < 0.05 / number of comparisons
                    p_adj = p_val * len(other_isolates) 
                    
                    diff_pct = ((target_vals.mean() - ctrl_mean) / ctrl_mean) * 100
                    sig_label = "SUPERIOR" if (p_adj < 0.05 and diff_pct > 0) else "INFERIOR" if (p_adj < 0.05 and diff_pct < 0) else "SIMILAR"
                    
                    f.write(f"{str(target) + ' vs 3610':<20} | {metric:<12} | {diff_pct:>9.1f}% | {p_val:>10.4e} | {sig_label}\n")
            f.write("-" * 60 + "\n")

print(f"Statistical report generated at: {OUTPUT_REPORT}")