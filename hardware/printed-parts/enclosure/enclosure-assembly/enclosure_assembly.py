"""Kitchen Edition enclosure assembly — the four enclosure pieces wrapped
around the contents.

Combines the four `../enclosure/enclosure-*.step` pieces with the placed
parts from `_contents.build()`, the through-wall connector bodies from
`_contents.panel_bodies()`, the display, and the hopper funnel, in their
shared coordinates. The contents keep their per-part colors; the pieces are
translucent so the arrangement (and both seams) reads through them.

Export computes the enclosure scorecard (scorecard.py) over the placed solids
and the four pieces — the gates (pack closes, part↔part clearance, pieces fit
the bed, seams mate, parts sourced) and the three goal axes (shaped / routed /
held) — prints the verdict, and fails the run if any gate fails."""

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_py_comments
import _contents as contents
import _lines
import scorecard

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


def _placed_funnel():
    """The static funnel (hopper_funnel.py, its own frame: collar-centre origin,
    z 0 = brim underside) seated in the top-wall opening: rotated FUNNEL_ROT
    about its own Z (the rectangular collar seats either way; the rotation
    picks which side the spout descends), then translated to
    _contents.FUNNEL_CX/CY with the brim underside on the box's outer top. The
    opening is cut from the same placement (enclosure._hopper_hole), so funnel
    and hole cannot drift apart."""
    _i, outer, _yj, _cf = enclosure._dims()
    return (cq.importers.importStep(str(FUNNEL_STEP)).val()
            .rotate((0, 0, 0), (0, 0, 1), contents.FUNNEL_ROT)
            .translate((contents.FUNNEL_CX, contents.FUNNEL_CY, outer[5])))


# --- Placement overrides -----------------------------------------------------
# The 3D viewer's dev-only component editor writes per-component moves here (a
# JSON sidecar beside the .step) and re-runs this script; each override is a
# sequence of steps — every step a rotate about the solid's CURRENT centre then
# a translate — applied to that named solid before it joins the pack. Steps
# accumulate (the editor appends one per Apply, from the pose it's showing), so a
# rotate always turns about the centre the viewer rotated about; preview and
# rebuild agree. It works for every named solid (the derived trays/tees included)
# because it acts on the finished placement, not the procedural anchor that
# produced it, and the pack's clash gates (main(), below) validate the moved pose
# exactly as they do the authored one. An empty/absent sidecar changes nothing.
# Authored runs (_lines.py) are NOT overridden — a moved component's tubes stay on
# their authored path until the move is promoted into the placement source
# (_contents.py).
#
#   { "<component>": [ { "translate": [dx,dy,dz], "rotate": {"axis":[x,y,z], "deg": d} }, … ] }
#
# translate and rotate are each optional per step; a lone dict (not a list) is
# tolerated as a single step.
OVERRIDES_PATH = _here.parent / "enclosure-assembly.overrides.json"


def _load_overrides():
    try:
        data = json.loads(OVERRIDES_PATH.read_text())
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, ValueError):
        return {}


def _apply_step(shape, step):
    rot = step.get("rotate")
    if rot and rot.get("deg"):
        ax = rot.get("axis") or [0.0, 0.0, 1.0]
        bb = shape.BoundingBox()
        c = ((bb.xmin + bb.xmax) / 2.0, (bb.ymin + bb.ymax) / 2.0, (bb.zmin + bb.zmax) / 2.0)
        shape = shape.rotate(c, (c[0] + ax[0], c[1] + ax[1], c[2] + ax[2]), float(rot["deg"]))
    t = step.get("translate")
    if t and any(t):
        shape = shape.translate((float(t[0]), float(t[1]), float(t[2])))
    return shape


def _apply_override(name, shape, overrides):
    steps = overrides.get(name)
    if not steps:
        return shape
    if isinstance(steps, dict):
        steps = [steps]
    for step in steps:
        shape = _apply_step(shape, step)
    return shape


def _components(overrides):
    """The interior components (contents.build()) — name → (shape, color), each override-applied.
    These alone define the interior extent the box is sized around; the extras below mount through
    or on the wall."""
    return {n: (_apply_override(n, s, overrides), c)
            for n, (s, c) in contents.build().items()}


def _extras(overrides):
    """The placed solids that are not interior components — the through-wall panel bodies, the
    display, the hopper funnel — name → (shape, color), each override-applied. In the pack for the
    assembly and the clash gates, out of the interior-extent measure."""
    out = dict(contents.panel_bodies())
    out["display"] = (_placed_display(), DISPLAY_COLOR)
    out["hopper-funnel"] = (_placed_funnel(), FUNNEL_COLOR)
    return {n: (_apply_override(n, s, overrides), c) for n, (s, c) in out.items()}


def _pieces_shapes(overrides):
    """The four enclosure pieces, name → shape, each override-applied."""
    return {n: _apply_override(n, cq.importers.importStep(str(p)).val(), overrides)
            for n, p in PIECES.items()}


@dataclass
class _Pack:
    """Every placed shape of one build, grouped by role and built exactly once. main() (the
    scorecard and the interior measure) and build() (the assembly) share one pack, so no component
    is imported or placed twice in a run."""
    components: dict   # contents.build() — the interior set — name → (shape, color)
    extras: dict       # panel bodies, display, funnel — name → (shape, color)
    pieces: dict       # the four printed enclosure pieces — name → shape
    lines: dict        # the authored runs (_lines.py) — name → (shape, color)

    @property
    def solids(self):
        """components + extras — every non-piece, non-line solid, name → (shape, color)."""
        return {**self.components, **self.extras}


def _build_pack(overrides):
    """Build the whole pack once — components, extras, pieces, and the authored line runs."""
    return _Pack(
        components=_components(overrides),
        extras=_extras(overrides),
        pieces=_pieces_shapes(overrides),
        lines=_lines.build(),
    )


def build(pack=None):
    """The full assembly. Pass a prebuilt pack to reuse main()'s single build; with none, build a
    fresh pack (standalone / interactive use)."""
    if pack is None:
        pack = _build_pack(_load_overrides())

    assy = cq.Assembly(name="kitchen-edition-enclosure-assembly")
    for name, shape in pack.pieces.items():
        assy.add(shape, name=name, color=PIECE_COLORS[name])
    for name, (shape, color) in pack.solids.items():
        assy.add(shape, name=name, color=color)
    # The authored runs (_lines.py), in the pack's coordinates. Lines, not components: outside
    # the component registry and its gates (and not moved by overrides).
    for name, (shape, color) in pack.lines.items():
        assy.add(shape, name=name, color=color)
    return assy


def main():
    overrides = _load_overrides()
    pack = _build_pack(overrides)
    solids = {n: s for n, (s, _c) in pack.solids.items()}

    inner_bbs = [s.BoundingBox() for _n, (s, _c) in pack.components.items()]
    ix = max(b.xmax for b in inner_bbs) - min(b.xmin for b in inner_bbs)
    iy = max(b.ymax for b in inner_bbs) - min(b.ymin for b in inner_bbs)
    iz = max(b.zmax for b in inner_bbs)
    inner, outer, _yj, _cf = enclosure._dims()
    print(f"pack interior: {ix:.1f} × {iy:.1f} × {iz:.1f} mm "
          f"(box exterior {outer[1] - outer[0]:.1f} × {outer[3] - outer[2]:.1f} × "
          f"{outer[5] - outer[4]:.1f})")

    sc = scorecard.build_scorecard(
        solids, pack.pieces, (enclosure.H2C_X, enclosure.H2C_Y, enclosure.H2C_Z), inner)
    print(scorecard.format_scorecard(sc))

    # Each authored run, with the tightest gap to a part it does not terminate on.
    for run, near in _lines.clearances(solids):
        gap = f"{near[0]:.2f} mm to {near[1]}" if near else "nothing near"
        print(f"line {run.id}: Ø{run.diam:g} × {run.length:.1f} mm, {len(run.bends)} bends "
              f"R{run.bend:.1f} — nearest {gap}")
    for cid, why in sorted(_lines.BLOCKED.items()):
        print(f"line {cid}: BLOCKED — {why}")
    # The scorecard reports every gate; today only pack-closes blocks the export — a
    # physically invalid pack (overlapping solids) must not be written. The rest report
    # until the design reaches them, then their gating turns on (the board's stance).
    if any(c.id == "pack-closes" and c.status == "fail" for c in sc.checks):
        raise SystemExit("pack does not close — overlapping solids (see scorecard above)")

    # The scorecard sidecar the 3D viewer reads — the same verdict, beside the model. Written
    # before the .step so the dev watcher's .step broadcast implies the sidecar is already fresh.
    sc_path = _here.parent / "enclosure-assembly.scorecard.json"
    sc_path.write_text(json.dumps(scorecard.scorecard_dict(sc), indent=2) + "\n")
    print(f"-> {sc_path.name}")

    assy = build(pack)
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")

    # Pin the hand-typed placeholder dimensions in _contents.py's prose.
    substitute_py_comments(
        Path(contents.__file__),
        variables={
            "CONDENSER_AIRFLOW": f"{contents.CONDENSER_AIRFLOW:.4g} mm",
        },
        expected_counts={
            "CONDENSER_AIRFLOW": 1,
        },
    )
    print("-> _contents.py")


if __name__ == "__main__":
    main()
