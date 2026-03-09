import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# 1. Configuration
weeks = ['week3', 'week4', 'week5', 'reading_week']
base_data_path = "data"
output_folder = "figures/comparisons"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

all_gp0_results = []

# 2. Loop through all weeks and files to collect G'0
for week in weeks:
    target_path = os.path.join(base_data_path, week, "*.csv")
    files = glob.glob(target_path)
    
    for file in files:
        filename = os.path.basename(file)
        isolate_id = filename.split('_')[0]
        
        try:
            df = pd.read_csv(file)
            
            # --- RAW DATA ONLY (NO 1/3 SKIP) ---
            gp_plateau_region = df.iloc[0:5, 2].values 
            gp0 = np.mean(gp_plateau_region)
            
            all_gp0_results.append({
                'Isolate': isolate_id, 
                'G0_prime': gp0,
                'Week': week
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# 3. Data Aggregation and Statistics
df_all = pd.DataFrame(all_gp0_results)
stats = df_all.groupby('Isolate')['G0_prime'].agg(['mean', 'std', 'count']).reset_index()
stats['sem'] = stats['std'] / np.sqrt(stats['count'])

# 4. Sorting for Direct Comparison
isolate_order = ['3610'] + sorted([x for x in stats['Isolate'].unique() if x != '3610'])
stats['Isolate'] = pd.Categorical(stats['Isolate'], categories=isolate_order, ordered=True)
stats = stats.sort_values('Isolate')

# 5. Plotting
plt.figure(figsize=(10, 6))

# Plotting bars and error bars
bars = plt.bar(stats['Isolate'], stats['mean'], yerr=stats['sem'], 
               capsize=8, color='skyblue', edgecolor='navy', alpha=0.8)

# Axis labels
plt.ylabel(r"Plateau Storage Modulus $G'_0$ [Pa]", fontsize=12)
plt.xlabel("Isolate Identity", fontsize=12)
plt.title("Stiffness Comparison: Soil Isolates vs 3610 (Raw Data)", fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
save_path = os.path.join(output_folder, "stiffness_comparison_G0.png")
plt.savefig(save_path, dpi=300)
plt.show()

print(f"Analysis Complete. Results saved to: {save_path}")