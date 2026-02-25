import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

# 1. Configuration: Selected Best Files
best_files = {
    '3610': ('week3', '3610_30C_2.csv'),
    '2103': ('week4', '2103_30C_2.csv'),
    '2106': ('week4', '2106_30C_1.csv'),
    '2107': ('week5', '2107_30C_2.csv'),
    '2108': ('week5', '2108_30C_3.csv'),
    '2109': ('reading_week', '2109_30C_3.csv'),
    '2125': ('reading_week', '2125_30C_1.csv')
}

base_data_path = "data"
output_folder = "figures/3_master_plots"
os.makedirs(output_folder, exist_ok=True)

plt.figure(figsize=(12, 8))

for isolate, (week, filename) in best_files.items():
    file_path = os.path.join(base_data_path, week, filename)
    
    try:
        # Load raw data
        df = pd.read_csv(file_path)
        
        # --- A. Filtering: Skip the first 1/3 ---
        skip_idx = len(df) // 3
        df_clean = df.iloc[skip_idx:].reset_index(drop=True)
        
        strain = df_clean.iloc[:, 4].values
        gp = df_clean.iloc[:, 2].values
        gpp = df_clean.iloc[:, 3].values
        
        # --- B. Parameter Extraction from Cleaned Data ---
        # 1. G'0: Mean of the first 5 points in the cleaned linear regime
        gp0 = np.mean(gp[0:5])
        
        # 2. gamma_f: Strain where G' = G''
        gamma_f = None
        diff = gp - gpp
        for i in range(len(diff) - 1):
            if diff[i] > 0 and diff[i+1] < 0:
                # Interpolation for pinpoint accuracy
                itp = interp1d([diff[i], diff[i+1]], [strain[i], strain[i+1]])
                gamma_f = float(itp(0))
                break
        
        # --- C. Plotting Normalized Curves ---
        if gamma_f and gp0 > 0:
            s_norm = strain / gamma_f
            gp_norm = gp / gp0
            gpp_norm = gpp / gp0
            
            # Styling: 3610 as bold black baseline
            color = 'black' if isolate == '3610' else None
            linewidth = 3.0 if isolate == '3610' else 1.5
            zorder = 10 if isolate == '3610' else 1
            
            # Solid for G', Dashed for G''
            line, = plt.plot(s_norm, gp_norm, '-', linewidth=linewidth, 
                             color=color, zorder=zorder, label=f"{isolate}")
            plt.plot(s_norm, gpp_norm, '--', linewidth=linewidth-0.5, 
                     color=line.get_color(), alpha=0.4, zorder=zorder)
            
    except Exception as e:
        print(f"Error processing {filename}: {e}")

# 3. Final Formatting & Protocol Compliance
plt.xscale('log')
plt.yscale('log')

# Crossover point markers
plt.axvline(x=1, color='gray', linestyle=':', alpha=0.6)
plt.axhline(y=1, color='gray', linestyle=':', alpha=0.6)

plt.xlabel(r'Normalized Strain ($\gamma / \gamma_f$)', fontsize=12)
plt.ylabel(r'Normalized Moduli ($G / G_0$)', fontsize=12)
plt.title("Master Plot (Normalisation & Initial 1/3 Skipped)", fontsize=14)

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.tight_layout()

# Save the plot
save_path = os.path.join(output_folder, "final_master_normalised_cleaned.png")
plt.savefig(save_path, dpi=300)
plt.show()

print(f"Cleaned Master Normalized Plot saved to: {save_path}")