#!/usr/bin/env python3
"""Render registered views of the closed shutoff and its braided supply."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "hardware"
OUT = HARDWARE / "install-guide/out/hose-scene"
ART = HARDWARE / "install-guide/assets"
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "quickstart/plumbing"))
from _cadq_export import _per_solid_color
import plumbing_scenes as plumbing


def build(attached=False):
    if attached:
        source = plumbing._direct_faucet_scene("hose-attached", valve_on=False)
    else:
        source = plumbing._base_scene(
            "hose-removed", valve_on=False, outlet_exposed=True)
        plumbing._add_faucet_supply(
            source,
            connector_base=(-24.0, plumbing.VALVE_AXIS_Y, 182.0),
            hose_points=(
                (-24.0, plumbing.VALVE_AXIS_Y, 213.0),
                (-25.0, 56.0, 237.0),
                (-34.0, 64.0, 281.0),
                (-42.0, 65.0, 340.0),
            ),
            free=True,
        )
    scene = cq.Assembly(name="hose-attached" if attached else "hose-removed")
    for child in source.children:
        if child.name != "finished-wall":
            scene.add(child)
    return scene


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    jobs = []
    for attached in (True, False):
        scene = build(attached)
        names = {child.name for child in scene.children}
        assert not any(name.startswith("tee-") for name in names)
        assert "white-quarter-inch-appliance-branch" not in names
        assert ("valve-open-waterway" in names) is not attached
        assert ("faucet-supply-free-gasket" in names) is not attached
        step = OUT / f"{scene.name}.step"
        _per_solid_color(scene).export(str(step))
        jobs.append(dict(
            step=str(step.relative_to(HARDWARE)), out=str(ART / f"{scene.name}.png"),
            cam=(1.05, 1.70, 0.62), target=(-6.0, 44.0, 144.0),
            span=86.0, size="1250x1150", up=(0, 0, 1),
            bg="#ffffff", transparent=True, solid=True,
            ortho=True, trim=False, ground=False, fog=False,
        ))
    subprocess.run(
        ["node", str(ROOT / "tools/render/render-step-posed.js"), "--jobs", "-"],
        cwd=ROOT, input=json.dumps(jobs), text=True, check=True,
    )
    print(ART)


if __name__ == "__main__":
    main()
