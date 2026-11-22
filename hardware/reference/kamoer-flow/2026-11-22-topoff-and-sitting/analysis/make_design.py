"""Write the session's programs, motor schedules from the firmware policy replay, and frozen forecasts from Codex's model."""
import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORD = HERE.parent
sys.path.insert(0, str(HERE))
from dose_model import predict

TRACE = sys.argv[1]  # compiled acquisition/policy_trace.cpp against firmware/lib/machine_policy
MODEL = json.loads((RECORD / 'model-used.json').read_text())


def gates(ratio, meter):
    args = [TRACE, str(ratio)] + [str(v) for stage in meter for v in stage]
    out = subprocess.check_output(args, text=True).split('\n')
    g = [[int(a), int(b)] for a, b in (s.split() for s in out if s and not s.startswith('stop'))]
    stop = [int(s.split()[1]) for s in out if s.startswith('stop')][0]
    return g, stop


PROGRAMS = {
    # Experiment 1: the slow top-off, one ingredient at a time.
    'topoff_n11': dict(ratio=18, meter=[[1, 5900]], start_ml=240, note='Codex low_topoff as reserved: 51 ms on, 494 ms off, 11 bursts'),
    'topoff_n6': dict(ratio=18, meter=[[1, 3000]], start_ml=240, note='same pulse and gap, 6 bursts'),
    'topoff_n22': dict(ratio=18, meter=[[1, 11700]], start_ml=240, note='same pulse and gap, 22 bursts'),
    'topoff_gap600': dict(ratio=20, meter=[[1, 6800]], start_ml=240, note='11 bursts of 50 ms with the training trickle gap'),
    'topoff_gap290': dict(ratio=10, meter=[[1, 3620]], start_ml=240, note='11 bursts of 55 ms with a short gap'),
    'topoff_high': dict(ratio=18, meter=[[1, 5900]], start_ml=256, note='topoff_n11 started high in the cup'),
    'topoff_low': dict(ratio=18, meter=[[1, 5900]], start_ml=222, note='topoff_n11 started low in the cup'),
    # Experiment 2 and the session check.
    'top_off': dict(ratio=20, meter=[[6, 650]], start_ml=240, note='training top-off from the pour-predictions archive: two 200 ms bursts'),
    'steady_glass': dict(ratio=19, meter=[[6, 6750]], start_ml=258, note='Codex steady_glass: full glass at full opening'),
}

design = {'programs': {}}
for name, p in PROGRAMS.items():
    g, stop = gates(p['ratio'], p['meter'])
    design['programs'][name] = dict(p, gates_start_ms_width_ms=g, bursts=len(g), on_s=sum(w for _, w in g) / 1000,
                                    stop_ms=stop, forecast_ml={h: predict(MODEL, h, g) for h in 'AB'})

rng = random.Random(20261122)
exp1 = ['topoff_n11', 'topoff_n6', 'topoff_n22', 'topoff_gap600', 'topoff_gap290', 'topoff_high', 'topoff_low']
blocks = []
for b in range(3):
    order = exp1[:]
    rng.shuffle(order)
    blocks.append(order)
design['exp1_blocks'] = blocks
sits = [10, 3, 30, 3, 10, 30]
design['exp2_sits_min'] = sits
print(json.dumps(design, indent=1))
