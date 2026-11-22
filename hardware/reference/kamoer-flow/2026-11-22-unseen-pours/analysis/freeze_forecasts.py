"""Calculate concentrate-dose predictions from the committed programs and the frozen historical fit."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import time
import sys

from dose_model import predict


def interpolate(width, anchors):
    scale = sorted((int(x), y) for x, y in anchors.items())
    for (left, a), (right, b) in zip(scale, scale[1:]):
        if left <= width <= right:
            return a + (width-left)*(b-a)/(right-left)
    raise ValueError(width)


def freeze(record):
    read = lambda name: json.loads((record/name).read_text())
    model, design = read('model.json'), read('design.json')
    prior_name = 'hardware/reference/kamoer-flow/2026-11-22-pour-predictions/geometry-model.json'
    prior = json.loads(subprocess.check_output(['git','show',model['training_revision']+':'+prior_name]))['anchors_ml_per_burst']
    table = {}
    for name, case in design['scenarios'].items():
        gates = case['ideal_gates_start_ms_width_ms']
        table[name] = {}
        for head in 'AB':
            table[name][head] = {
                'dose_ml': predict(model, head, gates),
                'old_width_model_ml': sum(interpolate(w, prior[head]) for _,w in gates),
            }
    return {'utc':datetime.now(timezone.utc).isoformat(), 'monotonic_ns':time.monotonic_ns(),
            'input_sha256':{name:hashlib.sha256((record/name).read_bytes()).hexdigest()
                             for name in ('design.json','model.json','analysis/dose_model.py','optics/geometry-used.json')},
            'forecasts':table}


if __name__ == '__main__':
    d = Path(sys.argv[1])
    with (d/'forecasts.json').open('x') as stream:
        stream.write(json.dumps(freeze(d),indent=2)+'\n')
