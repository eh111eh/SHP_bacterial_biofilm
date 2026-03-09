import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

# --- 1. Configuration ---
base_data_path = "data"
output_folder = "figures/4.1_parameter_plots_from_table"
csv_path = "results/params_best_samples.csv"
os.makedirs(output_folder, exist_ok=True)

# Load the parameters (The "Source of Truth")
df_params = pd.read_csv(csv_path)
df_params['Isolate'] = df_params['Isolate'].astype(str)
df_params = df_params.set_index('Isolate')

best_samples = {
    '3610': ('week3', '3610_30C_2.csv'),
    '2103': ('week4', '2103_30C_2.csv'),
    '2106': ('week4', '2106_30C_1.csv'),
    '2107': ('week5', '2107_30C_2.csv'),
    '2108': ('week5', '2108_30C_3.csv'),
    '2109': ('reading_week', '2109_30C_3.csv'),
    '2125': ('reading_week', '2125_30C_1.csv')
}

# --- 2. Individual Validation Plotting ---
for isolate, (week, filename) in best_samples.items():
    path = os.path.join(base_data_path, week, filename)
    df_raw = pd.read_csv(path)
    
    # Apply 1/3 skip
    df = df_raw.iloc[len(df_raw)//3:].reset_index(drop=True)
    
    p = df_params.loc[isolate]
    g0_ref = p['G0_prime']
    
    strain = df.iloc[:, 4].values
    gp_norm = df.iloc[:, 2].values / g0_ref
    gpp_norm = df.iloc[:, 3].values / g0_ref

    def get_y_on_curve(target_x, x_arr, y_arr):
        if np.isnan(target_x): return np.nan
        f_interp = interp1d(x_arr, y_arr, bounds_error=False, fill_value="extrapolate")
        return f_interp(target_x)

    plt.figure(figsize=(8, 6))
    plt.loglog(strain, gp_norm, '-', color='blue', alpha=0.4, label="$G'/G'_0$")
    plt.loglog(strain, gpp_norm, '-', color='red', alpha=0.4, label="$G''/G'_0$")

    # Points from CSV
    y_x, f_x = p['gamma_y'], p['gamma_f']
    plt.scatter(y_x, get_y_on_curve(y_x, strain, gp_norm), color='green', s=150, zorder=5, label=f'Yield ({y_x:.3f}%)')
    plt.scatter(f_x, get_y_on_curve(f_x, strain, gp_norm), color='black', s=150, zorder=5, label=f'Crossover ({f_x:.2f}%)')
    
    # WSO Peak
    wso_x = strain[np.argmax(gpp_norm)]
    plt.scatter(wso_x, np.max(gpp_norm), color='purple', s=150, zorder=5, label='WSO Peak')

    plt.axhline(1, color='gray', linestyle='--', alpha=0.3)
    plt.title(f"Table Validation: Isolate {isolate}")
    plt.xlabel("Strain [%]")
    plt.ylabel("Normalized Modulus [G/G'0]")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"plot_{isolate}_parameters_from_table.png"), dpi=300)
    plt.close()

# --- 3. Tan Delta Bar Chart ---
plt.figure(figsize=(10, 6))
# Using the index from df_params (Isolates) and the tan_delta0 column
isolates = df_params.index
tan_deltas = df_params['tan_delta0']

bars = plt.bar(isolates, tan_deltas, color='skyblue', edgecolor='navy', alpha=0.7)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.3f}', 
             ha='center', va='bottom', fontsize=10, fontweight='bold', color='navy')

plt.xlabel("Isolate Identity", fontsize=12)
plt.ylabel(r"Loss Tangent ($\tan \delta_0$)", fontsize=12)
plt.title("Comparison of Viscoelasticity (Tan Delta from Table)", fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()

plt.savefig(os.path.join(output_folder, "bar_chart_tan_delta_from_table.png"), dpi=300)
plt.show()

print(f"All plots and the Tan Delta bar chart have been saved in '{output_folder}'.")