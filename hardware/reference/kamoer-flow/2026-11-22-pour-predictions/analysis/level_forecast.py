"""Test whether calibrating a dose separately at each fill improves later endpoint predictions."""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


SITES = ('primary_ml', 'heldout_ml')


def read_journal(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def freeze(journal, output):
    if any(r['event'] == 'prediction' and r['block'] >= 5 for r in journal):
        raise ValueError('Reserved serving already predicted')
    training = [r for r in journal if r['event'] == 'trial' and r['block'] <= 3]
    cells = {}
    for head in 'AB':
        by_level = {}
        for level in ('low', 'high'):
            rows = [r for r in training if (r['head'], r['level']) == (head, level)]
            if sorted(r['block'] for r in rows) != [1, 2, 3]:
                raise ValueError('Incomplete training cell')
            by_level[level] = mean(r['primary_ml'] for r in rows)
        cells[head] = dict(by_level, pooled=mean(by_level.values()))
    model = {
        'question': 'Do fill-specific camera calibrations improve the next servings relative to a pooled calibration on the same pump?',
        'training': 'First three complete fill blocks, arithmetic mean at each head and level on the primary sightline. The pooled comparator averages those two means equally.',
        'test': 'Score blocks five and six, two servings per head and level. The intervening fourth block is excluded from both fits and tests. Both forecasts use the same pre-command cup photograph and the same observed endpoint.',
        'decision': 'Across all eight future servings on each sightline, require mean absolute error at least 0.25 nominal mL smaller than the pooled forecast and at least seven of eight within max(1 mL, 10 percent of the fill-specific prediction). Missing reads and wrong burst counts preclude a pass. Report by head even if the aggregate passes.',
        'limits': 'Same five-burst program and the same two fills used for training. All outcomes share a camera and two vessels. Two future servings in each head and level are a check of this calibration only.',
        'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'frozen_monotonic_ns': time.monotonic_ns(),
        'training_indices': [r['index'] for r in training],
        'forecasts_ml': cells,
    }
    with output.open('x') as stream:
        stream.write(json.dumps(model, indent=2) + '\n')


def summarize(rows, site):
    valid = [r for r in rows if r[site] is not None and r['bursts_correct']]
    if not valid:
        return {'n': len(rows), 'usable': 0}
    errors = {model: [abs(r[site] - r[model]) for r in valid] for model in ('conditional_ml', 'pooled_ml')}
    conditional, pooled = (mean(errors[m]) for m in ('conditional_ml', 'pooled_ml'))
    return {'n': len(rows), 'usable': len(valid), 'conditional_mae_ml': conditional, 'pooled_mae_ml': pooled,
            'improvement_ml': pooled - conditional,
            'conditional_in_band': sum(abs(r[site] - r['conditional_ml']) <= max(1, .1 * r['conditional_ml']) for r in valid)}


def score(journal, model, output):
    predictions = {r['index']: r for r in journal if r['event'] == 'prediction'}
    records = []
    for r in journal:
        if r['event'] != 'trial' or r['block'] not in (5, 6):
            continue
        stamp = predictions[r['index']]['mono_ns']
        if stamp <= model['frozen_monotonic_ns']:
            raise ValueError('Test forecast predates the numerical freeze')
        head, level = r['head'], r['level']
        cal = model['forecasts_ml'][head]
        records.append({'index': r['index'], 'head': head, 'level': level, 'block': r['block'], 'pre': r['pre'],
                        'post': r['post'], 'conditional_ml': cal[level], 'pooled_ml': cal['pooled'],
                        'start_ml': r['start_ml'], 'conditional_finish_ml': r['start_ml'] + (1 if head == 'B' else -1) * cal[level],
                        'actual_finish_ml': r['finish_ml'], 'primary_ml': r['primary_ml'], 'heldout_ml': r['heldout_ml'],
                        'bursts_correct': r['expected_bursts'] == r['burst_count']})
    if sorted(r['index'] for r in records) != list(range(16, 24)):
        raise ValueError('Missing future serving')
    overall = {site: summarize(records, site) for site in SITES}
    passed = all(s['usable'] == 8 and s['conditional_in_band'] >= 7 and s['improvement_ml'] >= .25 for s in overall.values())
    by_head = {h: {site: summarize([r for r in records if r['head'] == h], site) for site in SITES} for h in 'AB'}
    output.write_text(json.dumps({'passed': passed, 'overall': overall, 'by_head': by_head, 'servings': records}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('freeze', 'score'))
    parser.add_argument('journal', type=Path)
    parser.add_argument('model', type=Path)
    parser.add_argument('output', type=Path, nargs='?')
    args = parser.parse_args()
    events = read_journal(args.journal)
    if args.mode == 'freeze':
        freeze(events, args.model)
    else:
        score(events, json.loads(args.model.read_text()), args.output)
