import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def plot_rheology_parameters(csv_path, output_dir):
    # 1. Load data and set paths
    df = pd.read_csv(csv_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set graph styles
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.dpi'] = 300
    
    # List of parameters to visualize (Mean, Standard Deviation pairs)
    # Reset WSO to log scale (True)
    params = [
        ('G0_prime_mean', 'G0_prime_std', "Plateau Storage Modulus $G'_0$ [Pa]", "stiffness_G0.png", True),
        ('tan_delta0_mean', 'tan_delta0_std', r"Loss Tangent $\tan \delta_0$", "viscoelasticity_tan_delta.png", False),
        ('gamma_f_mean', 'gamma_f_std', r"Crossover Strain $\gamma_f$ [%]", "toughness_gamma_f.png", False),
        ('gamma_y_mean', 'gamma_y_std', r"Yield Strain $\gamma_y$ [%]", "brittleness_gamma_y.png", False),
        ('WSO_mean', 'WSO_std', "Weak Strain Overshoot (WSO) [Pa]", "overshoot_WSO.png", True)
    ]
    
    for mean_col, std_col, ylabel, filename, use_log in params:
        # --- Apply Strict Crossover Logic & Data Filtering ---
        if mean_col == 'gamma_f_mean':
            plot_df = df[(df[mean_col] > 0) & (df[mean_col] <= 100)].copy()
        else:
            plot_df = df[df[mean_col] > 0].copy() 
        
        plt.figure(figsize=(12, 6))
        
        ax = sns.barplot(
            data=plot_df, 
            x='Isolate', 
            y=mean_col, 
            hue='Temperature',
            palette={'30C': '#1f77b4', '50C': '#ff7f0e'},
            capsize=.1,
            edgecolor=".2"
        )
        
        # Manually add error bars
        x_coords = []
        for patch in ax.patches:
            if patch.get_height() > 0:
                x_coords.append(patch.get_x() + patch.get_width() / 2)
        
        df_sorted = plot_df.sort_values(['Temperature', 'Isolate'])
        means = df_sorted[mean_col].values
        stds = df_sorted[std_col].fillna(0).values
        
        if len(x_coords) == len(means):
            plt.errorbar(
                x=x_coords, 
                y=means, 
                yerr=stds, 
                fmt='none', 
                c='black', 
                capsize=5
            )

        if use_log:
            plt.yscale('log')
            ylabel += " (Log Scale)"
            
            # --- Add threshold line to WSO graph only ---
            if mean_col == 'WSO_mean':
                # Draw a red dashed line at y = 1 (10^0) to indicate the significant WSO boundary
                plt.axhline(y=1, color='red', linestyle='--', linewidth=1.5, label='Threshold (1 Pa)')
                #plt.text(-0.5, 1.2, 'Significant WSO', color='red', fontweight='bold')
                #plt.text(-0.5, 0.7, 'Noise / No WSO', color='gray', fontstyle='italic')

        plt.title(f"Comparison of {ylabel.split('[')[0].strip()}", fontsize=15, pad=15)
        plt.ylabel(ylabel, fontsize=12)
        plt.xlabel("Isolate ID", fontsize=12)
        plt.legend(title="Temperature", frameon=True)
        
        plt.tight_layout()
        plt.savefig(output_path / filename)
        print(f"✅ Saved: {filename}")
        plt.close()

if __name__ == "__main__":
    plot_rheology_parameters("results/all_params_avg.csv", "figures/parameters")