# Initial data inventory

Exploratory snapshot from the nine competition CSVs supplied to the team,
run on October 21, 2026. Reproduce it with `notebooks/00_data_inventory.ipynb`.
The source data and executed notebook outputs remain local; this document reports
aggregate counts only. These are coverage checks, not final model results.

## Files and identity checks

| File | Rows |
| --- | ---: |
| `players.csv` | 510 |
| `combine_results.csv` | 510 |
| `combine_tracking.csv` | 463,189 |
| `player_career_successes.csv` | 510 |
| `player_play.csv` | 314,197 |
| `games.csv` | 1,002 |
| `game_tracking_2023.csv` | 3,665,443 |
| `game_tracking_2024.csv` | 7,827,944 |
| `game_tracking_2025.csv` | 11,160,903 |

The initial checks found no missing or duplicated player identifiers in
`players.csv`, no duplicate `nfl_id` / `draft_year` keys in Combine results, no
duplicate `game_id` / `play_id` / `nfl_id` keys in player plays, and no player
plays with an unmatched `game_id`. The games file includes preseason, regular
season, and postseason; the preliminary outcome coverage uses regular season.

## Wide-receiver coverage

| Draft year | WRs | With PLAYER Combine tracking | With candidate YAC rows |
| --- | ---: | ---: | ---: |
| 2023 | 38 | 38 | 30 |
| 2024 | 31 | 31 | 27 |
| 2025 | 37 | 37 | 21 |
| **Total** | **106** | **106** | **78** |

All 106 WRs also appear in `combine_results.csv`. Having a PLAYER tracking row
does not by itself confirm that a usable attempt exists for every planned trait.

The initial filter finds 4,034 candidate rows across the 78 WRs: regular-season
completed passes, non-null `rec_yards` and `yards_after_catch`, and a play not
nullified by penalty. **This is not a validated reception definition.** Two
candidate rows have `target=False`; their play descriptions describe laterals
after another player's catch. The other 4,032 have `target=True`. The team must
review the target flag and source plays before defining the final outcome; simply
filtering on target should not be assumed to solve all attribution cases.

Candidate-row count thresholds illustrate sample sensitivity; they are not
recommended final cutoffs:

| Minimum candidate rows per WR | Players |
| ---: | ---: |
| 1 | 78 |
| 5 | 66 |
| 10 | 59 |
| 20 | 45 |
| 30 | 39 |
| 50 | 29 |
| 100 | 11 |

## Drill and traditional-test coverage

Distinct WR players with at least one `PLAYER` frame in each drill category:

| Drill category | WRs | Distinct event IDs |
| --- | ---: | ---: |
| `SKILL_DRILLS_WR` | 106 | 1,513 |
| `FORTY_YARD_DASH` | 93 | 174 |
| `SHORT_SHUTTLE` | 29 | 36 |
| `THREE_CONE_DRILL` | 24 | 30 |

Coverage does not establish that every event is complete or suitable for a
specific feature. Of 106 WR Combine-result rows, 10 lack 40-yard times, 68 lack
short-shuttle times, and 74 lack three-cone times. Missingness may considerably
reduce a complete-case comparison; inspect missingness on the final eligible
sample and avoid making modeling decisions from these totals alone.

## Next checks

- Review reception attribution, laterals, penalty handling, and sampled source
  plays with the NFL performance and outcome lead.
- Examine valid drill attempts, frame timing, and feature coverage with the
  Combine and movement leads.
- Agree on an observation window and candidate reception thresholds before
  comparing outcomes or models. Different cohorts have unequal NFL exposure.
- Recalculate all coverage after those rules are validated; group model splits
  by player and report uncertainty.
