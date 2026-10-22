"""Load and inspect the competition files without assuming a local data path."""

from pathlib import Path

import pandas as pd


FILES = (
    "players.csv", "combine_results.csv", "combine_tracking.csv",
    "player_career_successes.csv", "player_play.csv", "games.csv",
    "game_tracking_2023.csv", "game_tracking_2024.csv", "game_tracking_2025.csv",
)

# Only columns used by the initial inventory are required here; this is not a
# complete schema and should not be mistaken for the final analytical contract.
REQUIRED_COLUMNS = {
    "players.csv": ("nfl_id", "nfl_position", "draft_year"),
    "combine_results.csv": ("nfl_id", "draft_year"),
    "combine_tracking.csv": ("nfl_id", "entity_type", "draft_year", "event_id", "drill_type"),
    "player_play.csv": ("nfl_id", "game_id", "play_id", "pass_result", "rec_yards", "yards_after_catch", "play_nullified_by_penalty"),
    "games.csv": ("game_id", "season", "season_type"),
    "player_career_successes.csv": ("nfl_id",),
    "game_tracking_2023.csv": ("game_id", "play_id", "nfl_id"),
    "game_tracking_2024.csv": ("game_id", "play_id", "nfl_id"),
    "game_tracking_2025.csv": ("game_id", "play_id", "nfl_id"),
}
ID_COLUMNS = {"nfl_id", "game_id", "play_id", "event_id"}


def csv_path(data_dir, filename):
    """Resolve a file in the caller-supplied data directory with a clear error."""
    path = Path(data_dir).expanduser() / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing competition file: {path}. See README for data setup.")
    return path


def columns_for(data_dir, filename):
    """Read a header and check the fields needed for this inventory."""
    path = csv_path(data_dir, filename)
    columns = list(pd.read_csv(path, nrows=0).columns)
    missing = sorted(set(REQUIRED_COLUMNS.get(filename, ())) - set(columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")
    return columns


def read_columns(data_dir, filename, columns):
    """Load selected fields only, preserving identifiers as strings."""
    available = columns_for(data_dir, filename)
    missing = sorted(set(columns) - set(available))
    if missing:
        raise ValueError(f"{filename} is missing requested columns: {', '.join(missing)}")
    return pd.read_csv(csv_path(data_dir, filename), usecols=list(columns),
                       dtype={c: "string" for c in columns if c in ID_COLUMNS})


def file_inventory(data_dir, filenames=FILES, chunksize=200_000):
    """Count CSV rows in bounded memory and record headers and file sizes.

    This scans all requested files, including large game-tracking CSVs. It reads
    just one column from each file; it does not load all tracking frames at once.
    """
    records = []
    for name in filenames:
        columns = columns_for(data_dir, name)
        path = csv_path(data_dir, name)
        count = sum(len(chunk) for chunk in pd.read_csv(path, usecols=[columns[0]], chunksize=chunksize))
        records.append({"file": name, "rows": count, "columns": len(columns),
                        "size_mb": round(path.stat().st_size / 1_000_000, 2),
                        "fields": ", ".join(columns)})
    return pd.DataFrame(records)


def _duplicate_count(frame, keys):
    """Count rows in duplicate key groups, excluding rows with missing keys."""
    valid = frame.dropna(subset=list(keys))
    return int(valid.duplicated(list(keys), keep=False).sum())


def _require_unique(frame, keys, name):
    duplicates = _duplicate_count(frame, keys)
    if duplicates:
        raise ValueError(f"{name} has {duplicates} rows in duplicate {', '.join(keys)} groups; investigate before joining.")


def _player_tracking_ids(data_dir, chunksize):
    name = "combine_tracking.csv"
    columns_for(data_dir, name)
    ids = set()
    missing_ids = 0
    player_rows = 0
    drills = set()
    for chunk in pd.read_csv(csv_path(data_dir, name), usecols=["nfl_id", "entity_type", "drill_type"],
                             dtype={"nfl_id": "string"}, chunksize=chunksize):
        player = chunk[chunk["entity_type"].eq("PLAYER")]
        player_rows += len(player)
        missing_ids += int(player["nfl_id"].isna().sum())
        ids.update(player["nfl_id"].dropna().tolist())
        drills.update(player["drill_type"].dropna().tolist())
    return ids, player_rows, missing_ids, sorted(drills)


def coverage_report(data_dir, chunksize=200_000):
    """Build an exploratory WR overlap report, not a final modeling sample.

    Candidate receptions use completed plays, non-null receiver yards and YAC,
    non-nullified plays, and regular-season games. These are provisional data
    checks, not a validated definition of a reception or analytical window.
    """
    players = read_columns(data_dir, "players.csv", REQUIRED_COLUMNS["players.csv"])
    traditional = ("forty", "ten_yd_split", "vertical", "broad_jump", "three_cone", "short_shuttle", "combine_height", "combine_weight")
    combine_available = columns_for(data_dir, "combine_results.csv")
    combine = read_columns(data_dir, "combine_results.csv", (*REQUIRED_COLUMNS["combine_results.csv"],
                           *(column for column in traditional if column in combine_available)))
    plays = read_columns(data_dir, "player_play.csv", REQUIRED_COLUMNS["player_play.csv"])
    games = read_columns(data_dir, "games.csv", REQUIRED_COLUMNS["games.csv"])
    _require_unique(players, ["nfl_id"], "players.csv")
    _require_unique(games, ["game_id"], "games.csv")

    wr = players.loc[players["nfl_position"].eq("WR") & players["nfl_id"].notna()].copy()
    wr_ids = set(wr["nfl_id"])
    all_player_ids = set(players["nfl_id"].dropna())
    tracking_ids, tracking_rows, tracking_missing, drills = _player_tracking_ids(data_dir, chunksize)
    combine_ids = set(combine["nfl_id"].dropna())
    # Pandas matches null keys to null keys; exclude missing game IDs on the
    # dimension side so they remain unmatched instead of acquiring a season.
    matched_games = plays.merge(games.dropna(subset=["game_id"]), on="game_id", how="left",
                                validate="many_to_one", indicator=True)
    # Missing penalties are not silently treated as valid plays. No catch or
    # player attribution is considered confirmed without a source-record review.
    candidates = matched_games[
        matched_games["nfl_id"].isin(wr_ids)
        & matched_games["season_type"].eq("REG")
        & matched_games["pass_result"].eq("C")
        & matched_games["rec_yards"].notna()
        & matched_games["yards_after_catch"].notna()
        & matched_games["play_nullified_by_penalty"].eq("N")
    ]
    yac_ids = set(candidates["nfl_id"].dropna())
    wr["has_combine_results"] = wr["nfl_id"].isin(combine_ids)
    wr["has_player_tracking"] = wr["nfl_id"].isin(tracking_ids)
    wr["has_candidate_yac"] = wr["nfl_id"].isin(yac_ids)
    wr["tracking_and_candidate_yac"] = wr["has_player_tracking"] & wr["has_candidate_yac"]

    summary = pd.DataFrame([
        {"measure": "Players with an ID", "count": int(players["nfl_id"].notna().sum())},
        {"measure": "WR with an ID", "count": len(wr)},
        {"measure": "WR with Combine results", "count": int(wr["has_combine_results"].sum())},
        {"measure": "WR with PLAYER Combine tracking", "count": int(wr["has_player_tracking"].sum())},
        {"measure": "WR with candidate regular-season YAC", "count": int(wr["has_candidate_yac"].sum())},
        {"measure": "WR with tracking and candidate YAC", "count": int(wr["tracking_and_candidate_yac"].sum())},
        {"measure": "Candidate receiving rows (unvalidated)", "count": len(candidates)},
    ])
    diagnostics = pd.DataFrame([
        {"check": "players: missing nfl_id", "count": int(players["nfl_id"].isna().sum())},
        {"check": "players: rows in duplicate nfl_id groups", "count": _duplicate_count(players, ["nfl_id"])},
        {"check": "combine results: missing nfl_id", "count": int(combine["nfl_id"].isna().sum())},
        {"check": "combine results: unique IDs absent from players", "count": len(combine_ids - all_player_ids)},
        {"check": "combine results: rows in duplicate nfl_id + draft_year groups", "count": _duplicate_count(combine, ["nfl_id", "draft_year"])},
        {"check": "PLAYER tracking rows", "count": tracking_rows},
        {"check": "PLAYER tracking: missing nfl_id", "count": tracking_missing},
        {"check": "PLAYER tracking: unique IDs absent from players", "count": len(tracking_ids - all_player_ids)},
        {"check": "player plays: missing nfl_id", "count": int(plays["nfl_id"].isna().sum())},
        {"check": "player plays: unique IDs absent from players", "count": len(set(plays["nfl_id"].dropna()) - all_player_ids)},
        {"check": "player plays: missing YAC", "count": int(plays["yards_after_catch"].isna().sum())},
        {"check": "games: missing game_id", "count": int(games["game_id"].isna().sum())},
        {"check": "player plays: rows in duplicate game_id + play_id + nfl_id groups", "count": _duplicate_count(plays, ["game_id", "play_id", "nfl_id"])},
        {"check": "player plays: unmatched or missing game_id", "count": int(matched_games["_merge"].eq("left_only").sum())},
    ])
    by_year = (wr.groupby("draft_year", dropna=False)
               .agg(wr_players=("nfl_id", "size"),
                    combine_results=("has_combine_results", "sum"),
                    player_tracking=("has_player_tracking", "sum"),
                    candidate_yac=("has_candidate_yac", "sum"),
                    tracking_and_candidate_yac=("tracking_and_candidate_yac", "sum"))
               .reset_index())
    wr_combine = combine[combine["nfl_id"].isin(wr_ids)]
    missingness = pd.DataFrame([
        {"field": col, "available": col in wr_combine.columns,
         "wr_result_rows": len(wr_combine),
         "missing_rows": int(wr_combine[col].isna().sum()) if col in wr_combine.columns else None}
        for col in traditional
    ])
    return {"summary": summary, "by_draft_year": by_year, "diagnostics": diagnostics,
            "traditional_missingness": missingness,
            "game_periods": games.groupby(["season", "season_type"], dropna=False).size().reset_index(name="games"),
            "tracking_drill_types": drills, "wr_coverage": wr}
