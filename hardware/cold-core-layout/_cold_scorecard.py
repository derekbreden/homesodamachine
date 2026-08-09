"""The cold core's arrangement as a scorecard, written beside its STEP.

Same sidecar the enclosure's card writes ([`web/contracts/scorecard-sidecar.js`]
(/web/contracts/scorecard-sidecar.js)), so the 3D viewer draws this card with the machinery it
already has. The checks are this assembly's own: what the enclosure grades is where bodies
stand against each other in a box, and what is graded here is a vessel, a wound coil, two
reservoirs and the lines potted around them.

REPORTING, NOT GATING. `main` never exits nonzero on a finding — every row lands in the card
and on the terminal, and the build still writes its STEP. A reading that stops the build is a
reading nobody sees at `/3d`.

  bom-covered    every billed cold-core part against the body that realizes it
  bodies-clear   no two solids share volume
  routes-fit     no line meets a solid
  lines-apart    no line meets another line
  arcs-hold      every corner turns at the stock arc
  port-leads     every made-up end has a straight to receive the tube
  lane-census    what each lane carries, and at what storey
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = _hw.parent

DETAIL_MAX = 8
FOCUS_DETAIL_MAX = 24
# The axis this effort is on, in the order both surfaces lead with them.
FOCUS_IDS = ("bom-covered", "mounted")
# Two surfaces built to one nominal face meet at a sliver of this order.
TOUCH_VOLUME = 0.1


@dataclass
class Check:
    id: str
    label: str
    kind: str            # "gate" | "goal"
    status: str          # "pass" | "fail" | "warn"
    value: str
    target: str
    detail: list = field(default_factory=list)
    active: bool = True


def verdict(ok: bool) -> str:
    return "pass" if ok else "fail"


def score(check: Check) -> int:
    lo, hi = check.value.split("/")[0], check.value.split("/")[-1]
    try:
        done = int(re.findall(r"(\d+)", lo)[-1])
        total = int(re.findall(r"(\d+)", hi)[0])
    except (IndexError, ValueError):
        return 0
    return 0 if not total else round(100.0 * done / total)


@dataclass
class Scorecard:
    checks: list
    bends: list = field(default_factory=list)
    ports: list = field(default_factory=list)
    shapes: list = field(default_factory=list)
    mounts: list = field(default_factory=list)

    @property
    def gates_pass(self) -> bool:
        return all(c.status != "fail" for c in self.checks if c.kind == "gate")


def _source() -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(_repo),
                                capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        commit = ""
    return {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "commit": commit or None}


def to_dict(sc: Scorecard) -> dict:
    by_id = {c.id: c for c in sc.checks}
    prim = {d["component"]: d["primitive"] for d in sc.shapes}
    return {
        "gatesPass": sc.gates_pass,
        "placed": score(by_id["placed"]),
        "located": score(by_id["located"]),
        "shaped": score(by_id["shaped"]),
        "routed": score(by_id["routed"]),
        "held": score(by_id["held"]),
        "mounted": score(by_id["mounted"]),
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail),
             "active": c.active and c.id in FOCUS_IDS if c.kind == "goal" else c.active}
            for c in sc.checks
        ],
        "ports": sc.ports,
        "shapes": sc.shapes,
        "bends": sc.bends,
        "mounts": [{"component": n, "by": by, "held": h,
                    "kind": "placeholder" if prim.get(n) else "real"}
                   for n, by, h in sc.mounts],
        "source": _source(),
    }


def write(sc: Scorecard, step: Path) -> Path:
    out = step.parent / (step.stem + ".scorecard.json")
    out.write_text(json.dumps(to_dict(sc), indent=1) + "\n")
    return out


def report(sc: Scorecard) -> None:
    print("\nscorecard")
    for c in sc.checks:
        mark = {"pass": "OK  ", "fail": "FAIL", "warn": "    "}[c.status]
        print(f"  {mark} {c.id:14} {c.value:34} {c.label}")
        limit = FOCUS_DETAIL_MAX if c.id in FOCUS_IDS else DETAIL_MAX
        for line in c.detail[:limit]:
            print(f"         {line}")
        if len(c.detail) > limit:
            print(f"         … {len(c.detail) - limit} more")
    if sc.bends:
        print("\nlines")
        print(f"  {'line':18} {'grade':7} {'length':>8} {'reach':>8} {'detour':>7} "
              f"{'tightest':>9} corners")
        for d in sc.bends:
            det = d["need"]["detour"]
            reach = "—" if d["reach"] is None else f"{d['reach']:.1f}"
            print(f"  {d['id']:18} {str(d['grade'] or 'straight'):7} {d['length']:8.1f} "
                  f"{reach:>8} {'    — ' if det is None else f'{det:5.2f}x'} "
                  f"{d['radius']:9.2f} {len(d['corners'])}")
