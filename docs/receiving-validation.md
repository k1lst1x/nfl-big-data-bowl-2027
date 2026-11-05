# Receiving validation snapshot — November 4, 2026

This is a provisional data audit, not an association or prediction result.
Local checkout started clean at `286825c`. GitHub HEAD was `0075792`
([Document initial dataset coverage](https://github.com/k1lst1x/nfl-big-data-bowl-2027/commit/0075792ada9cf5d7dbbd6f2195c276797e3ec82c)),
a direct child of that commit. Its code changes and inventory report were
inspected without merging or changing local history. This audit agrees with its
WR counts and extends validation to other positions and player-season outcomes.
No AGENTS.md instructions were found under the project parent.

## Inputs and joins

All nine CSVs were found in `../RawData` relative to the repository. The raw
files remain outside this repository. Header checks and bounded-memory row
counts succeeded for all files. Full headers are in the local
`outputs/receiving_audit/file_inventory.csv`.

| File | Rows | Columns |
| --- | ---: | ---: |
| players | 510 | 10 |
| combine_results | 510 | 18 |
| combine_tracking | 463,189 | 14 |
| player_career_successes | 510 | 9 |
| player_play | 314,197 | 64 |
| games | 1,002 | 7 |
| game_tracking_2023 | 3,665,443 | 12 |
| game_tracking_2024 | 7,827,944 | 12 |
| game_tracking_2025 | 11,160,903 | 12 |

`nfl_id` joins players, Combine results, Combine PLAYER tracking and player-play
records; `game_id` joins player plays to games; player-play grain is
`game_id, play_id, nfl_id`. IDs are read as strings. No missing player-play keys,
duplicate player-play keys, unmatched player/game rows, duplicate player or game
IDs, duplicate Combine player IDs, or Combine/player draft-year disagreements
were found. All 106 WRs have Combine results and PLAYER Combine tracking;
tracking presence does not establish a valid attempt for a proposed metric.
Games contain 272 REG, 49 PRE and 13 POST games per season in 2023–2025.
Tracking files were counted one selected column at a time in chunks; game
tracking events, per-player coverage and trajectories have not been audited.

## Outcome and sample

The actual player-play header includes `yards_after_catch`, `rec_yards`, `target`,
`pass_result`, and `play_nullified_by_penalty`. A supplied YAC field exists;
tracking-based derivation is unnecessary for this first audit. Its units and
statistical semantics still need confirmation from the official dictionary.

Candidate rule: complete keys, matched player and game, REG, pass_result C,
target TRUE, penalty flag N, finite receiving yards and YAC. Zero and negative
YAC are retained. No missing outcome is replaced with zero. This leaves 5,041
rows across all positions (4,032 WR, 1,005 TE, four at other positions).
Four of the original 6,260 nonmissing YAC rows have target FALSE; all four play
descriptions contain laterals, including two WR cases. These are exported for
review rather than counted as receptions. Filtering targets alone does not
validate statistical attribution for all remaining plays.

| Position | All players | With candidate receptions | Player-season rows | At least 10 / 20 / 30 candidate receptions |
| --- | ---: | ---: | ---: | --- |
| WR | 106 | 78 | 142 | 59 / 45 / 39 |
| TE | 42 | 28 | 54 | 21 / 15 / 13 |

Thresholds count receptions across the supplied regular seasons per player,
not per season. No final minimum is imposed: the audit retains one or more
candidate receptions to expose coverage. A final cutoff needs a precision and
sensitivity analysis; 20 or 30 is not automatically defensible, especially for
TEs. The output keeps reception counts to support that decision. Cohorts have
unequal observation windows; a common rookie-season window is a useful next
sensitivity analysis. No modeling should treat player-season rows as independent
players or split a player across training and testing.

Available finite traditional measurements among players with candidate receptions:

| Measurement | WR usable / 78 | TE usable / 28 |
| --- | ---: | ---: |
| Forty / 10-yard split | 71 / 71 | 25 / 25 |
| Vertical | 68 | 24 |
| Broad jump | 69 | 23 |
| Three-cone | 24 | 11 |
| Short shuttle | 30 | 12 |
| Height / weight | 78 / 78 | 28 / 28 |
| Bench reps | 22 | 7 |

Usable here means finite numeric value, not physically validated. Complete-case
agility models would lose substantial data. Missingness and threshold tables
are exported for every observed position. The provisional player-season table
includes candidate reception counts, total YAC, total/count YAC per reception,
position, draft year and available Combine metrics. These are local artifacts.

## Physics and competition gaps

In the first 10,000 Combine tracking rows, all 9,837 within-event/player time
differences were 0.1 seconds. This supports 10 Hz for that sample only. The
sample contains x, y, s, a, dis and dir, but headers and numerical ranges cannot
confirm units or angle conventions. Before computing acceleration or cuts,
confirm units, entity and attempt boundaries, time ordering, gaps, direction
wrapping, sensor noise, and speed versus coordinate displacement. Do not label
`s` as mph or m/s or assume `a` is signed tangential acceleration yet.

The [official NFL overview](https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl/)
confirms the 2027 objective links Combine traits to later NFL performance and
includes WR/TE groups. That makes this question relevant. Official Kaggle
[data](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/data) and
[evaluation](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/overview/evaluation)
pages returned no readable content during verification. Exact submission
requirements, scoring weights, tracking-use requirements and dictionary units
remain unverified; the course proposal must not be described as competition
compliant yet. Recheck the official pages before finalizing scope or submission.

Next: review reception attribution with the outcome lead, confirm units and
complete drill attempts with the physics/feature leads, then choose observation
windows and thresholds. Only afterward explore WR and TE associations separately
and compare a position/context baseline against added Combine features using
identical samples and player-grouped splits; fit preprocessing on training data.

## Reproduction

From the repository, with dependencies installed:

```bash
export NFL_DATA_DIR=../RawData
PYTHONPATH=src .venv/bin/python -m nfl_bdb.receiving \
  --data-dir "$NFL_DATA_DIR" --output-dir outputs/receiving_audit
.venv/bin/python -m pytest -q
```

Run the existing inventory notebook with NFL_DATA_DIR set to an absolute path
if starting Jupyter from another directory. Generated audit tables are ignored
under outputs/. No data, changes, or commits were pushed.
