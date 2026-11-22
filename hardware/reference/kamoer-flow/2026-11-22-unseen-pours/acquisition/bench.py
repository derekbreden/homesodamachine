"""Run a single reserved set of metered concentrate pours and return the cup to its photographed start."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

from board import Board, Journal
from meter import configure, pour, read_settings
from stream import exposure, live

RECORD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RECORD/'optics'))
from read_levels import measure

DESIGN = json.loads((RECORD/'design.json').read_text())
FREEZE = json.loads((RECORD/'forecasts.json').read_text())
USB = '/dev/cu.usbserial-120'


def photograph(camera, journal, label):
    path = exposure(camera, label)
    readings = measure(path)
    capture = json.loads((path/'window.json').read_text())
    result = {'label':label, 'readings':readings, 'mid':capture['mid']}
    journal.append('image', **result)
    return result


def confirmed(snapshot):
    sites = snapshot['readings']
    values = [s['ml'] for s in sites.values()]
    if any(x is None or not 183 < x < 290 for x in values):
        raise ValueError(('Cup outside optical working range', snapshot))
    if abs(values[0]-values[1]) > 4:
        raise ValueError(('Cup sightlines disagree', snapshot))
    return sites['x990']['ml']


def arrange(camera, board, journal, label, target, tolerance=1.1):
    if not 199 <= target <= 275:
        raise ValueError(('Unsupported target', target))
    before = photograph(camera, journal, label+'-entry')
    for step in range(7):
        value = confirmed(before)
        diff = target - value
        if abs(diff) <= tolerance:
            return before
        head = 'B' if diff > 0 else 'A'
        seconds = abs(diff) / (10.0 if head == 'B' else 11.5)
        ms = round(1000 * min(1.25, max(.025, seconds)))
        live(camera)
        receipt = board.gate(head, ms)
        journal.append('position_gate', head=head, label=label, step=step, ms=ms, before=before['label'], **receipt)
        time.sleep(2.25)
        after = photograph(camera, journal, label+f'-set{step+1}')
        motion = (confirmed(after)-value)*(1 if head=='B' else -1)
        if ms >= 240 and not .45 < motion < ms*.025+2:
            raise RuntimeError(('Positioning response out of range', label, ms, motion))
        before = after
    if abs(confirmed(before)-target) > max(tolerance,1.5):
        raise RuntimeError(('Could not establish starting level', label, target, before))
    return before


def restore(board, original):
    settings = read_settings(board)
    for h in 'AB':
        if settings[h] != original[h]:
            configure(board, settings, h, original[h])
    configure(board, settings, original['flavor'], original[original['flavor']])
    restored = read_settings(board)
    if restored != original:
        raise RuntimeError(('Failed to restore appliance settings', restored, original))
    board.events.append('settings_restored', settings=restored)


def run_trial(camera, board, log, settings, index, item, center, tag):
    h, name, block = item['head'], item['scenario'], item['block']
    case = DESIGN['scenarios'][name]
    forecast = FREEZE['forecasts'][name][h]['dose_ml']
    sign = 1 if h=='B' else -1
    midpoint = center + DESIGN['positioning']['midpoint_offsets_ml'][block-1]
    namebase = f'{tag}-{index:03d}-{h.lower()}-{name.replace("_","-")}'
    start = arrange(camera, board, log, namebase, midpoint-sign*forecast/2)
    pre = start['readings']
    edge = confirmed(start) + sign*(18*case['ideal_on_s'] + 3)
    if not 182 < edge < 291:
        raise RuntimeError(('Maximum expected excursion outside observed cup band', namebase, edge))
    configure(board, settings, h, case['ratio'])
    meta = dict(index=index, head=h, scenario=name, block=block, label=namebase)
    log.append('prediction', **meta, start=start['label'], start_cup=pre, dose_ml=forecast,
               predicted_finish_ml={k:s['ml']+sign*forecast for k,s in pre.items()},
               expected_bursts=case['ideal_bursts'])
    live(camera)
    receipt = pour(board, h, case, camera)
    time.sleep(max(0, receipt['end_clock'] + 2.9 - time.monotonic()))
    after = photograph(camera, log, namebase+'-post')
    post = after['readings']
    dose = {k: None if s['ml'] is None else (s['ml']-pre[k]['ml'])*sign for k,s in post.items()}
    log.append('trial', **meta, start=start['label'], finish=after['label'], pre=pre, post=post,
               dose_ml=dose, forecast_ml=forecast, receipt=receipt)
    print(index+1, h, name, f'{forecast:.2f}', dose, receipt['bursts'], flush=True)
    confirmed(after)
    if receipt['valves'] != ('E G' if h=='A' else 'H J'):
        raise RuntimeError(('Unexpected dispensing path', namebase, receipt))
    if any(x is None or not max(.15,forecast*.20) < x < 2*forecast+2 for x in dose.values()):
        raise RuntimeError(('Physical transfer disagrees with the expected direction or range', namebase, dose))


def main(args):
    work = args.run.resolve()/'work'
    camera = work.parent/'camera'
    ref = measure(camera/'windows/station-idle')
    center = confirmed({'readings':ref})
    for key, digest in FREEZE['input_sha256'].items():
        if hashlib.sha256((RECORD/key).read_bytes()).hexdigest()!=digest:
            raise ValueError(('Frozen input changed',key))
    path = work/(args.mode+'.jsonl')
    old = [json.loads(s) for s in path.read_text().splitlines()] if path.is_file() else []
    initiated = {r['index'] for r in old if r['event']=='prediction'}
    log = Journal(path)
    b = Board(USB, log)
    saved = work/'original-settings.json'
    try:
        settings = read_settings(b)
        if not saved.exists():
            saved.write_text(json.dumps(settings, indent=2)+'\n')
        original = json.loads(saved.read_text())
        log.append('session', mode=args.mode, run_tag=args.tag, settings=settings, reference=ref)
        if args.mode == 'validation':
            for i, item in enumerate(DESIGN['order']):
                if i not in initiated and args.first <= i <= args.last:
                    run_trial(camera, b, log, settings, i, item, center, args.tag)
        elif args.mode == 'qualify':
            at = photograph(camera, log, args.tag+'-blank')
            confirmed(at)
            log.append('no_pump', start=ref, finish=at['readings'])
        else:
            at = arrange(camera,b,log,args.tag,center,tolerance=.25)
            time.sleep(8)
            end = photograph(camera,log,args.tag+'-settled')
            confirmed(end)
            log.append('station_return', initial=ref, final=end['readings'],
                       change_ml={k:end['readings'][k]['ml']-s['ml'] for k,s in ref.items()})
    except BaseException as error:
        log.append('halt', error=repr(error))
        b.send('flow 0 0')
        b.send('stop')
        time.sleep(1.2)
        raise
    finally:
        try:
            b.status()
            if saved.exists():
                restore(b,json.loads(saved.read_text()))
        finally:
            b.close()
            log.append('closed', mode=args.mode)


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=('qualify','validation','park'))
    ap.add_argument('run',type=Path)
    ap.add_argument('--tag',required=True)
    ap.add_argument('--first',type=int,default=0)
    ap.add_argument('--last',type=int,default=71)
    main(ap.parse_args())
