# Data dictionary

This document defines the source fields and the validated wide-receiver cohort
used by the project. The nine competition CSV files remain local and unchanged.
Generated tables must be reproducible from committed code. The small validated
WR-cohort CSV is versioned as a project deliverable; raw competition files are
never committed.

## Identifiers and table grain

| Field | Meaning | Use |
| --- | --- | --- |
| `nfl_id` | Stable player identifier | Joins players, Combine results, Combine tracking and player-play records |
| `game_id` | NFL game identifier | Joins `player_play.csv` to `games.csv` |
| `play_id` | Play identifier within a game | Used with `game_id` and `nfl_id` to identify a player-play row |
| `event_id` | Combine drill-attempt identifier | Separates tracking frames from different attempts |
| `draft_year` | Player's draft class | Defines the 2023-2025 project cohort |
| `season` | NFL season | Defines the game-performance observation window |

Identifiers are read as strings so leading zeros or large numeric values cannot
be changed by numeric conversion. The expected key of the clean player table is
`nfl_id`. The expected player-play key is (`game_id`, `play_id`, `nfl_id`).

## Source files used by the project

| File | Grain | Fields currently used | Purpose |
| --- | --- | --- | --- |
| `players.csv` | One row per player | `nfl_id`, `nfl_position`, `draft_year` | Player identity and WR cohort selection |
| `combine_results.csv` | One row per player | `nfl_id`, `draft_year`; traditional Combine measurements when present | Traditional-feature coverage and modeling |
| `combine_tracking.csv` | One entity frame per drill attempt and time | `nfl_id`, `entity_type`, `draft_year`, `event_id`, `drill_type` | PLAYER tracking coverage; later movement features |
| `player_play.csv` | One player in one play | `nfl_id`, `game_id`, `play_id`, `target`, `pass_result`, `rec_yards`, `yards_after_catch`, `play_nullified_by_penalty` | Provisional reception and YAC outcomes |
| `games.csv` | One row per game | `game_id`, `season`, `season_type` | Regular-season and year filtering |
| `player_career_successes.csv` | One row per player | `nfl_id` | Supplied career outcomes; not used in the clean WR cohort |
| `game_tracking_2023.csv` | One entity frame per play and time | `game_id`, `play_id`, `nfl_id` | 2023 game-tracking coverage |
| `game_tracking_2024.csv` | One entity frame per play and time | `game_id`, `play_id`, `nfl_id` | 2024 game-tracking coverage |
| `game_tracking_2025.csv` | One entity frame per play and time | `game_id`, `play_id`, `nfl_id` | 2025 game-tracking coverage |

This is a project dictionary, not a replacement for the official competition
schema. A column's physical unit or statistical meaning must be confirmed before
it is used as an analytical feature.

## Clean wide-receiver cohort

Run `python -m nfl_bdb.players` as documented in the root README to generate
`data/processed/clean_wr_players.csv`. The output has one row per player.

| Column | Type | Definition |
| --- | --- | --- |
| `nfl_id` | string | Unique WR identifier |
| `display_name` | string | Official player display name |
| `nfl_position` | string | Must equal `WR` |
| `draft_year` | integer-like | Must be one of 2023, 2024 or 2025 |
| `birth_date` | date-like string | Player birth date supplied by the competition |
| `college_name` | string | Player's college |
| `college_conference` | string | Player's college conference |
| `draft_round` | nullable integer-like | NFL draft round; missing for undrafted players |
| `draft_pick_within_round` | nullable integer-like | Pick within the draft round |
| `draft_overall_pick` | nullable integer-like | Overall draft pick |
| `has_combine_results` | boolean | A unique matching row exists in `combine_results.csv` |
| `has_player_tracking` | boolean | At least one matching `entity_type == PLAYER` frame exists in Combine tracking |

The cohort builder fails when player IDs are duplicated, Combine IDs do not
exist in the player table, or the player and Combine files disagree on draft
year. A tracking-presence flag does not prove that a complete or valid drill
attempt exists.

For the competition snapshot inventoried on October 21, 2026, the reproducible
control totals are 38 WRs from the 2023 draft class, 31 from 2024 and 37 from
2025, for 106 unique WRs in total. All 106 had a Combine-results row and at least
one PLAYER Combine-tracking row. A mismatch should be investigated rather than
silently accepted.

## Cohort-builder complexity

Let `P` be the number of player rows, `C` the number of Combine-result rows,
`T` the number of Combine-tracking rows, `B` the tracking chunk size and `W` the
number of retained WRs. Player and Combine key checks take `O(P + C)` time. The
chunked tracking scan takes `O(T)` time. Hash-set membership used for coverage
flags is expected `O(W)` time, and sorting the final cohort takes
`O(W log W)` time. The total is therefore `O(P + C + T + W log W)`, dominated by
the tracking scan for this dataset.

The CSV scan holds at most one chunk plus identifier and drill-coverage sets,
instead of loading every tracking frame at once. Working memory is therefore
bounded by the small player/Combine tables, the retained identifiers and event
coverage, and `O(B)` frame rows. The generated output itself uses `O(W)` space.

## Missing-value and exclusion rules

- Missing IDs are never used as join keys.
- Missing measurements are never replaced with zero during data preparation.
- Zero and negative YAC can be valid outcomes and must not be removed solely
  because of their sign.
- Reception filtering and YAC calculation are separate from player-cohort
  preparation and must preserve exclusion counts.
- Raw competition files are read-only inputs. Generated outputs are local and
  reproducible from committed code.
