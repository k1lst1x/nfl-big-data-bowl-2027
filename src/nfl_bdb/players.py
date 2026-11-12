"""Build the validated wide-receiver cohort used by downstream analyses."""

import argparse
from pathlib import Path

import pandas as pd

from nfl_bdb.data import (
    _player_tracking_ids,
    _require_unique,
    columns_for,
    read_columns,
)


DEFAULT_DRAFT_YEARS = (2023, 2024, 2025)


def build_wr_cohort(data_dir, draft_years=DEFAULT_DRAFT_YEARS, chunksize=200_000):
    """Return one validated row per WR in the requested draft classes.

    The cohort records whether each player has a Combine-results row and at
    least one PLAYER row in Combine tracking. It does not filter on receptions
    or YAC; outcome eligibility belongs to the receiving-outcome pipeline.
    """
    player_columns = columns_for(data_dir, "players.csv")
    required_player_columns = {"nfl_id", "nfl_position", "draft_year"}
    missing_player_columns = required_player_columns - set(player_columns)
    if missing_player_columns:
        raise ValueError(
            "players.csv is missing required columns: "
            f"{sorted(missing_player_columns)}"
        )
    players = pd.read_csv(
        Path(data_dir) / "players.csv", dtype={"nfl_id": "string"}
    )
    combine = read_columns(
        data_dir, "combine_results.csv", ["nfl_id", "draft_year"]
    )
    _require_unique(players, ["nfl_id"], "players.csv")
    _require_unique(combine, ["nfl_id"], "combine_results.csv")

    player_ids = set(players["nfl_id"].dropna())
    combine_ids = set(combine["nfl_id"].dropna())
    unknown_combine_ids = combine_ids - player_ids
    if unknown_combine_ids:
        raise ValueError(
            "combine_results.csv contains nfl_id values absent from players.csv: "
            f"{len(unknown_combine_ids)}"
        )

    year_check = players[["nfl_id", "draft_year"]].merge(
        combine[["nfl_id", "draft_year"]],
        on="nfl_id",
        how="inner",
        suffixes=("_players", "_combine"),
        validate="one_to_one",
    )
    disagreements = year_check[
        year_check["draft_year_players"].ne(year_check["draft_year_combine"])
    ]
    if not disagreements.empty:
        raise ValueError(
            "players.csv and combine_results.csv disagree on draft_year for "
            f"{len(disagreements)} nfl_id values"
        )

    requested_years = tuple(draft_years)
    cohort = players[
        players["nfl_position"].eq("WR")
        & players["draft_year"].isin(requested_years)
        & players["nfl_id"].notna()
    ].copy()
    tracking_ids, _, _, _, _ = _player_tracking_ids(
        data_dir, chunksize, set(cohort["nfl_id"])
    )
    cohort["has_combine_results"] = cohort["nfl_id"].isin(combine_ids)
    cohort["has_player_tracking"] = cohort["nfl_id"].isin(tracking_ids)
    cohort = cohort.sort_values(["draft_year", "nfl_id"]).reset_index(drop=True)

    if cohort["nfl_id"].duplicated().any():
        raise ValueError("clean WR cohort must contain one row per nfl_id")
    return cohort


def cohort_summary(cohort):
    """Summarize the exported cohort by draft class for reproducibility checks."""
    return (
        cohort.groupby("draft_year", dropna=False)
        .agg(
            wr_players=("nfl_id", "size"),
            with_combine_results=("has_combine_results", "sum"),
            with_player_tracking=("has_player_tracking", "sum"),
        )
        .reset_index()
    )


def write_wr_cohort(data_dir, output, draft_years=DEFAULT_DRAFT_YEARS, chunksize=200_000):
    """Build the cohort and write it to a local, caller-selected CSV path."""
    cohort = build_wr_cohort(data_dir, draft_years, chunksize)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(output, index=False)
    return cohort


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument(
        "--output",
        default="data/processed/clean_wr_players.csv",
        help="Output path for the reproducible WR-cohort CSV",
    )
    parser.add_argument(
        "--draft-years", nargs="+", type=int, default=list(DEFAULT_DRAFT_YEARS)
    )
    args = parser.parse_args()

    output = Path(args.output)
    cohort = write_wr_cohort(args.data_dir, output, args.draft_years)
    print(cohort_summary(cohort).to_string(index=False))
    print(f"Wrote {len(cohort)} unique WR rows to {output}")


if __name__ == "__main__":
    main()
