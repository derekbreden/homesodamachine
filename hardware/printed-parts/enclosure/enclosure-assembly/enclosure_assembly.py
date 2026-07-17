"""Kitchen Edition enclosure assembly — the four enclosure pieces wrapped
around the contents.

Combines the four `../enclosure/enclosure-*.step` pieces with the placed
parts from `_contents.build()`, the through-wall connector bodies from
`_contents.panel_bodies()`, the display, and the hopper funnel, in their
shared coordinates. The contents keep their per-part colors; the pieces are
translucent so the arrangement (and both seams) reads through them.

Export verifies the pack: every pair of placed solids (contents, panel bodies,
display, funnel) is intersected and any overlap past tolerance fails the run;
every solid is also intersected against the four enclosure pieces, catching
content that fouls a wall, a seam lip, or a cross-pin boss."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_py_comments
import _contents as contents

_ENCLOSURE_DIR = _repo / "hardware" / "printed-parts" / "enclosure" / "enclosure"
sys.path.insert(0, str(_ENCLOSURE_DIR))
import enclosure  # facet geometry, to seat the display in the housing

PIECES = {
    "enclosure_front_bottom": _ENCLOSURE_DIR / "enclosure-front-bottom.step",
    "enclosure_front_top":    _ENCLOSURE_DIR / "enclosure-front-top.step",
    "enclosure_back_bottom":  _ENCLOSURE_DIR / "enclosure-back-bottom.step",
    "enclosure_back_top":     _ENCLOSURE_DIR / "enclosure-back-top.step",
}
DISPLAY_STEP = _repo / "hardware" / "reference" / "waveshare-43b-display" / "waveshare-43b-display.step"
FUNNEL_STEP = _repo / "hardware" / "printed-parts" / "zone-c" / "hopper-funnel" / "hopper-funnel.step"
PIECE_COLORS = {
    "enclosure_front_bottom": cq.Color(0.85, 0.92, 1.00, 0.22),  # transparent PETG
    "enclosure_front_top":    cq.Color(0.88, 0.94, 1.00, 0.22),
    "enclosure_back_bottom":  cq.Color(0.80, 0.88, 0.98, 0.22),
    "enclosure_back_top":     cq.Color(0.83, 0.90, 0.99, 0.22),
}
DISPLAY_COLOR = cq.Color(0.10, 0.10, 0.12)      # the Waveshare 4.3B reference
FUNNEL_COLOR = cq.Color(0.95, 0.95, 0.97, 0.45) # translucent silicone funnel

CLASH_TOL = 1.0  # mm³ — face-contact booleans report ~0; anything past this fails


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


def _bb_overlap(a, b):
    return (min(a.xmax, b.xmax) > max(a.xmin, b.xmin) and
            min(a.ymax, b.ymax) > max(a.ymin, b.ymin) and
            min(a.zmax, b.zmax) > max(a.zmin, b.zmin))


def _check_pack(parts, pieces):
    """Pairwise intersection over every placed solid (bbox-prefiltered), plus
    every solid against the four enclosure pieces. Prints each overlap past
    CLASH_TOL and returns the count."""
    names = list(parts)
    bbs = {n: parts[n].BoundingBox() for n in names}
    clashes = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if not _bb_overlap(bbs[a], bbs[b]):
                continue
            v = parts[a].intersect(parts[b]).Volume()
            if v > CLASH_TOL:
                clashes += 1
                print(f"  CLASH {a} ∩ {b}: {v:.1f} mm³")
    for hname, hshape in pieces.items():
        hbb = hshape.BoundingBox()
        for n in names:
            if not _bb_overlap(hbb, bbs[n]):
                continue
            v = hshape.intersect(parts[n]).Volume()
            if v > CLASH_TOL:
                clashes += 1
                print(f"  CLASH {hname} ∩ {n}: {v:.1f} mm³")
    return clashes


def build():
    placed = dict(contents.build())
    placed.update(contents.panel_bodies())

    assy = cq.Assembly(name="kitchen-edition-enclosure-assembly")
    for name, path in PIECES.items():
        assy.add(cq.importers.importStep(str(path)).val(), name=name,
                 color=PIECE_COLORS[name])
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    assy.add(_placed_display(), name="display", color=DISPLAY_COLOR)
    funnel = cq.importers.importStep(str(FUNNEL_STEP)).val()
    assy.add(funnel, name="hopper-funnel", color=FUNNEL_COLOR)
    return assy


def main():
    placed = dict(contents.build())
    placed.update(contents.panel_bodies())
    solids = {n: s for n, (s, _c) in placed.items()}
    solids["display"] = _placed_display()
    solids["hopper-funnel"] = cq.importers.importStep(str(FUNNEL_STEP)).val()
    pieces = {n: cq.importers.importStep(str(p)).val() for n, p in PIECES.items()}

    inner_bbs = [s.BoundingBox() for s, _c in contents.build().values()]
    ix = max(b.xmax for b in inner_bbs) - min(b.xmin for b in inner_bbs)
    iy = max(b.ymax for b in inner_bbs) - min(b.ymin for b in inner_bbs)
    iz = max(b.zmax for b in inner_bbs)
    _i, outer, _yj, _cf = enclosure._dims()
    print(f"pack interior: {ix:.1f} × {iy:.1f} × {iz:.1f} mm "
          f"(box exterior {outer[1] - outer[0]:.1f} × {outer[3] - outer[2]:.1f} × "
          f"{outer[5] - outer[4]:.1f})")

    print("clearance check:")
    clashes = _check_pack(solids, pieces)
    if clashes:
        raise SystemExit(f"{clashes} clash(es) — pack does not close")
    print("  all pairs clear")

    assy = build()
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")

    # Pin the hand-typed placeholder dimensions in _contents.py's prose.
    substitute_py_comments(
        Path(contents.__file__),
        variables={
            "CONDENSER_AIRFLOW": f"{contents.CONDENSER_AIRFLOW:.4g} mm",
            "SEAFLO_DIMS": "{:g} x {:g} x {:g}".format(*contents.SEAFLO_DIMS),
        },
        expected_counts={
            "CONDENSER_AIRFLOW": 1,
            "SEAFLO_DIMS": 1,
        },
    )
    print("-> _contents.py")


if __name__ == "__main__":
    main()
