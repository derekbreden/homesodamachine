"""Run genrules with one enclosure-data binary and compare every file each leaves against the
baseline manifest (base/<rule>.base.0.json, hashed the same way: source sites and the work path
masked). A rule with an extended manifest (base/<rule>.base.1.json) is hashed and compared the
extended way (harness/batch.py, `tree`): the wall-time samples left out, the parts-cache scratch
directories masked, and a digest of a file of the same run read as that file's path.

usage: compare.py <rule>[,<rule>...] <label>=<binary> [--keep] [--direct] [--save-base]
Prints one JSON line per rule: status, wall/cpu, files, differ_count and the differing paths.
Labels name the work clones (work/<rule>.<label>.0): use your agent name. --keep keeps the clone
(delete it when done); a rule that differs keeps it anyway. --direct also runs the baseline binary
(label <label>-base) and compares the two runs, for a rule with no manifest yet or one whose
inputs outside this crate (part programs, other workers) moved since the manifest was saved.
--save-base runs the binary once, hashed the extended way, and saves that as the rule's extended
manifest (run it with the baseline binary).
"""
import argparse
import importlib.util
import json
import os
import shutil
import sys
import types
from pathlib import Path

RUN = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('batch', RUN / 'harness/batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
REV = '21d4adf8c'

ap = argparse.ArgumentParser()
ap.add_argument('rules')
ap.add_argument('variant')
ap.add_argument('--keep', action='store_true')
ap.add_argument('--timing', action='store_true')
ap.add_argument('--direct', action='store_true')
ap.add_argument('--save-base', action='store_true')
args = ap.parse_args()
label, binary = args.variant.split('=', 1)
binary = os.path.abspath(binary)
assert os.access(binary, os.X_OK), binary
spec_pins = json.load(open(RUN / 'pins-baseline.json'))
spec_pins['workers'] = {'enclosure-data': binary}
pins = RUN / f'pins-{label}.json'
pins.write_text(json.dumps(spec_pins))
base_pins = RUN / 'pins-baseline.json'
rules = batch.rules_at(REV)
opts = types.SimpleNamespace(trace_dir=None, timing=args.timing)
for rule in args.rules.split(','):
    extended_path = RUN / 'base' / f'{rule}.base.1.json'
    opts.extended = args.save_base or extended_path.exists()
    base_path = extended_path if opts.extended else RUN / 'base' / f'{rule}.base.0.json'
    template, info = batch.stage(REV, rule, rules[rule], RUN)
    if args.save_base:
        row, hashes, work = batch.run_variant(rule, template, info, label, str(pins), 0, opts)
        if row['status'] == 'ok':
            extended_path.write_text(json.dumps({'row': row, 'hashes': hashes, 'binary': binary}, sort_keys=True))
            row['saved'] = str(extended_path)
        if not args.keep and row['status'] == 'ok':
            shutil.rmtree(work, ignore_errors=True)
        else:
            row['kept'] = str(work)
        print(json.dumps(row), flush=True)
        continue
    base_work = None
    if args.direct:
        base_row, base_hashes, base_work = batch.run_variant(rule, template, info, label + '-base',
                                                            str(base_pins), 0, opts)
        base = {'row': base_row, 'hashes': base_hashes}
    elif not base_path.exists():
        print(json.dumps({'rule': rule, 'error': 'no baseline manifest yet: use --direct'}))
        continue
    else:
        base = json.load(open(base_path))
    row, hashes, work = batch.run_variant(rule, template, info, label, str(pins), 0, opts)
    differ = sorted(k for k in set(hashes) | set(base['hashes'])
                    if k not in batch.NOISE and hashes.get(k) != base['hashes'].get(k))
    row['extended'] = opts.extended
    row['against'] = 'base'
    row['base_status'] = base['row']['status']
    row['differ_count'] = len(differ)
    row['differ'] = differ[:60]
    if row.get('error'):
        row['error'] = row['error'][-2500:]
    if base_work is not None:
        if differ or row['status'] != 'ok' or args.keep:
            row['kept_base'] = str(base_work)
        else:
            shutil.rmtree(base_work, ignore_errors=True)
    if differ or row['status'] != 'ok':
        row['kept'] = str(work)
    elif not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    else:
        row['kept'] = str(work)
    print(json.dumps(row), flush=True)
