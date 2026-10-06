#!/usr/bin/env python3
"""Bind the controller to the released mechanical motion envelope."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MECHANICAL = HERE.parents[1] / 'hardware/printed-parts/fixtures/pgfun-positioner'

def expected():
    record = json.loads((MECHANICAL/'motion-geometry.json').read_text())
    g = record['motion']
    digest = hashlib.sha256(json.dumps(g, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    design = json.loads((MECHANICAL/'design.json').read_text())
    root=HERE.parents[1]
    if (digest != record['sha256'] or any(g.get(k) != v for k,v in design.items()) or
        not g.get('mechanical_sources') or
        any(hashlib.sha256((root/p).read_bytes()).hexdigest()!=v for p,v in g['mechanical_sources'].items())):
        raise ValueError('Rebuild mechanical outputs before generating firmware')
    counts = g['reduction'] * g['motor_full_steps'] * g['external_microsteps']
    limit = int(counts * g['soft_limit_deg']/360)
    return f'''#pragma once
#include <array>
#include <cstdint>
namespace pgfun_positioner {{
constexpr int32_t kCountsPerRev = {counts};
constexpr std::array<int32_t, 2> kMinCount = {{-{limit}, -{limit}}};
constexpr std::array<int32_t, 2> kMaxCount = {{{limit}, {limit}}};
constexpr const char *kGeometrySha256 = "{digest}";
}}
'''

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    path=HERE/'geometry_generated.h';text=expected()
    if args.check:
        if not path.exists() or path.read_text()!=text:raise SystemExit('Generated geometry is stale')
    else:path.write_text(text)
