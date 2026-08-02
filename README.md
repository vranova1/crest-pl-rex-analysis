# crest-pl-rex-analysis
Enhancement of Ligand Conformational Free Energy Estimation in the SQM2.20 Scoring Function Using CREST Sampling

# CREST Conformational Analysis Pipeline

This repository contains the scripts used in my bachelor's thesis for conformational sampling, geometry optimization, feature reconstruction, and analysis of the PL-REX dataset.

The workflow consists of several computational steps followed by analysis of the resulting conformational data.

---

## Requirements

All Python dependencies are specified in

```text
environment.yaml
```

Create the environment using Conda:

```bash
conda env create -f environment.yaml
conda activate <environment_name>
```

---

## Repository structure

```
.
├── config.sh
├── environment.yaml
├── steps/
│   ├── 01_crest_computation/
│   ├── 02_conformer_preparation/
│   ├── 03_conformer_refinement/
│   └── 04_lm5_reconstruction/
│
├── data/
│   ├── 01_data/
│   ├── 02_data/
│   ├── 03_data/
│   ├── 04_data/
│   └── pl_rex/
│
├── lib/
│   ├── extract/
│   ├── analysis/
│   └── ...
│
├── tables/
│
└── ...
```

---

# Computational workflow

## Configuration

The first three workflow steps obtain their configuration from

```text
config.sh
```

located in the project root.

Before running the workflow, update the paths in `config.sh` according to your local environment.

The fourth step (`04_lm5`) is independent of `config.sh`; instead, the project root path should be modified directly in `lm5.py`.

---

## Step 1 – CREST conformational search

```
steps/01_crest_computation/
```

Runs conformational sampling using **CREST**.

Execution:

```bash
run.sh
```

This script is designed to be executed on an HPC cluster using **SLURM**.

Some modifications (paths, submission parameters, etc.) may be required depending on the computing environment.

Input/output data are stored in

```
data/01_data/
```

---

## Step 2 – Update ligand SDF files

```
steps/02_conformer_preparation/
```

Updates ligand SDF files using the optimized geometries obtained from the CREST calculations.

Execution:

```bash
run.sh
```

Data are stored in

```
data/02_data/
```

---

## Step 3 – PM6 optimization

```
steps/03_conformer_refinement/
```

Runs PM6 geometry optimization using the structures produced in Step 2.

Execution:

```bash
run.sh
```

Data are stored in

```
data/03_data/
```

---

## Step 4 – LM5 feature reconstruction

```
steps/04_lm5_reconstruction/
```

Reconstructs the LM5 feature set.

Main script:

```text
lm5.py
```

Unlike the previous workflow steps, this script does **not** use `config.sh`.

Instead, update the project root path directly in

```python
lm5.py
```

Output files are stored in

```
data/04_data/
```

---

# Data

The complete dataset used in the thesis is too large to include in this repository.

Therefore,

- `data/` contains **three example ligands** demonstrating the expected input format and workflow.
- the `tables/` directory contains the exported **master_table.csv** for the complete dataset, allowing all analysis scripts to be reproduced without rerunning the computationally intensive calculations.

---

# Analysis

The analysis scripts are located in

```
lib/
```

Besides helper modules used internally by the workflow, two directories are intended for post-processing.

## Extract

```
lib/extract/
```

### create_master_table.py

Constructs the master table from the computed results.

---

## Analysis

```
lib/analysis/
```

Contains scripts for statistical analysis and visualization of the computed conformational descriptors.

Main scripts include:

- `correlate_results.py`
    - evaluates correlations between modified SQM2.20 scores and experimental binding affinities
- `plot_distributions.py`
    - generates distribution plots for computed corrections
- `generate_sconf_correl_plot.py`
    - produces correlation plots between LM5 entropies and CREST derived entropies

Before running these scripts, update the project root path near the beginning of each file and desired input file.

Optionally, output filenames can also be modified there.

By default, all generated tables and figures are written into

```
tables/
```

---

# Notes

- The workflow is intended primarily for Linux environments.
- The CREST pipeline assumes execution on a SLURM-managed HPC cluster.
- Only a small subset of ligands is included as an example because the full computational data exceed GitHub's storage limits.
- The exported master table is included so that all statistical analyses presented in the thesis can be reproduced without rerunning the expensive quantum chemical calculations.
