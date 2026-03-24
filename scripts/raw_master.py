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
# --------------------------------------------------

def find_column(columns, keywords):
    for col in columns:
        if any(key.lower() in col.lower() for key in keywords):
            return col
    return None

def plot_temperature_summary(data_root, output_dir):
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
        if not target_path.exists():
            continue
            
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
            avg_g1 = np.nanmean(all_g1, axis=0)
            avg_g2 = np.nanmean(all_g2, axis=0)
            if temp not in temp_summary:
                temp_summary[temp] = {}
            temp_summary[temp][sample_id] = (avg_g1, avg_g2)

    for temp, samples in temp_summary.items():
        plt.figure(figsize=(16, 10)) 
        colors = plt.get_cmap('tab10')
        
        sorted_samples = sorted(samples.items())
        
        for i, (sample_id, (g1, g2)) in enumerate(sorted_samples):
            color = colors(i % 10)
            plt.plot(common_strain, g1, '-', linewidth=4, color=color, label=f"{sample_id} $G'$")
            plt.plot(common_strain, g2, '--', linewidth=3, color=color, alpha=0.6, label=f"{sample_id} $G''$")

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(r'Strain [$\%$]', labelpad=15)
        plt.ylabel(r"$G', G''$ [Pa]", labelpad=15)
        # plt.title(f"Comparison of All Samples at {temp}", pad=20)
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
        plt.grid(True, which="both", ls="-", alpha=0.3, linewidth=1.5)
        plt.tight_layout()

        file_name = f"summary_plot_{temp}.png"
        plt.savefig(output_path / file_name, dpi=150, bbox_inches='tight')
        print(f"Saved: {file_name}")
        plt.close()

if __name__ == "__main__":
    plot_temperature_summary("data", "figures/raw")