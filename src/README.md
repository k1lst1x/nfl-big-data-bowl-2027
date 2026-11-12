# Source code

Reusable project code will live here as the analysis develops.

- `nfl_bdb/` will contain data-loading, validation, feature, and outcome helpers.
- `nfl_bdb/players.py` builds the validated one-row-per-player WR cohort used by
  downstream outcome and feature pipelines.
- Notebook-specific exploratory work belongs in `notebooks/` until it is stable
  enough to be extracted into a reusable function.

No competition data should be committed to this repository.
