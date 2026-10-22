from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nfl_bdb.data import columns_for, coverage_report, file_inventory, read_columns


@pytest.fixture
def sample_data(tmp_path):
    tables = {
        "players.csv": [
            {"nfl_id": 1, "nfl_position": "WR", "draft_year": 2023},
            {"nfl_id": 2, "nfl_position": "WR", "draft_year": 2024},
            {"nfl_id": 3, "nfl_position": "WR", "draft_year": 2024},
            {"nfl_id": 4, "nfl_position": "TE", "draft_year": 2024},
        ],
        "combine_results.csv": [
            {"nfl_id": 1, "draft_year": 2023}, {"nfl_id": 2, "draft_year": 2024},
        ],
        "combine_tracking.csv": [
            {"nfl_id": 1, "entity_type": "PLAYER", "draft_year": 2023, "event_id": 10, "drill_type": "FORTY"},
            {"nfl_id": 1, "entity_type": "PLAYER", "draft_year": 2023, "event_id": 10, "drill_type": "FORTY"},
            {"nfl_id": 2, "entity_type": "BALL", "draft_year": 2024, "event_id": 11, "drill_type": "WR"},
            {"nfl_id": 3, "entity_type": "PLAYER", "draft_year": 2024, "event_id": 12, "drill_type": "WR"},
        ],
        "games.csv": [
            {"game_id": 100, "season": 2023, "season_type": "REG"},
            {"game_id": 101, "season": 2024, "season_type": "POST"},
        ],
        "player_play.csv": [
            {"nfl_id": 1, "game_id": 100, "play_id": 1, "pass_result": "C", "rec_yards": 10, "yards_after_catch": 5, "play_nullified_by_penalty": "N"},
            {"nfl_id": 2, "game_id": 100, "play_id": 2, "pass_result": "C", "rec_yards": 0, "yards_after_catch": 0, "play_nullified_by_penalty": "N"},
            {"nfl_id": 3, "game_id": 101, "play_id": 3, "pass_result": "C", "rec_yards": 10, "yards_after_catch": 5, "play_nullified_by_penalty": "N"},
            {"nfl_id": 3, "game_id": 999, "play_id": 4, "pass_result": "C", "rec_yards": 10, "yards_after_catch": 5, "play_nullified_by_penalty": "N"},
            {"nfl_id": 3, "game_id": 100, "play_id": 5, "pass_result": "C", "rec_yards": 10, "yards_after_catch": None, "play_nullified_by_penalty": "N"},
            {"nfl_id": 4, "game_id": 100, "play_id": 6, "pass_result": "C", "rec_yards": 10, "yards_after_catch": 5, "play_nullified_by_penalty": "N"},
        ],
    }
    for row in tables["player_play.csv"]:
        row["target"] = True
    for filename, rows in tables.items():
        pd.DataFrame(rows).to_csv(tmp_path / filename, index=False)
    return tmp_path


def test_missing_file_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="players.csv"):
        columns_for(tmp_path, "players.csv")


def test_missing_column_error(tmp_path):
    pd.DataFrame({"nfl_id": [1]}).to_csv(tmp_path / "players.csv", index=False)
    with pytest.raises(ValueError, match="nfl_position"):
        columns_for(tmp_path, "players.csv")


def test_inventory_counts_rows_in_chunks(sample_data):
    inventory = file_inventory(sample_data, ["players.csv", "combine_tracking.csv"], chunksize=2)
    assert inventory.set_index("file")["rows"].to_dict() == {"players.csv": 4, "combine_tracking.csv": 4}
    assert read_columns(sample_data, "players.csv", ["nfl_id"])["nfl_id"].iloc[0] == "1"


def test_coverage_excludes_ball_missing_yac_and_postseason(sample_data):
    report = coverage_report(sample_data, chunksize=2)
    summary = report["summary"].set_index("measure")["count"]
    assert summary["WR with an ID"] == 3
    assert summary["WR with PLAYER Combine tracking"] == 2
    assert summary["WR with candidate regular-season YAC"] == 2
    assert summary["WR with tracking and candidate YAC"] == 1
    assert summary["Candidate receiving rows (unvalidated)"] == 2  # zero YAC is valid, missing is not
    diagnostics = report["diagnostics"].set_index("check")["count"]
    assert diagnostics["player plays: unmatched or missing game_id"] == 1


def test_duplicate_player_keys_fail_before_join(sample_data):
    path = sample_data / "players.csv"
    players = pd.read_csv(path)
    pd.concat([players, players.iloc[[0]]]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="duplicate nfl_id"):
        coverage_report(sample_data)


def test_duplicate_game_keys_fail_before_join(sample_data):
    path = sample_data / "games.csv"
    games = pd.read_csv(path)
    pd.concat([games, games.iloc[[0]]]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="duplicate game_id"):
        coverage_report(sample_data)


def test_missing_game_id_never_matches_missing_game_key(sample_data):
    games_path = sample_data / "games.csv"
    plays_path = sample_data / "player_play.csv"
    games = pd.read_csv(games_path)
    games.loc[len(games)] = [None, 2024, "REG"]
    games.to_csv(games_path, index=False)
    plays = pd.read_csv(plays_path)
    plays.loc[len(plays)] = [3, None, 7, "C", 10, 5, "N", True]
    plays.to_csv(plays_path, index=False)
    report = coverage_report(sample_data)
    diagnostics = report["diagnostics"].set_index("check")["count"]
    assert diagnostics["player plays: unmatched or missing game_id"] == 2
    assert report["summary"].set_index("measure").loc["WR with candidate regular-season YAC", "count"] == 2


def test_flags_candidate_that_was_not_the_target(sample_data):
    path = sample_data / "player_play.csv"
    plays = pd.read_csv(path)
    plays.loc[0, "target"] = False
    plays.to_csv(path, index=False)
    report = coverage_report(sample_data, chunksize=2)
    diagnostic = report["diagnostics"].set_index("check")["count"]
    summary = report["summary"].set_index("measure")["count"]
    assert diagnostic["candidate rows marked target=False"] == 1
    assert summary["Candidate receiving rows (unvalidated)"] == 2
    assert summary["Candidate rows marked target=True (unvalidated)"] == 1
    drills = report["wr_drill_coverage"].set_index("drill_type")
    assert drills.loc["FORTY", "wr_players"] == 1
    assert drills.loc["FORTY", "event_ids"] == 1  # repeated frames are one event


def test_notebook_runs_end_to_end_with_synthetic_data(sample_data, monkeypatch):
    import nbformat
    from nbclient import NotebookClient

    pd.DataFrame({"nfl_id": [1]}).to_csv(sample_data / "player_career_successes.csv", index=False)
    for year in (2023, 2024, 2025):
        pd.DataFrame({"game_id": [100], "play_id": [1], "nfl_id": [1]}).to_csv(
            sample_data / f"game_tracking_{year}.csv", index=False)
    monkeypatch.setenv("NFL_DATA_DIR", str(sample_data))
    root = Path(__file__).resolve().parents[1]
    notebook = nbformat.read(root / "notebooks" / "00_data_inventory.ipynb", as_version=4)
    nbformat.validate(notebook)
    result = NotebookClient(notebook, timeout=120, kernel_name="python3",
                            resources={"metadata": {"path": str(root)}}).execute()
    assert all(output.output_type != "error" for cell in result.cells
               for output in cell.get("outputs", []))
