import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from collections import defaultdict

# 1. Configuration
weeks = ['week3', 'week4', 'week5', 'reading_week']
base_data_path = "data"
output_folder = "figures/2_by_strain"

# Create output directory
os.makedirs(output_folder, exist_ok=True)

# 2. Group all files by Isolate Identity
# Using a dictionary to group files: { '2103': [path1, path2, path3], ... }
strain_groups = defaultdict(list)

for week in weeks:
    # Find all CSV files in each week folder
    files = glob.glob(os.path.join(base_data_path, week, "*.csv"))
    for file_path in files:
        filename = os.path.basename(file_path)
        # Extract Isolate ID (Assumes format: IsolateID_Temperature_Replicate.csv)
        # Example: '2103' from '2103_30C_1.csv'
        strain_id = filename.split('_')[0]
        strain_groups[strain_id].append((file_path, filename, week))

# 3. Plotting Replicates for Each Isolate
for strain_id, file_list in strain_groups.items():
    print(f"Processing Isolate: {strain_id} (Found {len(file_list)} files)")
    
    plt.figure(figsize=(10, 7))
    
    for file_path, filename, week in file_list:
        try:
            df = pd.read_csv(file_path)
            
            # Rheology Data Columns: G'(2), G''(3), Strain(4)
            strain = df.iloc[:, 4].values
            gp = df.iloc[:, 2].values
            gpp = df.iloc[:, 3].values

            # Plot each replicate with a unique color/label
            # G' as solid line, G'' as dashed line
            line, = plt.plot(strain, gp, linestyle='-', alpha=0.8, 
                             label=f"{filename} ({week}) $G'$")
            plt.plot(strain, gpp, linestyle='--', color=line.get_color(), 
                     alpha=0.4, label=f"{filename} $G''$")
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # Log-Log scale for standard Rheological representation
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'Strain ($\gamma$) [%]')
    plt.ylabel(r"Modulus $G', G''$ [Pa]")
    plt.title(f"Replicate Comparison: Isolate {strain_id}")
    
    # Place legend outside the plot area
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()

    # Save each strain's comparison plot
    save_path = os.path.join(output_folder, f"strain_{strain_id}_comparison.png")
    plt.savefig(save_path, dpi=300)
    plt.close()

print(f"\nTask 2 Complete: Replicate plots saved in '{output_folder}'.")