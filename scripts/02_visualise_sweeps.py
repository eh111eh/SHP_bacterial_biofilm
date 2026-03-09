import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# --- 1. Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))
RESULTS_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results", "all_params.csv"))
OUTPUT_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "figures", "2_normalized"))

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load the parameter table to get G0 and gamma_f for normalization
df_params = pd.read_csv(RESULTS_PATH)

# Helper to find the specific CSV file path based on filename in CSV
def find_file_path(filename):
    search_pattern = os.path.join(BASE_DATA_PATH, "**", filename)
    files = glob.glob(search_pattern, recursive=True)
    return files[0] if files else None

# Get unique isolates
isolates = df_params['Isolate'].unique()

# --- 2. Plotting per Isolate (Raw & Normalized) ---
for isolate in isolates:
    plt.figure(figsize=(12, 5))
    
    # Left Plot: Raw Data (Thermal Comparison)
    ax1 = plt.subplot(1, 2, 1)
    
    # Right Plot: Normalized (Structural Collapse)
    ax2 = plt.subplot(1, 2, 2)
    
    isolate_data = df_params[df_params['Isolate'] == isolate]
    
    # Colors for Temperatures
    colors = {'30C': 'blue', '50C': 'red'}
    
    for temp in ['30C', '50C']:
        temp_set = isolate_data[isolate_data['Temperature'] == temp]
        if temp_set.empty: continue
        
        # Plot each replicate
        for _, row in temp_set.iterrows():
            fpath = find_file_path(row['Filename'])
            if not fpath: continue
            
            # Load raw data (Skip 1/3 as per extraction logic)
            raw_df = pd.read_csv(fpath)
            raw_df = raw_df.iloc[len(raw_df)//3:].reset_index(drop=True)
            
            strain = raw_df.iloc[:, 4].values
            gp = raw_df.iloc[:, 2].values
            gpp = raw_df.iloc[:, 3].values
            
            # Retrieve normalization factors from table
            g0 = row['G0_prime']
            gf = row['gamma_f']
            
            # --- Subplot 1: Raw Scaling ---
            ax1.loglog(strain, gp, '-', color=colors[temp], alpha=0.6, label=f"{temp} G'" if _ == temp_set.index[0] else "")
            ax1.loglog(strain, gpp, '--', color=colors[temp], alpha=0.4, label=f"{temp} G''" if _ == temp_set.index[0] else "")
            
            # --- Subplot 2: Normalized Collapse ---
            # X-axis: strain / crossover strain | Y-axis: Modulus / Plateau Modulus
            if not np.isnan(gf):
                ax2.loglog(strain/gf, gp/g0, '-', color=colors[temp], alpha=0.5)
                ax2.loglog(strain/gf, gpp/g0, '--', color=colors[temp], alpha=0.3)

    # Formatting Raw Plot
    ax1.set_title(f"Isolate {isolate}: Raw Thermal Shift")
    ax1.set_xlabel("Strain [%]")
    ax1.set_ylabel("Modulus [Pa]")
    ax1.legend(fontsize='small')
    ax1.grid(True, which="both", alpha=0.2)

    # Formatting Normalized Plot
    ax2.set_title(f"Isolate {isolate}: Structural Collapse")
    ax2.set_xlabel(r"Normalized Strain ($\gamma / \gamma_f$)")
    ax2.set_ylabel(r"Normalized Modulus ($G / G'_0$)")
    ax2.axvline(1, color='black', linestyle=':', alpha=0.5) # Crossover point should be at 1
    ax2.axhline(1, color='black', linestyle=':', alpha=0.5) # Plateau should start at 1
    ax2.grid(True, which="both", alpha=0.2)

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_FOLDER, f"collapse_{isolate}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Generated comparison plot for Isolate {isolate}")

# --- 3. Master Global Collapse (All Isolates Together) ---
plt.figure(figsize=(8, 6))
for _, row in df_params.iterrows():
    if np.isnan(row['gamma_f']): continue
    
    fpath = find_file_path(row['Filename'])
    if not fpath: continue
    
    raw_df = pd.read_csv(fpath).iloc[20:].reset_index(drop=True) # General skip for master plot
    strain, gp, g0, gf = raw_df.iloc[:, 4].values, raw_df.iloc[:, 2].values, row['G0_prime'], row['gamma_f']
    
    color = 'blue' if row['Temperature'] == '30C' else 'red'
    plt.loglog(strain/gf, gp/g0, color=color, alpha=0.15)

plt.title("Global Master Curve Collapse (All Samples)")
plt.xlabel(r"$\gamma / \gamma_f$")
plt.ylabel(r"$G' / G'_0$")
plt.axvline(1, color='k', alpha=0.3)
plt.grid(True, which="both", alpha=0.2)
plt.savefig(os.path.join(OUTPUT_FOLDER, "master_collapse_all.png"), dpi=300)
print("\nGlobal master collapse plot saved.")