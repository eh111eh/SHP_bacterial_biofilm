import os
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d

def find_column(columns, keywords):
    for col in columns:
        if any(key.lower() in col.lower() for key in keywords):
            return col
    return None

def extract_metrics_from_data(strain, g1, g2):
    """Extract parameters from individual measurement data"""
    # 1. Linear Regime Mask (User-defined: 10^-0.8 ~ 10^0)
    plateau_mask = (strain >= 10**-0.8) & (strain <= 1.0)
    
    # Prepare for cases where plateau data is insufficient
    if not any(plateau_mask):
        return [np.nan] * 5

    gp0 = np.nanmean(g1[plateau_mask])
    gpp0 = np.nanmean(g2[plateau_mask])
    tan_delta0 = gpp0 / gp0
    
    # 2. Yield Strain (gamma_y): The point where G' drops to 95% of G'0
    gamma_y = np.nan
    for i in range(len(g1)):
        # Search starting after the linear region
        if strain[i] >= 10**-0.8 and g1[i] < 0.95 * gp0:
            gamma_y = strain[i]
            break
            
    # 3. Crossover Strain (gamma_f): G' = G'' (via interpolation)
    gamma_f = np.nan
    diff = g1 - g2
    for i in range(len(diff) - 1):
        if diff[i] > 0 and diff[i+1] < 0:
            itp = interp1d([diff[i], diff[i+1]], [strain[i], strain[i+1]])
            gamma_f = float(itp(0))
            break
            
    # 4. Weak Strain Overshoot (WSO): G''_{peak} - G''0
    post_plateau_mask = (strain > 0.5) 
    if any(post_plateau_mask):
        gpp_max = np.nanmax(g2[post_plateau_mask])
        wso_height = gpp_max - gpp0
        wso_height = max(0, wso_height)
    else:
        wso_height = 0
    
    return gp0, tan_delta0, gamma_f, gamma_y, wso_height

def analyze_rheology_by_replicates(data_root, output_dir):
    data_path = Path(data_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outliers = [
        "week6/2103_50C_1", "week6/2106_50C_1", "week8/2107_50C_1", 
        "week4/2106_30C_3", "week5/2107_30C_3", "reading_week/2109_30C_1"
    ]

    all_individual_results = []

    # Iterate through all individual files
    for csv_file in data_path.rglob("*.csv"):
        identifier = f"{csv_file.parent.name}/{csv_file.stem}"
        if identifier in outliers: continue
        
        parts = csv_file.stem.split('_')
        if len(parts) < 2: continue
        sample_id, temp = parts[0], parts[1]

        try:
            df = pd.read_csv(csv_file)
            col_x = find_column(df.columns, ['Complex shear strain(%)'])
            col_g1 = find_column(df.columns, ['elastic component'])
            col_g2 = find_column(df.columns, ['viscous component'])
            
            df = df.dropna(subset=[col_x, col_g1, col_g2]).sort_values(by=col_x)
            
            # Extract parameters directly from each
            gp0, tan0, gf, gy, wso = extract_metrics_from_data(
                df[col_x].values, df[col_g1].values, df[col_g2].values
            )
            
            all_individual_results.append({
                'Isolate': sample_id,
                'Temperature': temp,
                'G0_prime': gp0,
                'tan_delta0': tan0,
                'gamma_f': gf,
                'gamma_y': gy,
                'WSO': wso
            })
        except Exception as e:
            print(f"Error in {identifier}: {e}")

    # 1. Store all replicate results
    df_raw = pd.DataFrame(all_individual_results)
    df_raw.to_csv(output_path / "all_params.csv", index=False)

    # 2. Calculate the mean and standard deviation by sample/temperature
    numeric_cols = ['G0_prime', 'tan_delta0', 'gamma_f', 'gamma_y', 'WSO']
    df_avg = df_raw.groupby(['Isolate', 'Temperature'])[numeric_cols].agg(['mean', 'std']).reset_index()
    
    # Clean up column names (e.g., G0_prime_mean, G0_prime_std)
    df_avg.columns = [f"{c[0]}_{c[1]}" if c[1] else c[0] for c in df_avg.columns]

    df_avg.to_csv(output_path / "all_params_avg.csv", index=False)
    
    print(f"✅ Analysis complete.")
    print(f"   - Individual results: {output_path}/all_params.csv")
    print(f"   - Averaged results: {output_path}/all_params_avg.csv")
    
    return df_avg

if __name__ == "__main__":
    analyze_rheology_by_replicates("data", "results")