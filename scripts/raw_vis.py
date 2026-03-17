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

def plot_averaged_data(data_root, output_dir):
    data_path = Path(data_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outliers = [
        "week6/2103_50C_1", "week6/2106_50C_1", "week8/2107_50C_1", 
        "week4/2106_30C_3", "week5/2107_30C_3", "reading_week/2109_30C_1"
    ]

    groups = {}
    for csv_file in data_path.rglob("*.csv"):
        parts = csv_file.stem.split('_')
        if len(parts) < 2: continue
        groups.setdefault((parts[0], parts[1]), []).append(csv_file)

    for (sample_id, temp), files in groups.items():
        plt.figure(figsize=(8, 6))
        
        # Generate 100 uniform points from 10^{-1} to 10^2 (Common Strain Axis)
        common_strain = np.logspace(-0.8, 2, 100)
        all_g1 = []
        all_g2 = []

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
                
                # Apply interpolation: Transform individual sample data to the common strain axis
                f1 = interp1d(df[col_x], df[col_g1], bounds_error=False, fill_value="extrapolate")
                f2 = interp1d(df[col_x], df[col_g2], bounds_error=False, fill_value="extrapolate")
                
                all_g1.append(f1(common_strain))
                all_g2.append(f2(common_strain))
                
            except Exception as e:
                print(f"Error in {identifier}: {e}")

        if all_g1:
            # Calculate the average of multiple samples (excluding NaN values)
            avg_g1 = np.nanmean(all_g1, axis=0)
            avg_g2 = np.nanmean(all_g2, axis=0)

            # Plotting
            plt.plot(common_strain, avg_g1, '-', linewidth=2.5, color='tab:blue', label="Avg G'")
            plt.plot(common_strain, avg_g2, '--', linewidth=2.5, color='tab:orange', label="Avg G''")

            plt.xscale('log')
            plt.yscale('log')
            plt.xlabel('Strain [%]')
            plt.ylabel("G', G'' [Pa]")
            plt.title(f"Averaged Result: {sample_id} at {temp}")
            plt.legend(frameon=False)
            plt.grid(True, which="both", ls="-", alpha=0.2)
            plt.tight_layout()

            plt.savefig(output_path / f"{sample_id}_{temp}.png", dpi=300)
            print(f"Saved: {sample_id}_{temp}")
        
        plt.close()

if __name__ == "__main__":
    plot_averaged_data("data", "figures/raw")