import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import seaborn as sns

# --- 1. Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))
RESULTS_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results", "all_params.csv"))

# Directory Setup
RAW_ALL_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "figures", "1_raw_sweeps", "side-by-side"))
COMP_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "figures", "1_raw_sweeps", "all"))

os.makedirs(RAW_ALL_FOLDER, exist_ok=True)
os.makedirs(COMP_FOLDER, exist_ok=True)

df_params = pd.read_csv(RESULTS_PATH)
isolates = df_params['Isolate'].unique()

def find_file_path(filename):
    search_pattern = os.path.join(BASE_DATA_PATH, "**", filename)
    files = glob.glob(search_pattern, recursive=True)
    return files[0] if files else None

# --- 2. Plotting Loop ---
for isolate in isolates:
    iso_data = df_params[df_params['Isolate'] == isolate]

    # [TASK 1] Side-by-Side (for 1_raw_sweeps/all)
    # Left (30C) vs Right (50C) separated
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    axes = {'30C': ax1, '50C': ax2}
    palette_map = {'30C': 'Blues', '50C': 'Reds'}

    # [TASK 2] Direct Overlay (for 4_temp_comparison)
    # 30C and 50C on the SAME plot
    fig2, ax_comp = plt.subplots(figsize=(8, 7))
    colors_comp = {'30C': '#3498db', '50C': '#e74c3c'} # Fixed colors for comparison

    for temp in ['30C', '50C']:
        temp_set = iso_data[iso_data['Temperature'] == temp]
        if temp_set.empty: continue

        # Side-by-side palette
        sbs_palette = sns.color_palette(palette_map[temp], n_colors=len(temp_set) + 2)
        
        for i, (_, row) in enumerate(temp_set.iterrows()):
            fpath = find_file_path(row['Filename'])
            if fpath:
                data = pd.read_csv(fpath)
                data = data.iloc[len(data)//3:].reset_index(drop=True)
                strain, gp, gpp = data.iloc[:, 4], data.iloc[:, 2], data.iloc[:, 3]

                # Plot for Task 1 (Side-by-Side)
                axes[temp].loglog(strain, gp, '-', color=sbs_palette[i+2], label=f"Rep {row['Replicate']} G'")
                axes[temp].loglog(strain, gpp, '--', color=sbs_palette[i+2], alpha=0.5, label=f"Rep {row['Replicate']} G''")

                # Plot for Task 2 (Overlay Comparison)
                label_gp = f"{temp} G'" if i == 0 else ""
                label_gpp = f"{temp} G''" if i == 0 else ""
                ax_comp.loglog(strain, gp, '-', color=colors_comp[temp], alpha=0.6, linewidth=2, label=label_gp)
                ax_comp.loglog(strain, gpp, '--', color=colors_comp[temp], alpha=0.4, linewidth=1.5, label=label_gpp)

    # Finalize & Save Task 1
    fig1.suptitle(f"Isolate {isolate}: All Replicates (30C vs 50C)", fontsize=16)
    ax1.set_ylabel("Modulus [Pa]")
    for t, ax in axes.items():
        ax.set_title(f"Temp: {t}")
        ax.set_xlabel("Strain [%]")
        ax.grid(True, which="both", alpha=0.2)
        ax.legend(fontsize='x-small', ncol=2)
    fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig1.savefig(os.path.join(RAW_ALL_FOLDER, f"all_replicates_{isolate}.png"), dpi=300)
    plt.close(fig1)

    # Finalize & Save Task 2
    ax_comp.set_title(f"Raw Thermal Comparison: Isolate {isolate}", fontsize=14)
    ax_comp.set_xlabel("Strain [%]")
    ax_comp.set_ylabel("Modulus [Pa]")
    ax_comp.grid(True, which="both", alpha=0.2)
    ax_comp.legend()
    fig2.tight_layout()
    fig2.savefig(os.path.join(COMP_FOLDER, f"raw_comparison_{isolate}.png"), dpi=300)
    plt.close(fig2)

    print(f"Completed figures for Isolate {isolate}")

print("\nSuccess! Results are in '1_raw_sweeps/all' and '4_temp_comparison'.")