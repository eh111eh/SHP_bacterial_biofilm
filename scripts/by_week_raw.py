import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# 1. Configuration
weeks = ['week3', 'week4', 'week5', 'reading_week']
base_data_path = "data"
output_folder = "figures/1_by_week"

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

for week in weeks:
    # Find all CSV files in the specific week folder
    files = glob.glob(os.path.join(base_data_path, week, "*.csv"))
    
    if not files:
        print(f"Skipping {week}: No CSV files found.")
        continue
    
    print(f"Generating plot for {week}...")
    plt.figure(figsize=(10, 7))
    
    for file in files:
        filename = os.path.basename(file).replace('.csv', '')
        df = pd.read_csv(file)
        
        # Mapping: G'(index 2), G''(index 3), Strain(index 4)
        strain = df.iloc[:, 4]
        gp = df.iloc[:, 2]
        gpp = df.iloc[:, 3]

        # Formatting based on Isolate ID
        # If it's the control (3610), make it bold/distinct
        if '3610' in filename:
            line, = plt.plot(strain, gp, '-', linewidth=2.5, label=f"CONTROL: {filename} $G'$")
            plt.plot(strain, gpp, '--', color=line.get_color(), linewidth=1.5, alpha=0.8)
        else:
            line, = plt.plot(strain, gp, '-', alpha=0.5, label=f"{filename}")
            plt.plot(strain, gpp, '--', color=line.get_color(), alpha=0.3)

    # Log-Log scale for rheology standards
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'Strain ($\gamma$) [%]')
    plt.ylabel(r"Modulus $G', G''$ [Pa]")
    plt.title(f"Consistency Check: {week.upper()}")
    
    # Legend management (outside for clarity)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()

    # Save to the specific '1_by_week' folder
    save_path = os.path.join(output_folder, f"raw_comparison_{week}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()

print("\nTask 1 Complete: Individual week plots saved in 'figures/1_by_week/'.")