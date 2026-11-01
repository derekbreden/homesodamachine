"""Pictures of payloads through `hsm-render`, the renderer `hsm render` keeps in its daemon.

A job is a dict of the keys `hsm render --jobs` takes (tools/hsm/render/src/job.rs): a `step`
under hardware/ and an `out`, and the camera, frame and look of the picture. What is drawn is the
step's payload, `<step>.mesh`, so a scene exported to draw is written with one
(`_cadq_export._write_mesh_payload`). A run's jobs go in one call, which keeps the device and
model warm between its pictures.

THE PROGRAM IS BUILT FROM THIS CHECKOUT, as `_rust_part` builds a part's, and runs as a child of
this process. A picture a build action draws then follows the
renderer's sources, which the trace keeps from the program's dep-info, and the finishes it reads
beside the payload, `web/public/finishes.json`, kept here.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import _rust_part

ROOT = Path(__file__).resolve().parents[2]
FINISHES = ROOT / "web" / "public" / "finishes.json"


def render(jobs: list[dict], root: Path = ROOT, *, reports: bool = False) -> list[dict] | None:
    """Draw every job against the checkout at `root`. A picture that fails fails the run, after
    the others are drawn."""
    import _run_slots
    program = _rust_part.program("render", "hsm-render")
    _rust_part._READ_TARGETS.add(_rust_part._relative(FINISHES))
    result = subprocess.run([str(program), "--root", str(root), "--jobs", "-",
                             *(["--json"] if reports else [])],
                            input=json.dumps(jobs), text=True, check=True,
                            stdout=subprocess.PIPE if reports else None,
                            **_run_slots.subprocess_kwargs())
    return json.loads(result.stdout) if reports else None
