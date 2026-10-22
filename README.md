# NFL Big Data Bowl 2027

Course project for **CS501: Practical Applications of Algorithms** using the
[NFL Big Data Bowl 2027](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027)
competition.

## Team

- Damir Mertl — Data and Integration Lead
- Aayush Agasti — Combine Feature Engineering Lead
- Aliia Rustamova — NFL Performance and Outcome Lead
- Viplav Dodeja — Movement Physics Lead
- Meerimgul Abdibaap Kyzy — Modeling and Validation Lead

## Project goal

Investigate whether athletic traits measured at the NFL Scouting Combine are
associated with yards after catch (YAC) per reception among NFL wide receivers.
The analysis compares traditional Combine results with movement traits derived
from 10 Hz Combine tracking data.

The primary research question is:

> Do speed, acceleration, and change-of-direction traits measured using Combine
> tracking data help explain wide receivers' average YAC beyond traditional
> Combine results?

This is an association analysis, not a claim that Combine performance causes NFL
success. Predictive comparisons are included only if the available player sample
supports reliable player-grouped validation.

## Project pipeline

The analysis workflow and component relationships are documented in
[docs/architecture.md](docs/architecture.md).

## Repository layout

```text
docs/       Proposal, requirements, data guide, and architecture
data/       Local competition data (ignored; never commit it)
notebooks/  Reproducible exploratory and final Kaggle analyses
src/        Reusable loading, feature, outcome, and modeling code
```

## Data and references

- [Competition overview and data](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027)
- [Project proposal](docs/project-proposal.md)
- [Initial requirements analysis](docs/initial-requirements.md)
- [Dataset guide](docs/data.md)
- [Initial data inventory](docs/data-inventory.md)

Competition data is downloaded separately from Kaggle. Do not commit downloaded
data, Kaggle credentials, generated submissions, or other large artifacts.

## Getting started

1. Join the competition and accept its rules on Kaggle, then download and
   extract its nine CSV files into `data/`. Alternatively, authenticate with
   Kaggle and use `kagglehub.competition_download("nfl-big-data-bowl-2027")`;
   set `NFL_DATA_DIR` to the returned directory. Never share or commit tokens.
2. Create a Python virtual environment, install dependencies, and run Jupyter:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   jupyter lab
   ```

3. Open `notebooks/00_data_inventory.ipynb` and run all cells. With files outside
   `data/`, set `NFL_DATA_DIR` before launching Jupyter:

   ```bash
   export NFL_DATA_DIR=/path/to/competition-csvs
   jupyter lab
   ```

Run the small synthetic-data tests with `python -m pytest -q`. The inventory
reports candidate YAC coverage, not a validated final reception definition.
