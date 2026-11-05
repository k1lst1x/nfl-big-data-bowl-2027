"""Audit supplied receiving outcomes; all aggregates remain provisional."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from nfl_bdb.data import read_columns, columns_for, _require_unique

METRICS = ('forty', 'ten_yd_split', 'vertical', 'broad_jump', 'three_cone',
           'short_shuttle', 'combine_height', 'combine_weight', 'bench_reps')
KEYS = ['game_id', 'play_id', 'nfl_id']


def receiving_audit(data_dir):
    """Inspect joins and candidate reception attribution without tracking loads.

    Select REG, completed, targeted, explicitly non-nullified rows with finite
    receiving yards and YAC. Zero and negative YAC are retained. Do not interpret
    this rule as source-validated; laterals and statistical attribution need review.
    Duplicate player-play keys or dimension IDs fail before aggregation.
    """
    players = read_columns(data_dir, 'players.csv', ['nfl_id', 'nfl_position', 'draft_year'])
    games = read_columns(data_dir, 'games.csv', ['game_id', 'season', 'season_type'])
    available = columns_for(data_dir, 'combine_results.csv')
    metrics = [m for m in METRICS if m in available]
    combine = read_columns(data_dir, 'combine_results.csv', ['nfl_id', 'draft_year', *metrics])
    fields = [*KEYS, 'target', 'pass_result', 'rec_yards', 'yards_after_catch',
              'play_nullified_by_penalty']
    plays = read_columns(data_dir, 'player_play.csv', fields)
    for frame, keys, name in [(players, ['nfl_id'], 'players'), (games, ['game_id'], 'games'),
                              (combine, ['nfl_id'], 'combine'), (plays, KEYS, 'player_play')]:
        _require_unique(frame, keys, name)
    # Read boolean text consistently whether pandas inferred bool or string.
    target = plays['target'].astype('string').str.upper()
    plays['target'] = target
    for field in ['rec_yards', 'yards_after_catch']:
        plays[field] = pd.to_numeric(plays[field], errors='coerce')
    joined = plays.merge(games.dropna(subset=['game_id']), on='game_id', how='left',
                         validate='many_to_one', indicator='game_join')
    joined = joined.merge(players.dropna(subset=['nfl_id']), on='nfl_id', how='left',
                          validate='many_to_one', indicator='player_join')
    checks = [
        ('all player-play rows', pd.Series(True, index=joined.index)),
        ('complete player-play key', joined[KEYS].notna().all(axis=1)),
        ('matched player and game', joined['game_join'].eq('both') & joined['player_join'].eq('both')),
        ('regular season', joined['season_type'].eq('REG')),
        ('completed pass', joined['pass_result'].eq('C')),
        ('target TRUE', joined['target'].eq('TRUE')),
        ('penalty flag N', joined['play_nullified_by_penalty'].eq('N')),
        ('finite receiving yards and YAC', np.isfinite(joined['rec_yards']) & np.isfinite(joined['yards_after_catch'])),
    ]
    keep = pd.Series(True, index=joined.index)
    flow = []
    for label, mask in checks:
        before = int(keep.sum())
        keep &= mask.fillna(False)
        flow.append(dict(stage=label, remaining_rows=int(keep.sum()), excluded_rows=before-int(keep.sum())))
    candidates = joined.loc[keep].copy()
    outcomes = candidates.groupby(['nfl_id', 'season']).agg(
        candidate_receptions=('yards_after_catch', 'size'),
        candidate_total_yac=('yards_after_catch', 'sum')).reset_index()
    outcomes['candidate_yac_per_reception'] = outcomes['candidate_total_yac'] / outcomes['candidate_receptions']
    # Include players with no candidates in the player-level coverage denominator.
    counts = candidates.groupby('nfl_id').size().rename('candidate_receptions')
    coverage = players.merge(counts, on='nfl_id', how='left', validate='one_to_one')
    coverage['candidate_receptions'] = coverage['candidate_receptions'].fillna(0).astype(int)
    coverage = coverage.merge(combine.drop(columns='draft_year').dropna(subset=['nfl_id']),
                              on='nfl_id', how='left', validate='one_to_one', indicator='combine_join')
    missingness = []
    thresholds = []
    for position, group in coverage.groupby('nfl_position', dropna=False):
        for threshold in (1, 10, 20, 30):
            eligible = group[group['candidate_receptions'].ge(threshold)]
            thresholds.append(dict(position=position, min_candidate_receptions=threshold,
                                   players=len(eligible), with_combine_row=int(eligible['combine_join'].eq('both').sum())))
        for metric in METRICS:
            receiving = group[group['candidate_receptions'].gt(0)]
            numeric = pd.to_numeric(receiving[metric], errors='coerce') if metric in metrics else pd.Series(np.nan, index=receiving.index)
            missingness.append(dict(position=position, metric=metric, column_available=metric in metrics,
                                    receiving_players=len(receiving), usable_players=int(np.isfinite(numeric).sum()),
                                    missing_or_invalid_players=int((~np.isfinite(numeric)).sum())))
    yac_rows = joined[joined['yards_after_catch'].notna()]
    patterns = yac_rows.groupby(['target', 'pass_result', 'play_nullified_by_penalty'], dropna=False).size().reset_index(name='rows')
    diagnostics = {
        'unmatched_game_rows': int(joined['game_join'].eq('left_only').sum()),
        'unmatched_player_rows': int(joined['player_join'].eq('left_only').sum()),
        'combine_ids_absent_from_players': len(set(combine['nfl_id'].dropna()) - set(players['nfl_id'].dropna())),
        'combine_draft_year_disagreements': int(players.merge(combine, on='nfl_id', suffixes=('_player', '_combine')).eval('draft_year_player != draft_year_combine').sum()),
        'unknown_or_missing_target_rows': int((~target.isin(['TRUE', 'FALSE'])).sum()),
        'yac_rows_without_target_true': int((~yac_rows['target'].eq('TRUE').fillna(False)).sum()),
    }
    table = outcomes.merge(players.dropna(subset=['nfl_id']), on='nfl_id', validate='many_to_one').merge(
        combine.drop(columns='draft_year').dropna(subset=['nfl_id']), on='nfl_id', how='left', validate='many_to_one')
    exceptions = yac_rows[~yac_rows['target'].eq('TRUE').fillna(False)]
    return dict(player_season=table, player_coverage=coverage, exclusions=pd.DataFrame(flow),
                thresholds=pd.DataFrame(thresholds), missingness=pd.DataFrame(missingness),
                yac_patterns=patterns, attribution_exceptions=exceptions[fields], diagnostics=diagnostics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', required=True)
    parser.add_argument('--output-dir', required=True, help='Use an ignored outputs/ directory')
    args = parser.parse_args()
    report = receiving_audit(args.data_dir)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, value in report.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(output / f'{name}.csv', index=False)
        else:
            (output / f'{name}.json').write_text(json.dumps(value, indent=2) + '\n')
    print(report['exclusions'].to_string(index=False))
    print(json.dumps(report['diagnostics'], indent=2))


if __name__ == '__main__':
    main()
