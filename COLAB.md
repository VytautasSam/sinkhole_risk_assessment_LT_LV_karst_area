# Google Colab

The main notebook is directly available in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/VytautasSam/sinkhole_risk_assessment_LT_LV_karst_area/blob/main/notebooks/sinkhole_end_to_end.ipynb)

Direct Colab URL:

```text
https://colab.research.google.com/github/VytautasSam/sinkhole_risk_assessment_LT_LV_karst_area/blob/main/notebooks/sinkhole_end_to_end.ipynb
```

GitHub repository:

```text
https://github.com/VytautasSam/sinkhole_risk_assessment_LT_LV_karst_area
```

The notebook detects Google Colab automatically. On the first run it:

1. clones the public repository into `/content/sinkhole_risk_assessment_LT_LV_karst_area`;
2. installs `requirements.txt`;
3. uses repository-relative data paths;
4. downloads the core public reproducibility inputs only if they are not already stored in the repository;
5. downloads Figure 3 GIS inputs separately if they are required.

No GitHub username or repository URL needs to be entered manually.

For manuscript reproduction, keep both GridSearch switches enabled:

```python
USE_IMPUTATION_GRIDSEARCH = True
USE_RISK_GRIDSEARCH = True
```

Associated article:

[Sinkhole risk forecasting in the Lithuania–Latvia Karst region using artificial intelligence](https://www.sciencedirect.com/science/article/pii/S2214581826002703)
