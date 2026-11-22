"""Read the registered release-and-reopen comparison again from the calibrated clear-glass photographs."""
import argparse
import csv
import json
from pathlib import Path
from statistics import median


def compare(rows):
    result = {}
    for head in 'AB':
        result[head] = {}
        for site in ('x990', 'x1986'):
            pairs = {}
            for scenario in ('same_open_time', 'release_reopen'):
                pairs[scenario] = {
                    int(r['block']): float(r[site + '_dose_ml']) for r in rows
                    if r['phase'] == 'original program' and r['head'] == head
                    and r['scenario'] == scenario and r[site + '_dose_ml'] and r['bursts_match'] == 'True'
                }
            steady, interrupted = pairs['same_open_time'], pairs['release_reopen']
            by_block = [{'block': b, 'continuous_ml': steady[b], 'interrupted_ml': interrupted[b],
                         'fraction_less': 1 - interrupted[b] / steady[b]} for b in sorted(steady.keys() & interrupted.keys())]
            result[head][site] = {
                'matched_blocks': len(by_block), 'lower_in': sum(r['fraction_less'] > 0 for r in by_block),
                'continuous_median_ml': median(steady.values()), 'interrupted_median_ml': median(interrupted.values()),
                'fraction_less_ratio_of_medians': 1 - median(interrupted.values()) / median(steady.values()),
                'pairs': by_block,
            }
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('optical_trials', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    with args.optical_trials.open() as stream:
        result = compare(list(csv.DictReader(stream)))
    args.output.write_text(json.dumps(result, indent=2) + '\n')
