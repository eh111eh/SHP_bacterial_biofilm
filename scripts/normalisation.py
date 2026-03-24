import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import interp1d

plt.rcParams.update({
    'mathtext.fontset': 'cm',
    'font.size': 28,
    'axes.titlesize': 32,
    'axes.labelsize': 28,
    'xtick.labelsize': 24,
    'ytick.labelsize': 24,
    'legend.fontsize': 20,
    'axes.unicode_minus': False,
    'axes.linewidth': 2
})
# ------------------------------------------------------

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

    temp_summary = {} 
    file_groups = {}

    for temp_folder in ['30C', '50C']:
        target_path = data_path / temp_folder
        if not target_path.exists(): continue
            
        for csv_file in target_path.rglob("*.csv"):
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
                f1 = interp1d(df[col_x], df[col_g1], bounds_error=False, fill_value="extrapolate")
                f2 = interp1d(df[col_x], df[col_g2], bounds_error=False, fill_value="extrapolate")
                all_g1.append(f1(common_strain))
                all_g2.append(f2(common_strain))
            except Exception as e:
                print(f"Error in {identifier}: {type(e).__name__} - {str(e)}")

        if all_g1:
            if temp not in temp_summary: temp_summary[temp] = {}
            temp_summary[temp][sample_id] = (np.nanmean(all_g1, axis=0), np.nanmean(all_g2, axis=0))

    # 2. Normalized plotting logic
    for temp, samples in temp_summary.items():
        plt.figure(figsize=(16, 10))
        cmap = plt.get_cmap('tab10')

        sorted_samples = sorted(samples.items())
        for i, (sample_id, (g1, g2)) in enumerate(sorted_samples):
            color = cmap(i % 10)
            
            # G'0: Plateau modulus
            g1_0 = np.nanmean(g1[:10]) 
            
            # gamma_f: G' = G'' crossover point
            diff = np.abs(np.log10(g1) - np.log10(g2))
            cross_idx = np.nanargmin(diff)
            gamma_f = common_strain[cross_idx]

            # Normalization
            g1_norm = g1 / g1_0
            g2_norm = g2 / g1_0
            strain_norm = common_strain / gamma_f

            # Plotting
            plt.plot(strain_norm, g1_norm, '-', linewidth=4, color=color, label=f"{sample_id} $G'$")
            plt.plot(strain_norm, g2_norm, '--', linewidth=3, color=color, alpha=0.6, label=f"{sample_id} $G''$")

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(r'Normalised Strain ($\gamma / \gamma_f$)', labelpad=15) 
        plt.ylabel(r"Normalised Moduli ($G / G'_0$)", labelpad=15) 
        # plt.title(f"Normalised Master Curve at {temp}", pad=20)
        
        plt.axvline(1, color='gray', linestyle=':', linewidth=2, alpha=0.5) 
        plt.axhline(1, color='gray', linestyle=':', linewidth=2, alpha=0.5) 
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
        plt.grid(True, which="both", ls="-", alpha=0.3, linewidth=1.5)
        plt.tight_layout()

        file_name = f"normalised_{temp}.png"
        plt.savefig(output_path / file_name, dpi=150, bbox_inches='tight')
        print(f"Saved: {file_name}")
        plt.close()

if __name__ == "__main__":
    process_and_plot_normalised("data", "figures/normalised")