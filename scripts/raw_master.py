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

def plot_temperature_summary(data_root, output_dir):
    data_path = Path(data_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outliers = [
        "week6/2103_50C_1", "week6/2106_50C_1", "week8/2107_50C_1", 
        "week4/2106_30C_3", "week5/2107_30C_3", "reading_week/2109_30C_1"
    ]

    # 1. Group data into a (Temperature -> Sample_ID) structure
    temp_summary = {} # { '30C': { '2103': (avg_g1, avg_g2), ... }, '50C': { ... } }

    # group files as in the previous method (Sample_ID, Temp)
    file_groups = {}
    for csv_file in data_path.rglob("*.csv"):
        parts = csv_file.stem.split('_')
        if len(parts) < 2: continue
        file_groups.setdefault((parts[0], parts[1]), []).append(csv_file)

    common_strain = np.logspace(-0.8, 2, 100)

    # 2. Calculate the mean for each sample and store by temperature
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
                print(f"Error in {identifier}: {e}")

        if all_g1:
            avg_g1 = np.nanmean(all_g1, axis=0)
            avg_g2 = np.nanmean(all_g2, axis=0)
            
            if temp not in temp_summary:
                temp_summary[temp] = {}
            temp_summary[temp][sample_id] = (avg_g1, avg_g2)

    # 3. Generate consolidated plots for each temperature
    for temp, samples in temp_summary.items():
        plt.figure(figsize=(10, 7))
        
        # Use a colormap to assign unique colors to each sample
        colors = plt.get_cmap('tab10')
        
        for i, (sample_id, (g1, g2)) in enumerate(samples.items()):
            color = colors(i)
            # G': solid line, G'': dashed line (match colors per sample)
            plt.plot(common_strain, g1, '-', linewidth=2, color=color, label=f"{sample_id} G'")
            plt.plot(common_strain, g2, '--', linewidth=1.5, color=color, alpha=0.7, label=f"{sample_id} G''")

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Strain [%]', fontsize=12)
        plt.ylabel("G', G'' [Pa]", fontsize=12)
        plt.title(f"Comparison of All Samples at {temp}", fontsize=14)
        
        # Place the legend outside or in an appropriate position to avoid overcrowding.
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False, fontsize=9)
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.tight_layout()

        file_name = f"summary_plot_{temp}.png"
        plt.savefig(output_path / file_name, dpi=300, bbox_inches='tight')
        print(f"Saved summary plot for {temp}")
        plt.close()

if __name__ == "__main__":
    plot_temperature_summary("data", "figures/raw")