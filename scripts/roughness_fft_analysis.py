import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy import signal
import glob
import os
from matplotlib.lines import Line2D

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

def analyze_oct_file(file_path):
    try:
        df = pd.read_csv(file_path)
        # Surface extraction
        surface = df.groupby('X')['Y'].min().reset_index()
        
        x = surface['X'].values
        y = surface['Y'].values
        
        y_detrended = signal.detrend(y)
        
        # RMS
        rms = np.std(y_detrended)
        
        # FFT
        N = len(x)
        T = np.mean(np.diff(x))
        yf = fft(y_detrended)
        xf = fftfreq(N, T)[:N//2]
        amplitude = 2.0/N * np.abs(yf[:N//2])
        
        peak_idx = np.argmax(amplitude[1:]) + 1
        peak_freq = xf[peak_idx]
        wavelength = 1/peak_freq if peak_freq > 0 else np.nan
        
        return rms, wavelength
    except Exception as e:
        print(f"Error in {file_path}: {e}")
        return None, None

root_path = 'data/OCT'
results = []
files = glob.glob(os.path.join(root_path, '**', '*.csv'), recursive=True)

for f in files:
    path_parts = f.split(os.sep)
    temp = path_parts[-3] 
    filename = path_parts[-1]
    strain = filename.split('_')[0]
    
    rms, wavelength = analyze_oct_file(f)
    if rms is not None:
        results.append({'Strain': strain, 'Temp': temp, 'RMS': rms, 'Wavelength': wavelength})

res_df = pd.DataFrame(results)
summary = res_df.groupby(['Strain', 'Temp']).agg({
    'RMS': ['mean', 'std'],
    'Wavelength': ['mean', 'std']
}).reset_index()

summary.columns = ['Strain', 'Temp', 'RMS_mean', 'RMS_std', 'Wavelength_mean', 'Wavelength_std']
os.makedirs('results', exist_ok=True)
summary.to_csv('results/oct_fft_summary.csv', index=False)

# --- Transition Plot ---
plt.figure(figsize=(14, 10))
color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

for i, strain in enumerate(sorted(summary['Strain'].unique())):
    subset = summary[summary['Strain'] == strain].sort_values('Temp')
    color = color_cycle[i % len(color_cycle)]
    if len(subset) >= 2:
        x = subset['Wavelength_mean'].values
        y = subset['RMS_mean'].values
        x_err = subset['Wavelength_std'].values
        y_err = subset['RMS_std'].values
        
        # 30C: Circle (o), 50C: Triangle (^)
        plt.scatter(x[0], y[0], marker='o', s=250, color=color, edgecolors='black', zorder=5, label=strain)
        plt.scatter(x[1], y[1], marker='^', s=300, color=color, edgecolors='black', zorder=5)
        plt.errorbar(x[0], y[0], xerr=x_err[0], yerr=y_err[0],
                     fmt='none', color=color, capsize=5, linewidth=1.5, zorder=4)
        plt.errorbar(x[1], y[1], xerr=x_err[1], yerr=y_err[1],
                     fmt='none', color=color, capsize=5, linewidth=1.5, zorder=4)

plt.xlabel(r'Wavelength $\lambda$ [$\mu$m]', labelpad=15)
plt.ylabel(r'RMS Roughness [$\mu$m]', labelpad=15)

handles, labels = plt.gca().get_legend_handles_labels()
temp_elements = [
    Line2D([0], [0], marker='o', color='gray', label='30$^{\circ}$C', markersize=12, ls='None', markeredgecolor='k'),
    Line2D([0], [0], marker='^', color='gray', label='50$^{\circ}$C', markersize=12, ls='None', markeredgecolor='k')
]
plt.legend(handles=handles + temp_elements, bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)

plt.grid(True, linestyle='--', alpha=0.3, linewidth=1.5)
plt.tight_layout()

os.makedirs('figures/roughness', exist_ok=True)
plt.savefig('figures/roughness/structure_transition_plot.png', bbox_inches='tight')
plt.show()