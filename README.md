# SHP_bacterial_biofilm

```
repo/
├── data/
│   ├── 30C/                # Weeks 3, 4, 5, reading_week
│   └── 50C/                # Weeks 6, 7
├── figures/
│   ├── 1_raw_sweeps/       # G' and G'' plots (subfolders for 30C and 50C)
│   ├── 2_normalized/       # Curve collapse (G/G0 vs gamma/gamma_f)
│   └── 3_bars/             # Bar charts for tanδ, γf, γy, WSO (grouped by Temp)
├── results/
│   ├── all_params.csv
│   └── statistical_report.txt
└── scripts/
    ├── 01_parameter_extraction.py          # Integrated parameter extraction for 30C and 50C (Output: all_params.csv)
    ├── 02_visualize_sweeps.py              # Raw/Normalized Curves (Including Data Collapse)
    ├── 03_visualize_bars.py                # Comparison bar charts for G'_0, tan(delta), WSO, and yield strain
    └── 04_statistical_test.py              # Statistical tests (t-tests/ANOVA)
```