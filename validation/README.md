# Reference outputs

These files are preserved from successful reproduction runs and are intended as numerical regression targets.

- `expected_imputation_summary.csv` — seven-well Extra Trees imputation summary plus average.
- `expected_general_summary.csv` — aggregate sinkhole-risk performance for the eight feature sets.
- `expected_per_well_accuracy.csv` — 56 well × feature-set classification results.
- `full_36_gridsearch_reference.csv` — candidate-level results from the original 36-candidate Random Forest search, retained to validate the reduced 14-candidate grid.

Minor display rounding is acceptable, but changes in underlying predictions or selected hyperparameters should be investigated before a release is labelled reproducible.
