import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os
import glob

# --- 1. Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))
RESULTS_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results"))

os.makedirs(RESULTS_FOLDER, exist_ok=True)

TEMP_MAPPING = {
    "30C": ["reading_week", "week3", "week4", "week5"],
    "50C": ["week6", "week7"]
}

EXCLUDE_FILES = ["2103_50C_1.csv", "2109_30C_1.csv"]

def extract_parameters(file_path, temperature):
    try:
        df_raw = pd.read_csv(file_path)
        df = df_raw.iloc[23:].reset_index(drop=True)
        
        filename = os.path.basename(file_path)
        file_parts = filename.replace('.csv', '').split('_')
        
        isolate_id = file_parts[0]
        replicate = file_parts[-1]

        strain = df.iloc[:, 4].values
        gp_orig = df.iloc[:, 2].values
        gpp_orig = df.iloc[:, 3].values
        
        plateau_mask = (strain >= 0.01) & (strain <= 0.1)
        
        if not any(plateau_mask):
            gp0 = np.mean(gp_orig[:5])
            gpp0 = np.mean(gpp_orig[:5])
        else:
            gp0 = np.mean(gp_orig[plateau_mask])
            gpp0 = np.mean(gpp_orig[plateau_mask])
            
        tan_delta0 = gpp0 / gp0
        gp_norm = gp_orig / gp0
        gpp_norm = gpp_orig / gp0
        
        gamma_f = np.nan
        diff = gp_norm - gpp_norm
        for i in range(len(diff) - 1):
            if diff[i] > 0 and diff[i+1] < 0:
                itp = interp1d([diff[i], diff[i+1]], [strain[i], strain[i+1]])
                gamma_f = float(itp(0))
                break
        
        gamma_y = np.nan
        for i in range(len(gp_norm)):
            if gp_norm[i] < 0.95:
                gamma_y = strain[i]
                break
        
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

for temp_folder, sub_folders in TEMP_MAPPING.items():
    print(f"\nScanning Category: {temp_folder}")
    for sub in sub_folders:
        full_folder_path = os.path.join(BASE_DATA_PATH, temp_folder, sub)
        if not os.path.exists(full_folder_path): continue
            
        files = glob.glob(os.path.join(full_folder_path, "*.csv"))
        print(f"  [>] {sub}: Found {len(files)} files.")
        
        for f in files:
            fname = os.path.basename(f)
            if fname in EXCLUDE_FILES:
                print(f"  [-] Skipping excluded file: {fname}")
                continue

            params = extract_parameters(f, temp_folder)
            if params:
                all_results.append(params)

# --- 3. Save and Report ---
if not all_results:
    print("\n[!] FATAL: No data collected.")
else:
    # 3.1 Save Individual Data (all_params.csv)
    df_all = pd.DataFrame(all_results)
    df_all = df_all.sort_values(by=['Isolate', 'Temperature', 'Replicate'])
    
    output_path = os.path.join(RESULTS_FOLDER, "all_params.csv")
    df_all.to_csv(output_path, index=False)
    
    # 3.2 Save Averaged Data (all_params_avg.csv)
    # Define columns to average
    numeric_cols = ['G0_prime', 'tan_delta0', 'gamma_f', 'gamma_y', 'WSO']
    
    # Group by Isolate and Temperature, then calculate Mean and Std Dev
    df_avg = df_all.groupby(['Isolate', 'Temperature'])[numeric_cols].agg(['mean', 'std']).reset_index()
    
    # Flatten column names (e.g., G0_prime_mean, G0_prime_std)
    df_avg.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_avg.columns]
    
    avg_output_path = os.path.join(RESULTS_FOLDER, "all_params_avg.csv")
    df_avg.to_csv(avg_output_path, index=False)
    
    print("\n" + "="*60)
    print(f"SUCCESS: {len(df_all)} files processed.")
    print(f"Individual: {output_path}")
    print(f"Averaged:   {avg_output_path}")
    print("="*60)