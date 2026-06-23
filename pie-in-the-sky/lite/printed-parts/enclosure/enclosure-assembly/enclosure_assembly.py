"""Lite Edition enclosure assembly — the two enclosure halves wrapped around the
contents.

Combines `../enclosure/enclosure-front.step` and `enclosure-back.step` with the
placed parts from `_contents.build()` in their shared coordinates, the display
reference seated in the facet housing, and the hopper funnel seated in the top
opening. The contents keep their per-part colors; the halves are translucent so
the arrangement (and the front↔back split) reads through them.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_assembly
import _contents as contents

_ENCLOSURE_DIR = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "enclosure" / "enclosure"
sys.path.insert(0, str(_ENCLOSURE_DIR))
import enclosure  # facet geometry, to seat the display in the housing

FRONT_STEP = _ENCLOSURE_DIR / "enclosure-front.step"
BACK_STEP = _ENCLOSURE_DIR / "enclosure-back.step"
DISPLAY_STEP = _repo / "hardware" / "reference" / "waveshare-43b-display" / "waveshare-43b-display.step"
FUNNEL_STEP = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "funnel" / "funnel.step"
FRONT_COLOR = cq.Color(0.85, 0.92, 1.00, 0.22)  # transparent PETG, front half
BACK_COLOR = cq.Color(0.80, 0.88, 0.98, 0.22)   # transparent PETG, back half
DISPLAY_COLOR = cq.Color(0.10, 0.10, 0.12)      # the Waveshare 4.3B reference
FUNNEL_COLOR = cq.Color(0.92, 0.88, 0.55, 0.45) # translucent pale, hollow reads


def _placed_display():
    """The display reference seated in the facet housing: rotated −45° about X so
    its −Y screen faces the facet normal, then translated so the body lands on the
    PCB hole (facet center + display_body_offset). That carries its glass, which
    overhangs the body the opposite way, onto the centered counterbore."""
    _i, outer, _yj, _cf = enclosure._dims()
    a, _n, origin, _dy, _dz = enclosure._facet_geom(outer)
    fcx = outer[0] + enclosure.display_facet_x / 2.0
    target = (
        fcx + enclosure.display_body_offset_x,
        origin[1] + enclosure.display_body_offset_slope * math.cos(a),
        origin[2] + enclosure.display_body_offset_slope * math.sin(a),
    )
    disp = cq.importers.importStep(str(DISPLAY_STEP)).val()
    return disp.rotate((0, 0, 0), (1, 0, 0), -45.0).translate(target)


def build():
    placed = contents.build()
    front = cq.importers.importStep(str(FRONT_STEP)).val()
    back = cq.importers.importStep(str(BACK_STEP)).val()

    assy = cq.Assembly(name="lite-enclosure-assembly")
    assy.add(front, name="enclosure_front", color=FRONT_COLOR)
    assy.add(back, name="enclosure_back", color=BACK_COLOR)
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    assy.add(_placed_display(), name="display", color=DISPLAY_COLOR)
    funnel = cq.importers.importStep(str(FUNNEL_STEP)).val()
    assy.add(funnel, name="hopper-funnel", color=FUNNEL_COLOR)
    return assy


def _report_display_clear(placed, display):
    """Content must clear the SEATED display, not just the shell housing — the
    Waveshare PCB juts into the box behind the facet, deeper than the cavity, so a
    content-vs-shell check alone misses a tray driven up into it."""
    worst, who = 0.0, None
    for name, (shape, _c) in placed.items():
        v = shape.intersect(display).Volume()
        if v > worst:
            worst, who = v, name
    tag = "CLEAR" if worst < 1.0 else f"CLASH — {who}"
    print(f"  content vs display: {worst:.1f} mm³  ({tag})")


def main():
    assy = build()
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")
    _report_display_clear(contents.build(), _placed_display())


if __name__ == "__main__":
    main()
