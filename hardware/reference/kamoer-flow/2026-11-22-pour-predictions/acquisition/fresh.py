"""Validate frozen concentrate-dose forecasts with measured starts and simulated lever histories."""
import json
import sys
import time

from board import Board, Journal
from geometry import read_window
from lab import HERE, RECORD, WINDOWS
from pours import REF_ML, USB, arrange, configure, pour, read_settings, restore, window


def start_at_fill(board, journal, label, head, predicted, position, control):
    sign = 1 if head == 'B' else -1
    target = REF_ML + control['offset_from_center'][position] - sign * predicted / 2
    duration = control['conditioning_ms']
    approach = target - sign * duration * (0.010 if head == 'B' else 0.0115)
    arranged = arrange(board, journal, label, approach, max_steps=7)
    time.sleep(control['rest_seconds'])
    receipt = board.gate(head, duration)
    journal.append('condition', label=label, level=position, head=head, ms=duration,
                   position_window=arranged['label'], **receipt)
    time.sleep(control['rest_seconds'])
    before = window(label + '-conditioned', journal)
    motion = sign * (before['operating_ml'] - arranged['operating_ml'])
    if not 1.0 < motion < 9.0:
        raise RuntimeError(('uncertain conditioning transfer', label, motion))
    return before, target


def transfer(head, before, after, sight):
    a, b = before[sight]['ml'], after[sight]['ml']
    if a is None or b is None:
        return None
    return (b - a) * (1 if head == 'B' else -1)


def run(phase, start, end, tag):
    design_file, model_file = {
        'fresh': ('fresh-programs.json', 'geometry-model.json'),
        'fill': ('fill-design.json', 'fill-model.json'),
        'repeat': ('repeat-design.json', 'repeat-model.json'),
    }[phase]
    design = json.loads((RECORD / design_file).read_text())
    forecasts = json.loads((RECORD / model_file).read_text())['forecasts']
    sys.path.insert(0, str(RECORD / 'optical-calibration'))
    calibration = json.loads((RECORD / 'optical-calibration/geometry-used.json').read_text())
    log = HERE / f'{phase}.jsonl'
    journal = Journal(log)
    done = {r['index'] for r in map(json.loads, log.read_text().splitlines()) if r['event'] == 'trial'}
    board = Board(USB, journal)
    try:
        settings = read_settings(board)
        for index, trial in enumerate(design['orders']['validation']):
            if index in done or not start <= index <= end:
                continue
            head, scenario, block = trial['head'], trial['scenario'], trial['block']
            s, forecast = design['scenarios'][scenario], forecasts[scenario][head]
            sign = 1 if head == 'B' else -1
            label = f'{tag}-{index:03d}-{head.lower()}-{scenario.replace("_", "-")}'
            if phase == 'fill':
                label += '-' + trial['level']
                before, target = start_at_fill(board, journal, label, head, forecast, trial['level'], design['control'])
            else:
                offset = design['epochs']['validation_offset_ml'][block - 1]
                target = REF_ML + offset - sign * forecast / 2
                before = arrange(board, journal, label, target)
            pre = read_window(WINDOWS / before['label'], calibration)
            if pre['x990']['ml'] is None:
                raise RuntimeError(('unresolved starting volume', label))
            configure(board, settings, head, s['ratio'])
            if not 191 <= before['operating_ml'] + sign*(18*s['ideal_on_s']+3) <= 307:
                raise RuntimeError(('maximum transfer outside band', label))
            meta = dict(phase=phase, index=index, block=block, label=label, scenario=scenario, head=head,
                        pre=before['label'], forecast_ml=forecast)
            if phase == 'fill':
                meta['level'] = trial['level']
            journal.append('prediction', **meta, ideal_bursts=s['ideal_bursts'], target_start_ml=target,
                           start_optical=pre, forecast_finish_ml=pre['x990']['ml'] + sign * forecast)
            bursts, elapsed, ended = pour(board, head, s)
            time.sleep(max(0, ended + 2.9 - time.monotonic()))
            after = window(label + '-post', journal)
            post = read_window(WINDOWS / after['label'], calibration)
            primary, secondary = [transfer(head, pre, post, site) for site in ('x990', 'x1986')]
            motion = sign * (after['operating_ml'] - before['operating_ml'])
            journal.append('trial', **meta, post=after['label'], start_ml=pre['x990']['ml'],
                           finish_ml=post['x990']['ml'], primary_ml=primary, heldout_ml=secondary,
                           burst_count=bursts, expected_bursts=s['ideal_bursts'], elapsed_ms=elapsed,
                           pre_cup=pre, post_cup=post, operating_change_ml=motion)
            print(index, head, scenario, 'forecast', round(forecast,2), 'primary', primary,
                  'second', secondary, 'bursts', bursts, flush=True)
            if motion < .3 * forecast or motion > 2 * forecast + 2:
                raise RuntimeError(('unconfirmed physical transfer', label, motion))
    except BaseException as exc:
        journal.append('halt', error=repr(exc))
        board.send('flow 0 0')
        board.send('stop')
        time.sleep(.6)
        raise
    finally:
        try:
            board.status()
            restore(board)
        finally:
            board.close()
            journal.append('closed', phase=phase)


if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
