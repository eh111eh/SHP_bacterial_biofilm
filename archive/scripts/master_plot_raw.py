import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Configuration: Selected Best Files only
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

# Initialize a single plot
plt.figure(figsize=(12, 8))

for isolate, (week, filename) in best_files.items():
    file_path = os.path.join(base_data_path, week, filename)
    
    try:
        df = pd.read_csv(file_path)
        
        # Column mapping: G'(2), G''(3), Strain(4)
        strain = df.iloc[:, 4].values
        gp = df.iloc[:, 2].values
        gpp = df.iloc[:, 3].values

        # Styling: 3610 (Control) is Black and Bold, others are default colors
        color = 'black' if isolate == '3610' else None
        linewidth = 3.0 if isolate == '3610' else 1.5
        zorder = 10 if isolate == '3610' else 1 # Make 3610 appear on top

        # Plot G' (Solid line) and G'' (Dashed line)
        line, = plt.plot(strain, gp, linestyle='-', linewidth=linewidth, 
                         color=color, zorder=zorder, label=f"{isolate} $G'$")
        plt.plot(strain, gpp, linestyle='--', linewidth=linewidth-0.5, 
                 color=line.get_color(), alpha=0.5, zorder=zorder)
        
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# 2. Final Plot Formatting
plt.xscale('log')
plt.yscale('log')
plt.xlabel(r'Strain ($\gamma$) [%]', fontsize=12)
plt.ylabel(r"Modulus $G', G''$ [Pa]", fontsize=12)
plt.title("Master Raw Plot: All Representative Isolates vs 3610", fontsize=14)

# Place legend outside for clarity
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small', ncol=1)
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.tight_layout()

# 3. Save the single master plot
save_path = os.path.join(output_folder, "final_master_raw_plot.png")
plt.savefig(save_path, dpi=300)
plt.show()

print(f"Successfully generated ONE master plot: {save_path}")