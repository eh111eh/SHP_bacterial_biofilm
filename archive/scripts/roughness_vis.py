import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import glob
import os

def extract_surface_from_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        df.columns = [col.lower() for col in df.columns]
        surface = df.groupby('x')['y'].min().reset_index()
        surface = surface.sort_values('x')
        return surface
    except Exception as e:
        print(f"   > [ERROR] {os.path.basename(filepath)}: {e}")
        return None

def get_averaged_data(strain, temp, root_path="data/OCT"):
    search_pattern = os.path.join(root_path, temp, "**", f"{strain}_*.csv")
    file_list = glob.glob(search_pattern, recursive=True)
    
    if not file_list: 
        return None, None, None

    common_x = np.linspace(0, 6000, 3000)
    all_y = []

    for f in file_list:
        surf = extract_surface_from_csv(f)
        if surf is not None and len(surf) > 0:
            f_interp = interp1d(surf['x'], surf['y'], bounds_error=False, fill_value=np.nan)
            all_y.append(f_interp(common_x))

    if not all_y: return None, None, None

    mean_y = np.nanmean(all_y, axis=0)
    std_y = np.nanstd(all_y, axis=0)
    
    mask = ~np.isnan(mean_y)
    valid_x = common_x[mask]
    if len(valid_x) == 0: return None, None, None

    shifted_x = valid_x - valid_x[0]
    return shifted_x, mean_y[mask], std_y[mask]

def plot_temperature_comparison(strain, root_path="data/OCT", save_folder="figures/roughness"):
    """Compare 30C and 50C (Align starting points to 0 and normalize lengths) then save."""
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    x30, y30, s30 = get_averaged_data(strain, '30C', root_path)
    x50, y50, s50 = get_averaged_data(strain, '50C', root_path)

    if x30 is None and x50 is None:
        print(f"   [SKIP] No data found for {strain}")
        return

    plt.figure(figsize=(12, 5))
    
    max_x_limit = 0

    if x30 is not None:
        plt.fill_between(x30, y30 - s30, y30 + s30, color='royalblue', alpha=0.2)
        plt.plot(x30, y30, color='royalblue', linewidth=2, label='30°C (EPS-rich)')
        max_x_limit = x30.max()

    if x50 is not None:
        if x30 is not None:
            mask50 = x50 <= max_x_limit
            x50, y50, s50 = x50[mask50], y50[mask50], s50[mask50]
        else:
            max_x_limit = x50.max()
            
        plt.fill_between(x50, y50 - s50, y50 + s50, color='crimson', alpha=0.2)
        plt.plot(x50, y50, color='crimson', linewidth=2, label='50°C (PGA-rich)')

    plt.gca().invert_yaxis()
    plt.title(f"Biofilm Surface: {strain}", fontsize=14)
    plt.xlabel("Relative Horizontal Distance (pixels)")
    plt.ylabel("Vertical Depth (pixels)")
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xlim(0, max_x_limit)
    
    plt.tight_layout()
    
    save_path = os.path.join(save_folder, f"comparison_{strain}.png")
    plt.savefig(save_path)
    print(f"   [SAVE] Saved plot to {save_path}")
    
    plt.close()

# --- Main Loop ---

strains = ['3610', '2103', '2106', '2107', '2108', '2109', '2125']

print("Starting Batch Processing for OCT Surface Analysis...")
print("-" * 50)

for s in strains:
    print(f"\n>>> Processing Strain: {s}")
    plot_temperature_comparison(strain=s)

print("\n" + "-" * 50)
print("All strains processed successfully.")