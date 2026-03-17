# SHP_bacterial_biofilm

```
repo/
├── data/
│   ├── 30C/                # Weeks 3, 4, 5, reading_week
│   └── 50C/                # Weeks 6, 7
├── figures/
│   ├── raw/                # G' and G'' plots
│   ├── normalised/         # Normalised G' and G'' plots
│   └── parameters/         # Bar charts for tanδ, γf, γy, WSO (grouped by Temp)
├── results/
│   ├── all_params.csv
│   └── all_params_avg.csv
└── scripts/
    ├── raw_vis.py           # Raw Curves
    ├── raw_master.py        # Raw Master Curves
    ├── normalisation.py     # Normalized Master Curves
    ├── parameter.py         # Integrated parameter extraction for 30C and 50C (Output: all_params.csv & all_params_avg.csv)
    └── parameter_bar.py     # Comparison bar charts for G'_0, tan(delta), WSO, and yield strain
```