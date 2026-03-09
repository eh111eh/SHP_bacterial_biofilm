import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os
import glob

# --- Configuration ---
base_data_path = "data"
results_folder = "results"
os.makedirs(results_folder, exist_ok=True)

# Best Samples Mapping
best_samples_dict = {
    '3610': ('week3', '3610_30C_2.csv'),
    '2103': ('week4', '2103_30C_2.csv'),
    '2106': ('week4', '2106_30C_1.csv'),
    '2107': ('week5', '2107_30C_2.csv'),
    '2108': ('week5', '2108_30C_3.csv'),
    '2109': ('reading_week', '2109_30C_3.csv'),
    '2125': ('reading_week', '2125_30C_1.csv')
}

def extract_parameters_smart(file_path):
    """
    Logic:
    1. Skip the first 1/3 of data points.
    2. Identify G'0 and G''0 in the linear regime (0.01% - 0.1% strain).
    3. Normalize G' and G'' by G'0.
    4. Calculate breakdown parameters (Yield, Crossover, WSO) using normalized data.
    """
    try:
        df_raw = pd.read_csv(file_path)
        
        # [Logic 1] Skip first 1/3 to remove startup noise
        df = df_raw.iloc[len(df_raw)//3:].reset_index(drop=True)
        
        strain = df.iloc[:, 4].values
        gp_orig = df.iloc[:, 2].values
        gpp_orig = df.iloc[:, 3].values
        
        # [Logic 3-1] Determine G'0 from the Linear Regime (0.01% - 0.1%)
        plateau_mask = (strain >= 0.01) & (strain <= 0.1)
        
        if not any(plateau_mask):
            # Fallback to the first 5 points of the skipped data if range is missing
            gp0 = np.mean(gp_orig[:5])
            gpp0 = np.mean(gpp_orig[:5])
        else:
            gp0 = np.mean(gp_orig[plateau_mask])
            gpp0 = np.mean(gpp_orig[plateau_mask])
            
        tan_delta0 = gpp0 / gp0
        
        # [Logic 2] Data Normalisation (relative to G'0)
        gp_norm = gp_orig / gp0
        gpp_norm = gpp_orig / gp0
        
        # [Logic 3-2] Calculate parameters using Normalized data
        # 1. Crossover Strain (gamma_f): Where normalized G' = G''
        gamma_f = np.nan
        diff = gp_norm - gpp_norm
        for i in range(len(diff) - 1):
            if diff[i] > 0 and diff[i+1] < 0:
                itp = interp1d([diff[i], diff[i+1]], [strain[i], strain[i+1]])
                gamma_f = float(itp(0))
                break
        
        # 2. Yield Strain (gamma_y): Where normalized G' < 0.95 (5% deviation)
        gamma_y = np.nan
        for i in range(len(gp_norm)):
            if gp_norm[i] < 0.95:
                gamma_y = strain[i]
                break
        
        # 3. Weak Strain Overshoot (WSO): Peak in G'' relative to plateau G''0
        gpp_max_orig = np.max(gpp_orig)
        wso = gpp_max_orig - gpp0
        
        return {
            'G0_prime': gp0,
            'tan_delta0': tan_delta0,
            'gamma_f': gamma_f,
            'gamma_y': gamma_y,
            'WSO': wso
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# --- TASK 1: Best Samples Analysis ---
best_results = []
for isolate, (week, filename) in best_samples_dict.items():
    path = os.path.join(base_data_path, week, filename)
    p = extract_parameters_smart(path)
    if p:
        p['Isolate'] = isolate
        best_results.append(p)
df_best = pd.DataFrame(best_results).set_index('Isolate')

# --- TASK 2: All Samples Averaged Analysis ---
all_extracted = []
weeks = ['week3', 'week4', 'week5', 'reading_week']
for week in weeks:
    files = glob.glob(os.path.join(base_data_path, week, "*.csv"))
    for file_path in files:
        # Extract isolate ID from filename (assuming 'ID_30C_X.csv' format)
        isolate_id = os.path.basename(file_path).split('_')[0]
        p = extract_parameters_smart(file_path)
        if p:
            p['Isolate'] = isolate_id
            all_extracted.append(p)

df_all = pd.DataFrame(all_extracted)
df_averaged = df_all.groupby('Isolate').mean()

# --- TASK 3: Comparison and Export to CSV ---
common_isolates = df_best.index.intersection(df_averaged.index)
df_best_final = df_best.loc[common_isolates]
df_avg_final = df_averaged.loc[common_isolates]
df_diff = df_best_final - df_avg_final

# Saving outputs
df_best_final.to_csv(os.path.join(results_folder, 'params_best_samples.csv'))
df_avg_final.to_csv(os.path.join(results_folder, 'params_averaged_all.csv'))
df_diff.to_csv(os.path.join(results_folder, 'params_difference.csv'))

print(f"Analysis complete. CSV files saved in '{results_folder}'.")