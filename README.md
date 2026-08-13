# Sinkhole risk forecasting in the Lithuania–Latvia Karst region using artificial intelligence

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/VytautasSam/sinkhole_risk_assessment_LT_LV_karst_area/blob/main/notebooks/sinkhole_end_to_end.ipynb)

Reproducibility repository for the integrated workflow described in:

**Samalavičius, V. et al. (2026). _Sinkhole risk forecasting in the Lithuania–Latvia Karst region using artificial intelligence_. Journal of Hydrology: Regional Studies, 65, 103372.**

Article: https://www.sciencedirect.com/science/article/pii/S2214581826002703  
DOI: https://doi.org/10.1016/j.ejrh.2026.103372

The repository contains one end-to-end notebook that reconstructs missing daily groundwater levels and passes the reconstructed table **directly in memory** to the monthly sinkhole-risk classifier. It also contains the article-oriented figures/tables and supplementary diagnostics assembled from the source notebooks.

## Repository layout

```text
.
├── README.md
├── CITATION.cff
├── environment.yml
├── requirements.txt
├── requirements-build-lock.txt
├── data/
│   ├── README.md
│   ├── manifest.csv
│   ├── raw/                 # core reproducibility inputs
│   └── map/                 # Figure 3 GIS inputs
├── notebooks/
│   ├── sinkhole_end_to_end.ipynb
│   └── source/              # source notebooks retained for provenance
├── scripts/
│   ├── download_data.py
│   ├── verify_data.py
│   └── capture_environment.py
├── validation/
│   ├── expected_imputation_summary.csv
│   ├── expected_general_summary.csv
│   ├── expected_per_well_accuracy.csv
│   └── full_36_gridsearch_reference.csv
├── figures/
│   ├── source/
│   └── generated/
└── tables/
```

## 1. Clone and create the environment

### Option A — Conda / Mamba

```bash
git clone <YOUR-REPOSITORY-URL>
cd <YOUR-REPOSITORY>
conda env create -f environment.yml
conda activate sinkhole-risk-ai
```

### Option B — Python virtual environment

Python 3.11 is recommended.

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Put the public data snapshot inside the GitHub repository

This repository is prepared to keep the reproducibility inputs **inside the repository**. The master archive is configured for **Git LFS** through `.gitattributes`; the smaller CSV/GeoJSON files use normal Git.

After creating the repository on GitHub, run the included workflow once:

1. Open **Actions**.
2. Select **Vendor public reproducibility data**.
3. Click **Run workflow**.

The workflow downloads all 11 public inputs, validates them, computes SHA-256 checksums, and commits the files under `data/raw/` and `data/map/`.

You can perform the same step locally:

```bash
git lfs install
python scripts/download_data.py --all
python scripts/verify_data.py
git add .gitattributes data/raw data/map data/checksums.sha256
git commit -m "Vendor public reproducibility data"
git push
```

Once that one-time step is complete, the GitHub repository itself contains the complete input snapshot used by the notebook.

## 3. Run the notebook

```bash
jupyter lab
```

Open:

```text
notebooks/sinkhole_end_to_end.ipynb
```

At the beginning of the notebook, leave both switches enabled for the reproduced workflow:

```python
USE_IMPUTATION_GRIDSEARCH = True
USE_RISK_GRIDSEARCH = True
```

Setting either switch to `False` is intended only for faster development runs and will not reproduce the manuscript tuning workflow.

## 4. Run in Google Colab

The repository uses a fixed Colab link to the public `main` branch. No username or repository-name replacement is required. The direct URL is:

```text
https://colab.research.google.com/github/VytautasSam/sinkhole_risk_assessment_LT_LV_karst_area/blob/main/notebooks/sinkhole_end_to_end.ipynb
```

The notebook is Colab-aware. It asks for the repository URL on the first Colab run, clones the repository, installs `requirements.txt`, and then uses the data committed under `data/`. If the data have not been vendored yet, the bootstrap can retrieve the public snapshot automatically.

## 5. Reproducibility targets

Reference outputs from the previously reproduced runs are included under `validation/`.

### Groundwater-level imputation

Expected mean across the seven wells:

- CV R² mean: **0.598473**
- CV R² SD: **0.109526**
- CV MAE mean: **0.183358 m**
- CV MAE SD: **0.019022 m**

The full expected per-well table is in `validation/expected_imputation_summary.csv`.

### Sinkhole-risk classification

The reproduced feature-set results are stored in `validation/expected_general_summary.csv`. Key targets include:

- Groundwater Features: Accuracy ≈ 0.670; ROC AUC ≈ 0.608
- Climatic Features: Accuracy ≈ 0.902; ROC AUC ≈ 0.907
- GS Combined Features: Accuracy ≈ 0.964; ROC AUC ≈ 0.865
- CGS Combined Features: Accuracy ≈ 0.932; ROC AUC ≈ 0.862

`validation/expected_per_well_accuracy.csv` contains all 56 well × feature-set results. `validation/full_36_gridsearch_reference.csv` retains the original full-grid CV results used to derive and verify the reduced 14-candidate search.

## 6. Freeze the exact environment after a successful reproduction

Package versions can change numerical ML behavior. Once you have reproduced the reference results on your machine or Colab runtime, save that exact environment:

```bash
python scripts/capture_environment.py
```

This creates:

```text
requirements-reproduced.txt
```

Commit that file with the repository/release. `requirements-build-lock.txt` is only a reference snapshot of the environment used when this GitHub bundle was assembled; it is not claimed to be the historical Colab lock used for the publication.

## Data provenance and redistribution

`data/manifest.csv` records the public source for every bundled input, while `data/checksums.sha256` records the exact downloaded bytes. The combined modeling table includes variables derived from E-OBS, GLEAM, GLDAS and national groundwater/sinkhole sources. Before making a public release that redistributes the downloaded files, verify that the redistribution terms of each upstream source are compatible with repository distribution.

## Large files and GitHub

The master daily archive is tracked with Git LFS (`.gitattributes`) so it can remain versioned with the repository even if it exceeds GitHub's normal 100 MiB Git-object limit.

## Source notebooks

The integrated notebook is the recommended entry point. The earlier map, level, imputation and risk notebooks are retained under `notebooks/source/` solely for provenance and troubleshooting.
