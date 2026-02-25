import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

# --- Configuration ---
base_data_path = "data"
output_folder = "figures/4_parameter_plots"
os.makedirs(output_folder, exist_ok=True)

best_samples = {
    '3610': ('week3', '3610_30C_2.csv'),
    '2103': ('week4', '2103_30C_2.csv'),
    '2106': ('week4', '2106_30C_1.csv'),
    '2107': ('week5', '2107_30C_2.csv'),
    '2108': ('week5', '2108_30C_3.csv'),
    '2109': ('reading_week', '2109_30C_3.csv'),
    '2125': ('reading_week', '2125_30C_1.csv')
}

extracted_data = []

# --- Step 1: Individual Plotting & Parameter Extraction ---
for isolate, (week, filename) in best_samples.items():
    path = os.path.join(base_data_path, week, filename)
    df_raw = pd.read_csv(path)
    
    # 1. Skip the first 1/3 of data points
    df = df_raw.iloc[len(df_raw)//3:].reset_index(drop=True)
    
    strain = df.iloc[:, 4].values
    gp_raw = df.iloc[:, 2].values
    gpp_raw = df.iloc[:, 3].values

    # 2. Identify Linear Plateau (0.01% - 0.1%) to find Normalisation factor G'0
    mask = (strain >= 0.01) & (strain <= 0.1)
    gp0 = np.mean(gp_raw[mask]) if any(mask) else np.mean(gp_raw[0:5])
    gpp0 = np.mean(gpp_raw[mask]) if any(mask) else np.mean(gpp_raw[0:5])
    tan_d = gpp0 / gp0

    # 3. Data Normalisation
    gp = gp_raw / gp0
    gpp = gpp_raw / gp0

    # 4. Parameter Extraction (using normalised data)
    # Yield Strain (where G' drops below 95% of G'0, which is 0.95 in normalised plot)
    try:
        y_idx = np.where(gp < 0.95)[0][0]
        gamma_y, gp_y = strain[y_idx], gp[y_idx]
    except IndexError:
        gamma_y, gp_y = np.nan, np.nan

    # Crossover Strain (where G' = G'')
    gamma_f, val_f = np.nan, np.nan
    for i in range(len(gp)-1):
        if gp[i] > gpp[i] and gp[i+1] < gpp[i+1]:
            itp = interp1d([gp[i]-gpp[i], gp[i+1]-gpp[i+1]], [strain[i], strain[i+1]])
            gamma_f = float(itp(0))
            # Interpolate the Y-value at the crossover
            val_f = float(interp1d([strain[i], strain[i+1]], [gp[i], gp[i+1]])(gamma_f))
            break

    # Weak Strain Overshoot (Peak in G'')
    wso_idx = np.argmax(gpp)
    gamma_wso, gpp_wso = strain[wso_idx], gpp[wso_idx]

    extracted_data.append({'Isolate': isolate, 'tan_delta': tan_d})

    # --- Plotting Individual Normalised Strain Sweep with 3 Points ---
    plt.figure(figsize=(8, 6))
    plt.loglog(strain, gp, 'o-', label="$G'/G'_0$", color='blue', alpha=0.6)
    plt.loglog(strain, gpp, 'o-', label="$G''/G'_0$", color='red', alpha=0.6)

    # Plot the 3 key points
    if not np.isnan(gamma_y):
        plt.scatter(gamma_y, gp_y, color='green', s=150, zorder=5, label=f'Yield ({gamma_y:.2f}%)')
    if not np.isnan(gamma_f):
        plt.scatter(gamma_f, val_f, color='black', s=150, zorder=5, label=f'Crossover ({gamma_f:.2f}%)')
    plt.scatter(gamma_wso, gpp_wso, color='purple', s=150, zorder=5, label=f'WSO Peak ({gamma_wso:.2f}%)')

    plt.axhline(1, color='gray', linestyle='--', alpha=0.3) # Baseline G'0
    plt.title(f"Normalised Parameter Analysis: Isolate {isolate}")
    plt.xlabel("Strain [%]")
    plt.ylabel("Normalised Modulus [G/G'0]")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"plot_{isolate}_parameters_norm.png"), dpi=300)
    plt.close()

# --- Step 2: Tan Delta Bar Chart ---
df_tan = pd.DataFrame(extracted_data)
plt.figure(figsize=(10, 6))
bars = plt.bar(df_tan['Isolate'], df_tan['tan_delta'], color='skyblue', edgecolor='navy')

# Labeling
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.3f}', ha='center', va='bottom', color='blue', fontweight='bold')

plt.ylabel(r"Loss Tangent ($\tan \delta_0$)")
plt.xlabel("Isolate Identity")
plt.title("Viscoelasticity Comparison (Linear Regime: 0.01% - 0.1% Strain)")
plt.savefig(os.path.join(output_folder, "bar_chart_tan_delta.png"), dpi=300)
plt.show()

print(f"Visualisation complete. 7 Normalised plots and 1 Bar chart saved in '{output_folder}'.")