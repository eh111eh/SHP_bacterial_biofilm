import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import interp1d

def find_column(columns, keywords):
    for col in columns:
        if any(key.lower() in col.lower() for key in keywords):
            return col
    return None

def process_and_plot_normalised(data_root, output_dir):
    data_path = Path(data_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outliers = [
        "week6/2103_50C_1", "week6/2106_50C_1", "week8/2107_50C_1", 
        "week4/2106_30C_3", "week5/2107_30C_3", "reading_week/2109_30C_1"
    ]

    # 1. Data collection and mean calculation logic
    temp_summary = {} 
    file_groups = {}
    for csv_file in data_path.rglob("*.csv"):
        parts = csv_file.stem.split('_')
        if len(parts) < 2: continue
        file_groups.setdefault((parts[0], parts[1]), []).append(csv_file)

    common_strain = np.logspace(-0.8, 2, 100)

    for (sample_id, temp), files in file_groups.items():
        all_g1, all_g2 = [], []
        for file_path in files:
            identifier = f"{file_path.parent.name}/{file_path.stem}"
            if identifier in outliers: continue
            try:
                df = pd.read_csv(file_path)
                col_x = find_column(df.columns, ['Complex shear strain(%)'])
                col_g1 = find_column(df.columns, ['elastic component'])
                col_g2 = find_column(df.columns, ['viscous component'])
                col_freq = find_column(df.columns, ['Frequency'])

                if col_freq:
                    df = df[(df[col_freq] >= 0.9) & (df[col_freq] <= 1.1)]
                if df.empty: continue

                df = df.sort_values(by=col_x)
                # Apply interpolation
                f1 = interp1d(df[col_x], df[col_g1], bounds_error=False, fill_value="extrapolate")
                f2 = interp1d(df[col_x], df[col_g2], bounds_error=False, fill_value="extrapolate")
                all_g1.append(f1(common_strain))
                all_g2.append(f2(common_strain))
            except Exception as e:
                print(f"Error in {identifier}: {e}")

        if all_g1:
            if temp not in temp_summary: temp_summary[temp] = {}
            temp_summary[temp][sample_id] = (np.nanmean(all_g1, axis=0), np.nanmean(all_g2, axis=0))

    # 2. Normalized plotting logic
    for temp, samples in temp_summary.items():
        plt.figure(figsize=(10, 7))
        cmap = plt.get_cmap('tab10')

        for i, (sample_id, (g1, g2)) in enumerate(samples.items()):
            color = cmap(i % 10)
            
            # Extract G'0: Plateau modulus of the linear region
            g1_0 = np.nanmean(g1[:10]) 
            
            # Extract gamma_f: G' = G'' crossover point
            diff = np.abs(g1 - g2)
            cross_idx = np.nanargmin(diff)
            gamma_f = common_strain[cross_idx]

            # Data normalization
            g1_norm = g1 / g1_0
            g2_norm = g2 / g1_0
            strain_norm = common_strain / gamma_f

            # Plotting
            plt.plot(strain_norm, g1_norm, '-', linewidth=2, color=color, label=f"{sample_id} G' norm")
            plt.plot(strain_norm, g2_norm, '--', linewidth=1.5, color=color, alpha=0.6, label=f"{sample_id} G'' norm")

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(r'Normalised Strain ($\gamma / \gamma_f$)', fontsize=12) 
        plt.ylabel(r"Normalised Moduli ($G / G'_0$)", fontsize=12) 
        plt.title(f"Normalised Master Curve at {temp}", fontsize=14)
        
        # Add visual baselines for guidelines
        plt.axvline(1, color='gray', linestyle=':', alpha=0.5) # crossover point (x=1)
        plt.axhline(1, color='gray', linestyle=':', alpha=0.5) # plateau level (y=1)
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False, fontsize=9)
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.tight_layout()

        plt.savefig(output_path / f"normalised_{temp}.png", dpi=300, bbox_inches='tight')
        print(f"Saved normalized summary plot for {temp}")
        plt.close()

if __name__ == "__main__":
    process_and_plot_normalised("data", "figures/normalised")