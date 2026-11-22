"""Drive the bench for this record: photograph the cup, set its level with single gates, run metered pours and sits, and park."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORD = HERE.parent
sys.path[:0] = [str(HERE), str(RECORD / 'camera')]
import cam  # noqa: E402
from board import Board, Journal  # noqa: E402
from meter import configure, pour, read_settings  # noqa: E402

USB = '/dev/cu.usbserial-120'
PROGRAMS = json.loads((RECORD / 'programs.json').read_text())['programs']
ORIGINAL = {'flavor': 'A', 'A': 20, 'B': 15}
FROZEN_INPUTS = ('model-used.json', 'programs.json', 'design.json')


class Bench:
    def __init__(self, work, tag):
        self.work = Path(work)
        self.tag = tag
        self.log = Journal(self.work / 'logs' / f'{tag}.jsonl')
        self.endpoints = self.work / 'endpoints'
        self.count = 0
        digests = {k: hashlib.sha256((RECORD / k).read_bytes()).hexdigest() for k in FROZEN_INPUTS}
        self.log.append('session', tag=tag, inputs_sha256=digests)
        self.board = Board(USB, self.log)
        self.settings = read_settings(self.board)
        self.log.append('settings_found', settings=self.settings)

    def label(self, what):
        self.count += 1
        return f'{self.tag}-{self.count:03d}-{what}'

    def photo(self, what):
        lab = self.label(what)
        s = cam.Stream(self.work, lab, 7.5, journal=self.log)
        try:
            return cam.photograph(s, lab, self.endpoints)
        finally:
            s.close()

    @staticmethod
    def confirmed(shot):
        v = [shot['readings'][k]['ml'] for k in ('x990', 'x1986')]
        if any(x is None or not 183 < x < 290 for x in v):
            raise ValueError(('cup outside the reader band', shot['label'], v))
        if abs(v[0] - v[1]) > 4:
            raise ValueError(('sightlines disagree', shot['label'], v))
        return v[0]

    def gate(self, head, ms, why):
        receipt = self.board.gate(head, ms)
        self.log.append('position_gate', head=head, ms=ms, why=why, **receipt)

    def arrange(self, target, tolerance=1.1):
        if not 199 <= target <= 275:
            raise ValueError(('unsupported target', target))
        shot = self.photo(f'set{target:.0f}')
        for step in range(7):
            value = self.confirmed(shot)
            diff = target - value
            if abs(diff) <= tolerance:
                return shot
            head = 'B' if diff > 0 else 'A'
            ms = round(1000 * min(1.25, max(.025, abs(diff) / (10.0 if head == 'B' else 11.5))))
            self.gate(head, ms, f'arrange to {target}')
            time.sleep(2.25)
            after = self.photo(f'set{target:.0f}')
            moved = (self.confirmed(after) - value) * (1 if head == 'B' else -1)
            if ms >= 240 and not .45 < moved < ms * .025 + 2:
                raise RuntimeError(('positioning response out of range', ms, moved))
            shot = after
        if abs(self.confirmed(shot) - target) > max(tolerance, 1.5):
            raise RuntimeError(('could not set the starting level', target, shot['label']))
        return shot

    def measured(self, head, name, kind, extra=None):
        prog = PROGRAMS[name]
        forecast = prog['forecast_ml'][head]
        sign = 1 if head == 'B' else -1
        lab = self.label(f'{head.lower()}-{name}')
        seconds = 5.5 + 1.2 + prog['stop_ms'] / 1000 + 3.1 + 1.2 + 3
        s = cam.Stream(self.work, lab, seconds, journal=self.log)
        try:
            pre = cam.photograph(s, lab + '-pre', self.endpoints)
            start = self.confirmed(pre)
            edge = start + sign * (1.25 * forecast + 3)
            if not 182 < edge < 291:
                raise RuntimeError(('expected excursion leaves the reader band', lab, start, forecast))
            configure(self.board, self.settings, head, prog['ratio'])
            self.log.append('prediction', label=lab, head=head, program=name, kind=kind, dose_ml=forecast,
                            start={k: v['ml'] for k, v in pre['readings'].items()}, **(extra or {}))
            receipt = pour(self.board, head, prog, s)
            time.sleep(max(0, receipt['end_clock'] + 2.9 - time.monotonic()))
            post = cam.photograph(s, lab + '-post', self.endpoints)
        finally:
            s.close()
        dose = {k: None if post['readings'][k]['ml'] is None else
                (post['readings'][k]['ml'] - pre['readings'][k]['ml']) * sign for k in ('x990', 'x1986')}
        self.log.append('trial', label=lab, head=head, program=name, kind=kind, forecast_ml=forecast, dose_ml=dose,
                        pre=pre['readings'], post=post['readings'], receipt=receipt, **(extra or {}))
        print(time.strftime('%H:%M:%S'), lab, kind, f'forecast {forecast:.2f}',
              {k: None if v is None else round(v, 2) for k, v in dose.items()}, receipt['bursts'], flush=True)
        self.confirmed(post)
        if receipt['valves'] != ('E G' if head == 'A' else 'H J'):
            raise RuntimeError(('unexpected dispensing path', lab, receipt))
        if receipt['bursts'] != prog['bursts']:
            raise RuntimeError(('burst count differs from the policy replay', lab, receipt['bursts'], prog['bursts']))
        if any(v is None or not max(.15, forecast * .2) < v < 2 * forecast + 2 for v in dose.values()):
            raise RuntimeError(('transfer disagrees with direction or range', lab, dose))
        return dose

    def restore(self):
        now = read_settings(self.board)
        for h in 'AB':
            if now[h] != ORIGINAL[h]:
                configure(self.board, now, h, ORIGINAL[h])
        configure(self.board, now, ORIGINAL['flavor'], ORIGINAL[ORIGINAL['flavor']])
        back = read_settings(self.board)
        self.log.append('settings_restored', settings=back)
        if back != ORIGINAL:
            raise RuntimeError(('settings not restored', back))

    def close(self):
        try:
            self.board.status()
            self.restore()
        finally:
            self.board.close()
            self.log.append('closed')


def main(a):
    b = Bench(a.work, a.tag)
    try:
        if a.mode == 'direction':
            for head, sign in (('A', -1), ('B', 1)):
                before = b.photo(f'dir-{head.lower()}-before')
                b.gate(head, 60, 'direction check')
                time.sleep(2.25)
                after = b.photo(f'dir-{head.lower()}-after')
                moved = (b.confirmed(after) - b.confirmed(before)) * sign
                b.log.append('direction', head=head, moved_ml=moved)
                print(head, 'moved', round(moved, 3), 'mL in its direction', flush=True)
                if moved < .15:
                    raise RuntimeError(('direction check failed', head, moved))
        elif a.mode == 'glass':
            b.arrange(PROGRAMS['steady_glass']['start_ml'])
            b.measured('A', 'steady_glass', a.kind)
            b.measured('B', 'steady_glass', a.kind)
        elif a.mode == 'exp1':
            blocks = json.loads((RECORD / 'programs.json').read_text())['exp1_blocks']
            done = set()
            for path in (b.work / 'logs').glob('exp1*.jsonl'):
                for s in path.read_text().splitlines():
                    r = json.loads(s)
                    if r['event'] == 'prediction' and r['kind'].startswith('exp1'):
                        done.add((r['kind'], r['head']))
            for bi, order in enumerate(blocks):
                if bi + 1 < a.first_block:
                    continue
                for name in order:
                    kind = f'exp1-block{bi + 1}'
                    k = (f'{kind}-{name}', 'A')
                    if k in done:
                        continue
                    b.arrange(PROGRAMS[name]['start_ml'])
                    b.measured('A', name, f'{kind}-{name}', dict(block=bi + 1))
                    b.measured('B', name, f'{kind}-{name}', dict(block=bi + 1))
        elif a.mode == 'sit':
            b.arrange(PROGRAMS['top_off']['start_ml'])
            t0 = time.time()
            b.log.append('sit_start', minutes=a.minutes, index=a.index)
            print(time.strftime('%H:%M:%S'), 'sitting', a.minutes, 'min', flush=True)
            end = t0 + a.minutes * 60 - 7
            while time.time() < end:
                time.sleep(min(20, end - time.time()))
                b.board.port.reset_input_buffer()
            sat = time.time() - t0
            b.log.append('sit_end', minutes=a.minutes, index=a.index, sat_s=sat)
            info = dict(sit_min=a.minutes, sit_index=a.index)
            b.measured('A', 'top_off', 'exp2-sat', info)
            b.measured('B', 'top_off', 'exp2-sat', info)
            b.measured('A', 'top_off', 'exp2-conditioned', info)
            b.measured('B', 'top_off', 'exp2-conditioned', info)
        elif a.mode == 'history':
            for i in range(0 if a.after_only else 2):
                b.arrange(PROGRAMS['topoff_n11']['start_ml'])
                b.measured('A', 'topoff_n11', 'exp3-before', dict(repeat=i + 1))
                b.measured('B', 'topoff_n11', 'exp3-before', dict(repeat=i + 1))
            for i in range(0 if a.after_only else 3):
                if i == 0:
                    b.arrange(PROGRAMS['steady_glass']['start_ml'])
                b.measured('A', 'steady_glass', 'glass-late' if i == 0 else 'exp3-running', dict(repeat=i + 1))
                b.measured('B', 'steady_glass', 'glass-late' if i == 0 else 'exp3-running', dict(repeat=i + 1))
            for i in range(3):
                b.arrange(PROGRAMS['topoff_n11']['start_ml'])
                b.measured('A', 'topoff_n11', 'exp3-after', dict(repeat=i + 1))
                b.measured('B', 'topoff_n11', 'exp3-after', dict(repeat=i + 1))
        elif a.mode == 'park':
            b.arrange(a.target, tolerance=.3)
            time.sleep(8)
            b.photo('parked')
        elif a.mode == 'photo':
            for _ in range(a.repeat):
                shot = b.photo('rest')
                print(time.strftime('%H:%M:%S'), {k: round(v['ml'], 3) for k, v in shot['readings'].items()}, flush=True)
    except BaseException as error:
        b.log.append('halt', error=repr(error))
        b.board.send('flow 0 0')
        b.board.send('stop')
        time.sleep(1.2)
        raise
    finally:
        b.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('direction', 'glass', 'exp1', 'sit', 'history', 'park', 'photo'))
    p.add_argument('work', type=Path)
    p.add_argument('--tag', required=True)
    p.add_argument('--kind', default='glass')
    p.add_argument('--first-block', type=int, default=1)
    p.add_argument('--minutes', type=float, default=0)
    p.add_argument('--index', type=int, default=0)
    p.add_argument('--target', type=float, default=233.2)
    p.add_argument('--repeat', type=int, default=1)
    p.add_argument('--after-only', action='store_true', help='resume a history run after its glasses')
    main(p.parse_args())
