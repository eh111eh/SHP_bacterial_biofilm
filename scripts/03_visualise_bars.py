import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- 1. Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "results", "all_params.csv"))
OUTPUT_FOLDER = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "figures", "3_bars"))

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 300

# --- 2. Load Data ---
df = pd.read_csv(RESULTS_PATH)

# Added 'WSO' to the metrics dictionary
metrics = {
    'G0_prime': "Storage Modulus $G'_0$ [Pa] (Stiffness)",
    'tan_delta0': "Loss Tangent $\\tan \\delta_0$ (Fluidity)",
    'gamma_y': "Yield Strain $\\gamma_y$ [%] (Elastic Limit)",
    'WSO': "Weak Strain Overshoot Height [Pa] (Structural Ductility)"
}

# --- 3. Plotting Loop ---
for col, title in metrics.items():
    plt.figure(figsize=(12, 6))
    
    ax = sns.barplot(
        data=df, 
        x='Isolate', 
        y=col, 
        hue='Temperature',
        palette={'30C': '#3498db', '50C': '#e74c3c'},
        capsize=.1,
        errwidth=1.5,
        edgecolor='black'
    )
    
    # Use Log Scale for G0 and WSO due to high variance
    if col in ['G0_prime', 'WSO']:
        ax.set_yscale("log")
        ax.set_ylabel(f"{title} - Log Scale")
    else:
        ax.set_ylabel(title)

    plt.title(f"Comparison of {col} across Isolates", fontsize=14, pad=15)
    plt.xlabel("Isolate ID")
    plt.legend(title="Condition")
    
    save_path = os.path.join(OUTPUT_FOLDER, f"bar_{col}.png")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Generated Bar Chart: {save_path}")