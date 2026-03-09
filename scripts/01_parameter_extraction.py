import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os
import glob

# --- 1. Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Moves up to project root, then into 'data'
BASE_DATA_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))
RESULTS_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results"))

os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Define the temperature subfolders based on your NEW directory structure
# Key is the middle folder (30C/50C), Value is the list of sub-sub-folders
TEMP_MAPPING = {
    "30C": ["reading_week", "week3", "week4", "week5"],
    "50C": ["week6", "week7"]
}

def extract_parameters(file_path, temperature):
    """
    Extracts rheological parameters from a single CSV file.
    """
    try:
        df_raw = pd.read_csv(file_path)
        
        # Extract metadata from filename (e.g., '2103_30C_1.csv')
        filename = os.path.basename(file_path)
        file_parts = filename.replace('.csv', '').split('_')
        
        # Expecting format: [Isolate, Temp, Replicate]
        isolate_id = file_parts[0]
        replicate = file_parts[-1]

        # [Logic] Skip first 1/3 of data points
        df = df_raw.iloc[len(df_raw)//3:].reset_index(drop=True)
        
        # Column mapping: 2:G', 3:G'', 4:Strain (%)
        strain = df.iloc[:, 4].values
        gp_orig = df.iloc[:, 2].values
        gpp_orig = df.iloc[:, 3].values
        
        # [Logic] Linear Regime (0.01% - 0.1% strain)
        plateau_mask = (strain >= 0.01) & (strain <= 0.1)
        
        if not any(plateau_mask):
            gp0 = np.mean(gp_orig[:5])
            gpp0 = np.mean(gpp_orig[:5])
        else:
            gp0 = np.mean(gp_orig[plateau_mask])
            gpp0 = np.mean(gpp_orig[plateau_mask])
            
        tan_delta0 = gpp0 / gp0
        
        # [Normalization]
        gp_norm = gp_orig / gp0
        gpp_norm = gpp_orig / gp0
        
        # 1. Crossover Strain (gamma_f)
        gamma_f = np.nan
        diff = gp_norm - gpp_norm
        for i in range(len(diff) - 1):
            if diff[i] > 0 and diff[i+1] < 0:
                itp = interp1d([diff[i], diff[i+1]], [strain[i], strain[i+1]])
                gamma_f = float(itp(0))
                break
        
        # 2. Yield Strain (gamma_y)
        gamma_y = np.nan
        for i in range(len(gp_norm)):
            if gp_norm[i] < 0.95:
                gamma_y = strain[i]
                break
        
        # 3. Weak Strain Overshoot (WSO)
        gpp_max_orig = np.max(gpp_orig)
        wso_height = gpp_max_orig - gpp0
        
        return {
            'Isolate': isolate_id,
            'Temperature': temperature,
            'Replicate': replicate,
            'G0_prime': gp0,
            'tan_delta0': tan_delta0,
            'gamma_f': gamma_f,
            'gamma_y': gamma_y,
            'WSO': wso_height,
            'Filename': filename
        }

    except Exception as e:
        print(f"  [!] Error in {os.path.basename(file_path)}: {e}")
        return None

# --- 2. Main Execution ---
all_results = []

print("="*60)
print("RHEOLOGY PARAMETER EXTRACTION: 30C & 50C COMPARISON")
print("="*60)
print(f"Base Directory: {BASE_DATA_PATH}")

for temp_folder, sub_folders in TEMP_MAPPING.items():
    print(f"\nScanning Category: {temp_folder}")
    
    for sub in sub_folders:
        # Correct Path: data / 30C / week3 / *.csv
        full_folder_path = os.path.join(BASE_DATA_PATH, temp_folder, sub)
        
        if not os.path.exists(full_folder_path):
            print(f"  [?] Path not found: {full_folder_path}")
            continue
            
        files = glob.glob(os.path.join(full_folder_path, "*.csv"))
        print(f"  [>] {sub}: Found {len(files)} files.")
        
        for f in files:
            params = extract_parameters(f, temp_folder)
            if params:
                all_results.append(params)

# --- 3. Save and Report ---
if not all_results:
    print("\n[!] FATAL: No data collected. Double check the folder structure.")
else:
    df_all = pd.DataFrame(all_results)
    df_all = df_all.sort_values(by=['Isolate', 'Temperature', 'Replicate'])
    
    output_path = os.path.join(RESULTS_FOLDER, "all_params.csv")
    df_all.to_csv(output_path, index=False)
    
    print("\n" + "="*60)
    print(f"SUCCESS: {len(df_all)} files processed.")
    print(f"File saved to: {output_path}")
    print("="*60)

    # Preview average G'0 to confirm data load
    if 'G0_prime' in df_all.columns:
        print("\nMean Plateau Modulus (G'0) by Isolate & Temp:")
        print(df_all.groupby(['Isolate', 'Temperature'])['G0_prime'].mean().unstack())