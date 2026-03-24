import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams.update({
    'mathtext.fontset': 'cm',
    'font.size': 28,
    'axes.titlesize': 32,
    'axes.labelsize': 28,
    'xtick.labelsize': 24,
    'ytick.labelsize': 24,
    'legend.fontsize': 20,
    'axes.unicode_minus': False,
    'axes.linewidth': 2,
    'figure.dpi': 150
})

def plot_roughness_correlations():
    rms_df = pd.read_csv('results/oct_fft_summary.csv')
    rheo_df = pd.read_csv('results/all_params_avg.csv')
    rheo_df = rheo_df.rename(columns={'Isolate': 'Strain', 'Temperature': 'Temp'})

    master_df = pd.merge(rms_df, rheo_df, on=['Strain', 'Temp'])
    
    unique_strains = sorted(master_df['Strain'].unique())
    marker_list = ['o', 's', 'P', 'D', 'v', '^', 'X']
    strain_markers = dict(zip(unique_strains, marker_list))

    output_dir = Path("figures/roughness")
    output_dir.mkdir(parents=True, exist_ok=True)

    def create_plot(x_col, xlabel, filename, is_log=False):
        plt.figure(figsize=(14, 10))
        
        sns.scatterplot(data=master_df, x=x_col, y='RMS_mean', 
                        hue='Temp', style='Strain', 
                        markers=strain_markers, s=400,
                        palette={'30C': 'royalblue', '50C': 'crimson'}, 
                        edgecolor='black', zorder=3)
        
        if is_log: plt.xscale('log')
        
        plt.xlabel(xlabel, labelpad=15)
        plt.ylabel(r"RMS Roughness [$\mu$m]", labelpad=15)
        plt.grid(True, which="both", ls="--", alpha=0.3)
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
        plt.tight_layout()
        plt.savefig(output_dir / filename, bbox_inches='tight')
        plt.close()

    # 1. G'0 vs RMS
    create_plot('G0_prime_mean', r"Storage Modulus $G'_0$ [Pa]", "correlation_stiffness_rms.png", is_log=True)
    
    # 2. Yield Strain vs RMS (gamma_y replaces gamma_f)
    create_plot('gamma_y_mean', r"Yield Strain $\gamma_y$ [%]", "correlation_yield_rms.png")
    
    print("✅ Correlation plots with unique isolate markers saved.")

if __name__ == "__main__":
    plot_roughness_correlations()