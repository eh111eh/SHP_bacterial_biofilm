# B. subtilis Biofilm Thermal Adaptation: Rheological and Morphological Characterisation

This repository contains all data, analysis scripts, and figures 
for a BSc Honours dissertation (Mathematical Physics, University 
of Edinburgh) investigating how extracellular matrix mechanics and 
surface morphology of *Bacillus subtilis* biofilms adapt to 
thermal stress.

## Project Overview

The study compares the laboratory reference strain NCIB 3610 with 
six environmental isolates (NRS 2103, 2106, 2107, 2108, 2109, 2125) 
grown at 30°C and 50°C. Oscillatory rheometry and Optical 
Coherence Tomography (OCT) are combined to link microscopic 
viscoelastic transitions to macroscopic surface structural changes.

---

## Repository Structure
```
.
├── data/
│   ├── 30C/               # Raw rheology CSVs at 30°C (by week)
│   ├── 50C/               # Raw rheology CSVs at 50°C (by week)
│   └── OCT/               # OCT surface profile CSVs (30C and 50C)
├── results/
│   ├── all_params.csv         # Per-replicate extracted parameters
│   ├── all_params_avg.csv     # Ensemble averages ± SD per isolate/temperature
│   ├── oct_fft_summary.csv    # OCT RMS roughness and wavelength (mean ± SD)
│   ├── oct_fft_all.csv        # Per-colony OCT metrics
│   └── statistical_report.txt # Welch's t-test and Bonferroni results
├── scripts/
│   ├── raw_master.py              # Master strain-sweep plots (30C and 50C)
│   ├── normalisation.py           # Normalised master curves
│   ├── parameter.py               # Parameter extraction pipeline
│   ├── parameter_bar.py           # Bar plots for G'₀, tan δ, γ_y, γ_f, WSO
│   ├── roughness_fft_analysis.py  # OCT surface segmentation, RMS, FFT
│   ├── stiffness_roughness_correlation.py  # G'₀/γ_y vs RMS correlation plots
│   ├── stats.py                   # Statistical testing
│   └── raw_vis.py                 # Individual isolate strain-sweep visualisation
├── figures/
│   ├── raw/               # Summary and per-isolate strain-sweep plots
│   ├── normalised/        # Normalised master curves
│   ├── parameters/        # Bar plots for all rheological parameters
│   └── roughness/         # OCT transition, correlation, and comparison plots
└── archive/               # Earlier analysis iterations (superseded)
```

---

## Methods Summary

### Biofilm Preparation

Cultures standardised to OD₆₀₀ = 0.5 in PBS were spotted (10 µL) 
onto agar plates and incubated for 48 h at either 30°C (inverted) 
or 50°C (upright). Each experimental run included NCIB 3610 as an 
internal reference.

### Rheology

Oscillatory strain sweeps (1 Hz, up to 200% strain) were performed 
on a Malvern Kinexus rheometer (PU20 upper plate, PLS40 lower 
plate). Six outlier datasets were excluded on the basis of 
non-physical fluctuations (see `results/statistical_report.txt`).

**Extracted parameters:**
- `G'₀`: plateau storage modulus (LVE mean)
- `tan δ₀`: loss tangent (LVE mean)
- `γ_y`: yield strain (5% drop below G'₀)
- `γ_f`: crossover strain (G' = G''); not reported for isolates 
  where no crossover was detected at 50°C (2108, 2125, 3610)
- `WSO`: weak strain overshoot intensity (threshold: 1 Pa)

Normalised master curves follow Jana et al. (2020): moduli scaled 
by G'₀, strain scaled by γ_f.

### OCT Surface Analysis

Biofilm–air interfaces were extracted from OCT volumetric scans 
in ImageJ (morphological subtraction). The central 80% of each 
profile was retained after edge cropping (10% each side), linearly 
detrended, and analysed for:
- **RMS roughness**: `sqrt(mean(y_detrended²))`
- **Dominant wavelength λ**: `1 / f_peak` from single-sided FFT

### Statistics

- Welch's t-test for 30°C vs 50°C comparisons per isolate
- Bonferroni correction (n = 6) for inter-isolate comparisons 
  at 50°C vs NCIB 3610
- log₁₀ transformation applied to G'₀ and WSO prior to testing
- Significance threshold: p < 0.05

---

## Key Results

At 30°C, all isolates form viscoelastic solid matrices (tan δ₀ < 
0.3) with broadly conserved yielding behaviour. At 50°C, the 
isolates diverge substantially:

| Group | Isolates | Behaviour at 50°C |
|-------|----------|-------------------|
| Liquefied | 3610, 2125, 2108 | Large ↑ tan δ₀ and γ_y; G'₀ ~10–16 Pa |
| Retained solid-like | 2106, 2107 | Little change in tan δ₀ or γ_y; G'₀ ~160–185 Pa |
| Intermediate | 2103, 2109 | G'₀ declines; tan δ₀ and γ_y largely unchanged |

OCT imaging shows a universal shift toward longer wrinkling 
wavelengths at 50°C. RMS roughness generally co-declines with 
stiffness; yield strain γ_y is a more consistent predictor of 
surface roughness than G'₀ alone.

---

## Dependencies
```
Python 3.x
numpy
scipy
pandas
matplotlib
```

---

## Data Notes

- Raw rheology data in `data/30C/` and `data/50C/` are organised 
  by experimental week
- OCT surface profiles in `data/OCT/` are organised by temperature 
  and week, with one CSV per colony scan
- Outliers excluded from analysis: `week6/2103_50C_1`, 
  `week6/2106_50C_1`, `week8/2107_50C_1`, `week4/2106_30C_3`, 
  `week5/2107_30C_3`, `reading_week/2109_30C_1`
- γ_f reported as `---` for 2108, 2125, and 3610 at 50°C (no 
  detectable G' = G'' crossover within 200% strain range)

---

## Reference

NRS isolates provided by the N.R. Stanley-Wall laboratory, 
University of Dundee. NCIB 3610 obtained from TBD.