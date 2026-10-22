# NFL Big Data Bowl 2027 dataset guide

The competition provides nine CSV files, approximately 2.2 GiB in total, for
510 prospects who entered the NFL between 2023 and 2025. Local data belong under
`data/` and are intentionally excluded from version control.

## Core tables

| File | Role in this project | Key fields |
| --- | --- | --- |
| `players.csv` | Player identity and WR eligibility | `nfl_id`, `draft_year`, `nfl_position`, draft metadata |
| `combine_results.csv` | Traditional Combine features | `nfl_id`, `forty`, `ten_yd_split`, jumps, agility tests, height, weight |
| `combine_tracking.csv` | 10 Hz drill movement data | `event_id`, `nfl_id`, `drill_type`, `drill_name`, `attempt`, `time`, `x`, `y`, `s`, `a`, `dir` |
| `player_play.csv` | Reception-level YAC and football context | `nfl_id`, `game_id`, `play_id`, `yards_after_catch`, `rec_yards`, `route_ran`, `separation_at_pass_forward` |
| `games.csv` | Season and game filtering | `game_id`, `season`, `season_type`, `week` |

The game-tracking files are available for 2023, 2024, and 2025. They are not a
required input for the initial YAC outcome because `player_play.csv` supplies
`yards_after_catch`; they may be used later only for a documented validation or
context analysis.

The competition lists the data license as CC BY-NC 4.0. Download the files from
the competition page under the applicable rules; do not commit raw data to this
repository.

## Initial inventory

Run `notebooks/00_data_inventory.ipynb` after acquiring the files. It checks
schemas, row counts, selected missing values, duplicate keys, game periods, and
WR overlap. The YAC coverage check uses a provisional candidate filter, not a
validated reception definition. Tracking coverage includes `PLAYER` rows only.
The notebook scans large files in chunks, so the full inventory can take time.

## Join and sample rules

1. Use `nfl_id` as the player key between player, Combine-result, Combine-tracking,
   and player-play tables.
2. Restrict the primary analysis to players whose `nfl_position` is `WR`.
3. Define valid receptions and the NFL observation window before estimating
   relationships or comparing models.
4. Compute a player's average YAC as total valid `yards_after_catch` divided by
   valid reception count; missing YAC is not zero.
5. Report each exclusion, unmatched player, duplicate, missing measurement, and
   player count used in the final analysis.

## Feature families

- **Traditional:** 40-yard dash, 10-yard split, vertical and broad jump,
  three-cone, short shuttle, height, and weight, where available.
- **Tracking-derived:** maximum speed, early acceleration, maximum deceleration,
  time to peak speed, directional change, speed retention, post-cut acceleration,
  and path efficiency. Each feature must state its unit and attempt-aggregation
  rule.
- **Contextual:** route type, catch location or pass length, defender proximity,
  season, and opportunity measures where coverage is sufficient. These contextual
  fields help interpret YAC; they are not pre-draft scouting inputs.
