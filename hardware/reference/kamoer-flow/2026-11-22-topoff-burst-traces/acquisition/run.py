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

    def measured(self, head, name, kind, extra=None, bracket_s=0.0, trace=False):
        prog = PROGRAMS[name]
        forecast = prog['forecast_ml'][head]
        sign = 1 if head == 'B' else -1
        lab = self.label(f'{head.lower()}-{name}')
        seconds = 5.5 + 1.2 + prog['stop_ms'] / 1000 + 3.1 + 1.2 + 3 + (bracket_s + 1.2 if bracket_s else 0)
        s = cam.Stream(self.work, lab, seconds, journal=self.log)
        still = None
        try:
            if bracket_s:
                still = cam.photograph(s, lab + '-still', self.endpoints)
                time.sleep(max(0, still['wall_mid'] + bracket_s - time.time()))
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
            if trace:
                t0 = (still or pre)['wall_mid'] - .5
                t1 = post['wall_mid'] + .5
                keep = [f for f in list(s.frames) if t0 <= f[1] <= t1]
                (self.work / 'traces').mkdir(exist_ok=True)
                with open(self.work / 'traces' / f'{lab}.npz', 'wb') as out:
                    cam.np.savez_compressed(out, native_luma=cam.np.stack([f[2] for f in keep]),
                                            wall_s=cam.np.array([f[1] for f in keep]), seq=cam.np.array([f[0] for f in keep]),
                                            sensor_x=cam.SENSOR_X, sensor_y=cam.SENSOR_Y,
                                            wall_minus_monotonic_s=time.time() - time.monotonic())
        finally:
            s.close()
        dose = {k: None if post['readings'][k]['ml'] is None else
                (post['readings'][k]['ml'] - pre['readings'][k]['ml']) * sign for k in ('x990', 'x1986')}
        settle = None
        if still:
            # No-pump drift over the bracket before the pour, scaled to the pre-to-post interval, in the pump's direction.
            span = (post['wall_mid'] - pre['wall_mid']) / (pre['wall_mid'] - still['wall_mid'])
            settle = {k: (pre['readings'][k]['ml'] - still['readings'][k]['ml']) * span * sign for k in ('x990', 'x1986')}
        extra = dict(extra or {}, still=still and still['readings'], settle_ml=settle,
                     corrected_dose_ml=settle and {k: dose[k] - settle[k] for k in dose})
        self.log.append('trial', label=lab, head=head, program=name, kind=kind, forecast_ml=forecast, dose_ml=dose,
                        pre=pre['readings'], post=post['readings'], receipt=receipt, **(extra or {}))
        print(time.strftime('%H:%M:%S'), lab, kind, f'forecast {forecast:.2f}',
              {k: None if v is None else round(v, 2) for k, v in dose.items()},
              'settle', settle and {k: round(v, 2) for k, v in settle.items()}, receipt['bursts'], flush=True)
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
        elif a.mode == 'tracetest':
            b.arrange(PROGRAMS['topoff_n11']['start_ml'])
            b.measured('A', 'topoff_n11', 'resolution-test', {}, 10, True)
        elif a.mode == 'traces':
            plan = json.loads((RECORD / 'design.json').read_text())
            deadline = time.mktime(time.strptime(time.strftime('%Y-%m-%d ') + plan['last_cycle_end_local'], '%Y-%m-%d %H:%M'))
            for i in range(plan['cycles']):
                if time.time() + plan['cycle_budget_s'] > deadline:
                    b.log.append('cycle_skipped', index=i)
                    print('skipped cycle', i, flush=True)
                    continue
                b.arrange(PROGRAMS['steady_glass']['start_ml'])
                for head in 'AB':
                    b.measured(head, 'steady_glass', 'glass', dict(cycle=i))
                    done = time.time()
                    while time.time() < done + plan['delay_s'] - 6.5 - plan['bracket_s']:
                        time.sleep(.5)
                    b.measured(head, 'topoff_n11', 'after-own-glass', dict(cycle=i), plan['bracket_s'], True)
                    b.measured(head, 'topoff_n11', 'after-topoff', dict(cycle=i), plan['bracket_s'], True)
        elif a.mode == 'reproduce':
            plan = json.loads((RECORD / 'design.json').read_text())['amendment']
            bracket = plan['bracket_s']

            def wait_until(t):
                while time.time() < t:
                    time.sleep(.5)

            def episode(name, pairs, gates, index):
                b.arrange(PROGRAMS['steady_glass']['start_ml'])
                for p in range(pairs):
                    for head in 'AB':
                        b.measured(head, 'steady_glass', f'{name}-glass', dict(episode=index, pair=p + 1))
                last = time.time()
                b.log.append('pause_start', episode=index, name=name, gates=gates)
                if gates:
                    b.arrange(PROGRAMS['topoff_n11']['start_ml'])
                wait_until(last + plan['pause_s'] - 6.5 - bracket)
                for k in (1, 2):
                    for head in 'AB':
                        b.measured(head, 'topoff_n11', f'{name}-topoff{k}', dict(episode=index, gates=gates), bracket)

            for i in range(2):
                b.arrange(PROGRAMS['topoff_n11']['start_ml'])
                b.measured('A', 'topoff_n11', 'rested', dict(repeat=i + 1), bracket)
                b.measured('B', 'topoff_n11', 'rested', dict(repeat=i + 1), bracket)
            for i, (name, pairs, gates) in enumerate(plan['episodes']):
                episode(name, pairs, gates, i)
        elif a.mode == 'afterglass':
            plan = json.loads((RECORD / 'design.json').read_text())
            deadline = time.mktime(time.strptime(time.strftime('%Y-%m-%d ') + plan['last_cycle_end_local'], '%Y-%m-%d %H:%M'))
            bracket = plan['bracket_s']
            for i in range(0 if a.skip_rested else 2):
                b.arrange(PROGRAMS['topoff_n11']['start_ml'])
                b.measured('A', 'topoff_n11', 'rested', dict(repeat=i + 1), bracket)
                b.measured('B', 'topoff_n11', 'rested', dict(repeat=i + 1), bracket)
            for i, delay in enumerate(plan['cycle_delays_s']):
                if time.time() + plan['cycle_budget_s'][str(delay)] > deadline:
                    b.log.append('cycle_skipped', index=i, delay_s=delay)
                    print('skipped cycle', i, delay, flush=True)
                    continue
                b.arrange(PROGRAMS['steady_glass']['start_ml'])
                for head in 'AB':
                    b.measured(head, 'steady_glass', 'glass', dict(cycle=i, delay_s=delay))
                    done = time.time()
                    while time.time() < done + delay - 6.5 - bracket:
                        time.sleep(1)
                    b.log.append('delay', head=head, cycle=i, target_s=delay, waited_s=time.time() - done)
                    b.measured(head, 'topoff_n11', f'after-glass-{delay}s', dict(cycle=i, delay_s=delay), bracket)
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
    p.add_argument('mode', choices=('direction', 'glass', 'exp1', 'sit', 'history', 'tracetest', 'traces', 'reproduce', 'afterglass', 'park', 'photo'))
    p.add_argument('work', type=Path)
    p.add_argument('--tag', required=True)
    p.add_argument('--kind', default='glass')
    p.add_argument('--first-block', type=int, default=1)
    p.add_argument('--minutes', type=float, default=0)
    p.add_argument('--index', type=int, default=0)
    p.add_argument('--target', type=float, default=233.2)
    p.add_argument('--repeat', type=int, default=1)
    p.add_argument('--skip-rested', action='store_true', help='delay cycles after the reproduce run, whose rested top-offs stand')
    p.add_argument('--after-only', action='store_true', help='resume a history run after its glasses')
    main(p.parse_args())
