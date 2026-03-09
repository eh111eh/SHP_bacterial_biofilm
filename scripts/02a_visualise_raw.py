import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import seaborn as sns

# --- 1. Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))
RESULTS_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results", "all_params.csv"))

# New Folders for your request
RAW_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "figures", "1_raw_sweeps"))

os.makedirs(RAW_FOLDER, exist_ok=True)

df_params = pd.read_csv(RESULTS_PATH)
isolates = df_params['Isolate'].unique()

def find_file_path(filename):
    search_pattern = os.path.join(BASE_DATA_PATH, "**", filename)
    files = glob.glob(search_pattern, recursive=True)
    return files[0] if files else None

# --- 2. Generate 1_raw_sweeps (Every single file) ---
print("Generating 1_raw_sweeps...")
for _, row in df_params.iterrows():
    fpath = find_file_path(row['Filename'])
    if not fpath: continue
    
    # Create subfolders for 30C and 50C inside 1_raw_sweeps
    sub_raw_path = os.path.join(RAW_FOLDER, row['Temperature'])
    os.makedirs(sub_raw_path, exist_ok=True)
    
    data = pd.read_csv(fpath).iloc[20:] # Simple skip for clean visualization
    strain, gp, gpp = data.iloc[:, 4], data.iloc[:, 2], data.iloc[:, 3]
    
    plt.figure(figsize=(6, 5))
    plt.loglog(strain, gp, 'o-', label="G'", markersize=4)
    plt.loglog(strain, gpp, 's--', label="G''", markersize=4)
    plt.title(f"Raw Sweep: {row['Filename']}")
    plt.xlabel("Strain [%]")
    plt.ylabel("Modulus [Pa]")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    
    plt.savefig(os.path.join(sub_raw_path, f"{row['Filename'].replace('.csv', '.png')}"))
    plt.close()

print("Done! Check your 'figures/1_raw_sweeps' folder.")