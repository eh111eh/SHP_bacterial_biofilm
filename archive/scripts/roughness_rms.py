import pandas as pd
import numpy as np
import glob
import os

def calculate_rms(y_values):
    """Calculate RMS Roughness."""
    if len(y_values) == 0:
        return np.nan
    # sqrt(mean((y - mean_y)^2))
    mean_y = np.mean(y_values)
    rms = np.sqrt(np.mean((y_values - mean_y)**2))
    return rms

def process_rms_analysis(root_path="data/OCT"):
    strains = ['3610', '2103', '2106', '2107', '2108', '2109', '2125']
    temps = ['30C', '50C']
    
    all_results = []

    print("Starting RMS Roughness Calculation...")
    print("-" * 60)

    for strain in strains:
        for temp in temps:
            search_pattern = os.path.join(root_path, temp, "**", f"{strain}_*.csv")
            file_list = glob.glob(search_pattern, recursive=True)
            
            if not file_list:
                continue
                
            print(f"Processing: {strain} at {temp} ({len(file_list)} files)")

            for f in file_list:
                try:
                    df = pd.read_csv(f)
                    df.columns = [col.lower() for col in df.columns]
                    
                    # 1. Surface extract
                    surface = df.groupby('x')['y'].min().reset_index()
                    
                    # 2. RMS calculation
                    rms_val = calculate_rms(surface['y'].values)
                    
                    # 3. Save results
                    all_results.append({
                        'Strain': strain,
                        'Temp': temp,
                        'RMS': rms_val,
                        'File': os.path.basename(f)
                    })
                except Exception as e:
                    print(f"   > [ERROR] {os.path.basename(f)}: {e}")

    # Convert dataframe
    res_df = pd.DataFrame(all_results)

    if not os.path.exists('results'):
        os.makedirs('results')

    # 1. Save individual RMS values for all samples
    res_df.to_csv('results/all_rms_values.csv', index=False)
    
    # 2. Summarize mean and standard deviation by strain and temperature
    summary = res_df.groupby(['Strain', 'Temp'])['RMS'].agg(['mean', 'std', 'count']).reset_index()
    summary.columns = ['Strain', 'Temp', 'RMS_mean', 'RMS_std', 'n_samples']
    summary.to_csv('results/rms_summary.csv', index=False)

    print("-" * 60)
    print("Analysis Complete!")
    print(f"Individual values saved to: results/all_rms_values.csv")
    print(f"Summary table saved to: results/rms_summary.csv")
    print("-" * 60)
    
    return summary

if __name__ == "__main__":
    summary_data = process_rms_analysis()
    print(summary_data)