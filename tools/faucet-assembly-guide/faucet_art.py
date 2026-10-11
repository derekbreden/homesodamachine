"""Render the faucet guide's component and section pictures by hand.

The accepted lever and current shell/thimble STEPs supply the visible shapes.
Tube proxies use the documented diameters; they are illustrative lengths.
No assembled lever pose is invented. The guide draws the observed lever
motion separately as an explicitly schematic sequence.

    tools/cad-venv/bin/python tools/faucet-assembly-guide/faucet_art.py

This manual document tool is outside the appliance build and publish paths.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "hardware"
GUIDE = HARDWARE / "faucet-assembly-guide"
ART = GUIDE / "art"
sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import _per_solid_color

FAUCET = HARDWARE / "printed-parts/faucet"
ACCENT = cq.Color(0.91, 0.34, 0.18)
STOCK = cq.Color(0.17, 0.18, 0.20)
STEEL = cq.Color(0.56, 0.59, 0.63)
BLUE = cq.Color(0.09, 0.29, 0.82)


def read(path):
    return cq.importers.importStep(str(path))


def section(shape):
    """Open the positive-X half; use the source part's exact internal faces."""
    cutter = cq.Workplane("XY").box(500, 1000, 1000).translate((250, 0, 0))
    return shape.cut(cutter)


def tube(z0, length, y=0):
    return (cq.Workplane("XY", origin=(0, y, z0))
            .circle(9.525 / 2).circle(6.35 / 2).extrude(length))


def lever():
    a = cq.Assembly(name="accepted-lever")
    a.add(read(FAUCET / "lever-replica/lever-replica.step"), color=ACCENT)
    return a


def sleeve():
    a = cq.Assembly(name="sleeve-on-tube-outside-donor")
    a.add(section(read(FAUCET / "tpu-o-ring/tpu-o-ring.step")), color=ACCENT)
    # The tube is poised above the open mouth, along its actual insertion axis.
    a.add(section(tube(23.6, 25)), color=STOCK)
    return a


def donor():
    a = cq.Assembly(name="bare-metal-donor-and-sleeved-tube")
    src = HARDWARE / "reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step"
    a.add(section(read(src)), color=STEEL)
    sleeve = read(FAUCET / "tpu-o-ring/tpu-o-ring.step").translate((0, 8.75, 51))
    a.add(section(sleeve), color=ACCENT)
    # Tube end is on the cap. The source sleeve has interference and is compliant;
    # cutting the tube by the source sleeve keeps that overlap out of the picture.
    a.add(section(tube(53.1, 38, 8.75).cut(sleeve)), color=STOCK)
    return a


def shell():
    a = cq.Assembly(name="current-shell-base-section")
    a.add(section(read(FAUCET / "faucet-shell/faucet-shell-base.step")), color=STOCK)
    return a


def tip():
    a = cq.Assembly(name="current-shared-tip-section")
    a.add(section(read(FAUCET / "faucet-shell/faucet-shell-tip.step")), color=STOCK)
    return a


SCENES = {
    "accepted-lever": (lever, (0.8, -1.0, -0.8), (0, 1, 0)),
    "sleeve-on-tube": (sleeve, (1.0, -0.75, 0.25), (0, 0, 1)),
    "sleeved-tube-to-donor": (donor, (1.0, -0.8, 0.3), (0, 0, 1)),
    "shell-base-section": (shell, (1.0, -0.3, 0.18), (0, 0, 1)),
    "shared-tip-section": (tip, (1.0, -0.5, 0.45), (0, 0, 1)),
}


def render(names):
    ART.mkdir(parents=True, exist_ok=True)
    (GUIDE / "out").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="faucet-art-", dir=GUIDE / "out") as scratch:
        jobs = []
        for name in names:
            build, cam, up = SCENES[name]
            step = Path(scratch) / (name + ".step")
            _per_solid_color(build()).export(str(step))
            jobs.append({"step": str(step.relative_to(HARDWARE)),
                         "out": str(ART / (name + ".png")),
                         "cam": cam, "up": up, "size": "1500x1500",
                         "bg": "#ffffff", "transparent": True,
                         "trim": True, "solid": True, "ortho": True,
                         "ground": False, "fog": False})
        subprocess.run(["node", str(ROOT / "tools/render/render-step-posed.js"),
                        "--jobs", "-"], input=json.dumps(jobs), text=True,
                       cwd=ROOT, check=True)


if __name__ == "__main__":
    render(sys.argv[1:] or list(SCENES))
