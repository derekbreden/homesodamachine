"""Cut the guide's pictures from the funnel-mold solids.

Every figure in the two guides is one of these renders or an inline SVG drawn in the leaf
that carries it. The renders come from the same STEP files `funnel_mold.py` exports, through
the viewer the assembly cards use, so a camera here sees the shipped geometry and nothing else.

RUN BY HAND. NOT A STEP OF THE BUILD — `hardware/funnel-mold-guide/README.md` names what holds
that. This module lives under `tools/`, which `tools/bazel/trace_inputs.py` names in `ELSEWHERE`,
so no sweep traces it into a rule and no changed-path reading widens a slice to reach it.

    tools/cad-venv/bin/python tools/funnel-mold-guide/_art.py

Its output is committed. Re-run it when `funnel_mold.py` moves, then rebuild the guides with
`_build.py`.

Poses are Z-up (`--up 0,0,1`); the model's own frame puts the cavity's feet at Z=0 and the
assembled stack above it. `trim` crops to the navy field, so a panel in the page carries the
subject and no margin of its own.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
GUIDE = REPO_ROOT / "hardware" / "funnel-mold-guide"
ART = GUIDE / "art"
MOLD = "printed-parts/zone-c/funnel-mold/"
FUNNEL = "printed-parts/zone-c/funnel/"

NAVY = "#1a1a2e"
BIG = "1800x1350"
WIDE = "1900x1150"
DETAIL = "1500x1150"


def job(step: str, name: str, cam, **kw) -> dict:
    spec = {
        "step": step,
        "out": str(ART / f"{name}.png"),
        "cam": list(cam),
        "up": [0, 0, 1],
        "size": BIG,
        "bg": NAVY,
        "solid": True,
        "trim": True,
        # No contact shadow and no distance fade: the field stays flat navy, so a trimmed
        # frame sits on the page's own navy without a seam.
        "ground": False,
        "fog": False,
    }
    spec.update(kw)
    return spec


# The two halves are shown the way the hands meet them: the cavity from above, where it is
# poured into; the core from below, where its coated face points at the floor. `core-back`
# looks at the side that lies on the bed through its print and under the clamp board through
# the cure.
JOBS = [
    job(MOLD + "funnel-mold-assembly.step", "assembly-iso", (1, -1, 0.55), size=WIDE),
    job(MOLD + "funnel-mold-assembly.step", "assembly-cover", (1, -0.85, 0.42), size="2000x1250"),
    job(MOLD + "funnel-mold-cavity.step", "cavity-iso", (1, -1, 0.80)),
    job(MOLD + "funnel-mold-cavity.step", "cavity-bed", (1, -1, 0.30), size=WIDE),
    job(MOLD + "funnel-mold-core.step", "core-under", (1, -1, -0.55)),
    job(MOLD + "funnel-mold-core.step", "core-back", (1, -1, 0.85)),
    job(MOLD + "funnel-mold-finish-witness.step", "witness-finish", (1, -0.6, 0.42), size=DETAIL),
    job(MOLD + "funnel-mold-hardware-witness.step", "witness-hardware", (1, -1, 0.70), size=DETAIL),
    job(MOLD + "funnel-mold-guide-witness.step", "witness-blade", (1, -0.7, 0.50), size=DETAIL),
    # Details: `span` frames a region while the whole solid stays in the scene, so a close-up
    # is the same part in the same light.
    job(
        MOLD + "funnel-mold-assembly.step",
        "station-detail",
        (1, -0.55, 0.30),
        ortho=True,
        span=52,
        target=[119, 6, 78],
        size=DETAIL,
    ),
    job(
        MOLD + "funnel-mold-cavity.step",
        "spout-detail",
        (0.42, -0.42, 1),
        ortho=True,
        span=44,
        target=[0, 0, 34],
        size=DETAIL,
    ),
    job(
        MOLD + "funnel-mold-core.step",
        "socket-detail",
        (1, -1, -0.55),
        ortho=True,
        span=34,
        target=[0, 0, 34],
        size=DETAIL,
    ),
    # Framed on the corner of the brim ring the pour throat and its dish stand in; the vents
    # take the other three corners and the two mid-sides.
    job(
        MOLD + "funnel-mold-core.step",
        "ports-detail",
        (0.5, -0.5, 1),
        ortho=True,
        span=58,
        target=[-72, -72, 88],
        size=DETAIL,
    ),
    job(
        MOLD + "funnel-mold-core.step",
        "backing-air",
        (0.75, -1, 0.55),
        ortho=True,
        span=62,
        target=[62, -62, 86],
        size=DETAIL,
    ),
    job(FUNNEL + "funnel.step", "funnel-iso", (1, -1, 0.55), size=WIDE),
    job(FUNNEL + "funnel.step", "funnel-cover", (1, -0.9, 0.38), size="2000x1250"),
]


# Figures that name a body or cut through one. `render-view.js` carries the leaders, the
# per-body solid/ghost/x-ray sets and the clip planes; the poses above carry everything that
# only needs a camera. A clip leaves cut faces open, so these all clip on Z and look iso.
VIEWS = [
    (
        "station-labelled",
        [
            "--view", "iso",
            "--only", "jack-screw-*,square-nut-*,washer-*",
            "--ghost", "cavity,core",
            "--hide", "funnel,rod",
            "--label",
            "--caption", "Four jacks: nut in the core arm, screw tip on the washer",
        ],
    ),
    (
        "cast-in-place",
        [
            "--view", "iso",
            "--clip", "z:0,76",
            "--only", "cavity,funnel,rod",
            "--hide", "core,jack-screw-*,square-nut-*,washer-*",
            "--label",
            "--caption", "Cut at the parting plane: the cast funnel and the rod in the cavity",
        ],
    ),
    # The casting guide's cover: the same cut, without the leaders and the scale bar, which
    # are unreadable at cover size and read as noise on a shelf.
    (
        "cast-cover",
        [
            "--view", "iso",
            "--clip", "z:0,76",
            "--only", "cavity,funnel,rod",
            "--hide", "core,jack-screw-*,square-nut-*,washer-*",
            "--no-label", "--no-grid",
        ],
    ),
    (
        "mold-section",
        [
            "--view", "iso",
            "--clip", "z:0,90",
            "--only", "cavity,core,funnel,rod",
            "--hide", "jack-screw-*,square-nut-*,washer-*",
            "--label",
            "--caption", "Closed on the pour: cavity, silicone, rod, core",
        ],
    ),
]

VIEW_SIZE = "1700x1275"
# render-view burns a provenance block into the top-left corner: the source path, the camera,
# the clip, the hidden set. It is struck off the frame here — the leaders, the scale bar and
# the caption stay. The field behind it is flat navy, so the corner fills back to background.
LEGEND_PANEL = (13, 14, 29)
LEGEND_FIELD = (26, 26, 46)


def strike_legend(path: Path) -> None:
    from PIL import Image

    with Image.open(path) as handle:
        image = handle.convert("RGB")
    pixels = image.load()
    width, height = image.size
    right = bottom = 0
    for y in range(min(height, 400)):
        for x in range(min(width, 1200)):
            if pixels[x, y] == LEGEND_PANEL:
                right, bottom = max(right, x), max(bottom, y)
    if not bottom:
        return
    for y in range(0, bottom + 4):
        for x in range(0, right + 4):
            pixels[x, y] = LEGEND_FIELD
    image.save(path, optimize=True)


def main() -> int:
    ART.mkdir(exist_ok=True)
    manifest = ART / "_jobs.json"
    manifest.write_text(json.dumps(JOBS, indent=1) + "\n")
    posed = REPO_ROOT / "tools" / "render" / "render-step-posed.js"
    failed = subprocess.run(["node", str(posed), "--jobs", str(manifest)], check=False).returncode
    manifest.unlink(missing_ok=True)

    viewer = REPO_ROOT / "tools" / "render" / "render-view.js"
    for name, flags in VIEWS:
        code = subprocess.run(
            [
                "node", str(viewer),
                MOLD + "funnel-mold-assembly.step",
                str(ART / f"{name}.png"),
                *flags,
                "--size", VIEW_SIZE,
                "--bg", NAVY,
            ],
            check=False,
        ).returncode
        failed = failed or code
        if not code:
            strike_legend(ART / f"{name}.png")

    for spec in JOBS:
        out = Path(spec["out"])
        mark = " " if out.exists() else "MISSING"
        print(f"  {mark} {out.name:24s} {out.stat().st_size // 1024 if out.exists() else 0:5d} KB")
    for name, _ in VIEWS:
        out = ART / f"{name}.png"
        mark = " " if out.exists() else "MISSING"
        print(f"  {mark} {out.name:24s} {out.stat().st_size // 1024 if out.exists() else 0:5d} KB")
    return failed


if __name__ == "__main__":
    sys.exit(main())
