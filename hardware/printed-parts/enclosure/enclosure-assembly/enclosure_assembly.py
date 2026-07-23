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

import hashlib
import json
import math
import os
import pickle
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
import _boxes
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
PIECE_COLORS = {
    "enclosure_front_bottom": cq.Color(0.85, 0.92, 1.00, 0.22),  # transparent PETG
    "enclosure_front_top":    cq.Color(0.88, 0.94, 1.00, 0.22),
    "enclosure_back_bottom":  cq.Color(0.80, 0.88, 0.98, 0.22),
    "enclosure_back_top":     cq.Color(0.83, 0.90, 0.99, 0.22),
}
DISPLAY_COLOR = cq.Color(0.10, 0.10, 0.12)      # the Waveshare 4.3B reference
FUNNEL_COLOR = cq.Color(0.95, 0.95, 0.97, 0.45) # translucent silicone funnel
CLASH_COLOR = cq.Color(1.00, 0.12, 0.20, 1.00)  # editor-only: the overlap volume of a clashing pack


def _placed_display():
    """The display reference seated in the facet housing: rotated −45° about X so
    its −Y screen faces the facet normal, then translated so the body lands on the
    PCB hole (facet center + display_body_offset). That carries its glass, which
    overhangs the body the opposite way, onto the centered counterbore."""
    outer = enclosure._dims().outer
    a, _n, origin, _dy, _dz = enclosure._facet_geom(outer)
    fcx = outer[0] + enclosure.display_facet_x / 2.0
    target = (
        fcx + enclosure.display_body_offset_x,
        origin[1] + enclosure.display_body_offset_slope * math.cos(a),
        origin[2] + enclosure.display_body_offset_slope * math.sin(a),
    )
    disp = cq.importers.importStep(str(DISPLAY_STEP)).val()
    return disp.rotate((0, 0, 0), (1, 0, 0), -45.0).translate(target)


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
    out["hopper-funnel"] = (contents.placed_funnel(), FUNNEL_COLOR)
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


# --- Scorecard cache ---------------------------------------------------------
# The component gates + audits (pack-closes clash, part↔part clearance, shaped, placed, located,
# seams, bed fit) are a pure function of the placed components — they never read the tube routes.
# So a build that only changed _lines.py (route iteration) recomputes the identical component
# verdict — ~40s of OCC booleans + distances — for nothing. This caches that verdict, keyed on what
# determines it: each placed solid's bounding box, plus the source that places and measures them
# (_contents.py, this file, enclosure.py, scorecard.py, the overrides) and the STEP files they
# import — but NOT _lines.py / _routing.py. On a hit the cheap _lines-dependent checks — the routed
# axis and the lines-clear gate — are recomputed fresh, so neither the routed % nor the tube-clash
# verdict goes stale. A miss or any error falls through to a full build_scorecard, so the
# pack-closes gate is never served stale.
_SCORECARD_CACHE_PATH = _here.parent / ".enclosure-assembly.scorecard-cache.pkl"


def _step_inputs():
    """Every STEP the pack imports — the four pieces, the display, the funnel, and each .step Path
    _contents declares (the component assemblies). A change to any of them invalidates the cache."""
    steps = set(PIECES.values()) | {DISPLAY_STEP, contents.FUNNEL_STEP}
    steps |= {v for v in vars(contents).values() if isinstance(v, Path) and v.suffix == ".step"}
    return sorted(steps)


def _bbox_key(bb):
    return tuple(round(v, 4) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax))


def _scorecard_cache_key(pack, inner):
    """A content key for the component verdict: solid + piece bounding boxes, the inner extent, the
    source files that place and measure them, and the STEP files they import — everything the verdict
    depends on except the routes, which it does not read."""
    h = hashlib.sha256()
    for name in sorted(pack.solids):
        h.update(repr((name, _bbox_key(_boxes.boxed(pack.solids[name][0])))).encode())
    for name in sorted(pack.pieces):
        h.update(repr((name, _bbox_key(_boxes.boxed(pack.pieces[name])))).encode())
    h.update(repr(tuple(round(v, 4) for v in inner)).encode())
    for p in (Path(contents.__file__), _here, Path(scorecard.__file__), Path(enclosure.__file__), OVERRIDES_PATH):
        h.update(b"PY:" + str(p).encode())
        h.update(p.read_bytes() if p.exists() else b"")
    for p in _step_inputs():
        st = p.stat()
        h.update(b"STEP:" + str(p).encode() + repr((st.st_mtime_ns, st.st_size)).encode())
    return h.hexdigest()


def _cached_scorecard(pack, pieces, bed, inner):
    """build_scorecard, reusing the cached component verdict when the components are unchanged and
    recomputing the _lines-dependent checks (the routed axis + the lines-clear gate). Fail-safe: a
    miss or any error falls through to a full build_scorecard, so the pack-closes gate is never
    served stale."""
    solids = {n: s for n, (s, _c) in pack.solids.items()}
    try:
        key = _scorecard_cache_key(pack, inner)
        if _SCORECARD_CACHE_PATH.exists():
            blob = pickle.loads(_SCORECARD_CACHE_PATH.read_bytes())
            if blob.get("key") == key:
                sc = blob["scorecard"]
                # The _lines-dependent checks, recomputed fresh (route work changes them every
                # build): the routed goal and the lines-clear gate. gates_pass is refreshed too,
                # since lines-clear is a gate.
                routed_ck, routed = scorecard.routed_check(solids)
                fresh = {"routed": routed_ck,
                         "lines-clear": scorecard.lines_clear_check(solids, pieces)}
                sc.checks = [fresh.get(c.id, c) for c in sc.checks]
                sc.routed = routed
                sc.gates_pass = all(c.status == "pass" for c in sc.checks if c.kind == "gate")
                return sc
        sc = scorecard.build_scorecard(solids, pieces, bed, inner)
        tmp = _SCORECARD_CACHE_PATH.with_suffix(".pkl.tmp")
        tmp.write_bytes(pickle.dumps({"key": key, "scorecard": sc}))
        os.replace(tmp, _SCORECARD_CACHE_PATH)
        return sc
    except Exception:
        return scorecard.build_scorecard(solids, pieces, bed, inner)


def main():
    overrides = _load_overrides()
    pack = _build_pack(overrides)
    solids = {n: s for n, (s, _c) in pack.solids.items()}

    inner_bbs = [_boxes.boxed(s) for _n, (s, _c) in pack.components.items()]
    ix = max(b.xmax for b in inner_bbs) - min(b.xmin for b in inner_bbs)
    iy = max(b.ymax for b in inner_bbs) - min(b.ymin for b in inner_bbs)
    iz = max(b.zmax for b in inner_bbs)
    box = enclosure._dims()
    inner, outer = box.inner, box.outer
    print(f"pack interior: {ix:.1f} × {iy:.1f} × {iz:.1f} mm "
          f"(box exterior {outer[1] - outer[0]:.1f} × {outer[3] - outer[2]:.1f} × "
          f"{outer[5] - outer[4]:.1f})")

    sc = _cached_scorecard(
        pack, pack.pieces, (enclosure.H2C_X, enclosure.H2C_Y, enclosure.H2C_Z), inner)
    print(scorecard.format_scorecard(sc))

    for cid, why in sorted(_lines.BLOCKED.items()):
        print(f"line {cid}: BLOCKED — {why}")
    # pack-closes and lines-clear are the two gates that block the export: a physically invalid pack
    # (two solids overlapping, or a routed tube driving through one) must never land as the committed
    # .step. The rest report until the design reaches them, then their gating turns on (the board's
    # stance).
    blocking = [c for c in sc.checks if c.id in ("pack-closes", "lines-clear") and c.status == "fail"]
    if blocking:
        # Name the offending pairs, not just the gate label — this line is all the dev-server log and
        # the editor panel show, so "pack does not close" without "fluid-11 ∩ tee-y-c: 342 mm³" is a
        # dead end. The full list is in the scorecard (terminal block above + the viewer's drill-down).
        parts = []
        for c in blocking:
            row = c.label
            if c.detail:
                extra = len(c.detail) - 8
                row += ": " + "; ".join(c.detail[:8]) + (f"; +{extra} more" if extra > 0 else "")
            parts.append(row)
        msg = " | ".join(parts) + "  (see scorecard)"
        # A headless / committed build must NEVER write an invalid pack, so it hard-stops here. But
        # HSM_EDITOR (the dev component editor, web/dev-server) is exactly where you drag a part to
        # SEE where it collides — a build that refuses to write leaves nothing to look at, and the
        # move appears to do nothing. So under the editor we write it anyway: the .step carries the
        # real overlapping geometry (the move is visible and survives a refresh) and the sidecar
        # records the failing verdict (gatesPass=false). The pre-commit gate reads that sidecar and
        # blocks the commit — an invalid pack can be inspected but can never land.
        if not os.environ.get("HSM_EDITOR"):
            raise SystemExit(msg)
        print("NOT BUILD-READY — " + msg + "  (written anyway for the editor)")

    # The scorecard sidecar the 3D viewer reads — the same verdict, beside the model. Written
    # before the .step so the dev watcher's .step broadcast implies the sidecar is already fresh.
    sc_path = _here.parent / "enclosure-assembly.scorecard.json"
    sc_path.write_text(json.dumps(scorecard.scorecard_dict(sc), indent=2) + "\n")
    print(f"-> {sc_path.name}")

    assy = build(pack)
    # Editor build of a clashing pack: render each overlap VOLUME as a bright solid named
    # `clash__a__b`, so the viewer's clash row can x-ray to the exact overlapping region (not just
    # the two whole parts). `a`/`b` match the scorecard's `a ∩ b` rows one-for-one; the ASCII name
    # (spaces/∩ don't survive a STEP round-trip cleanly) is what scorecard-3d.js reconstructs. Gone
    # the moment the pack is clean, and never in a headless build (it hard-stops before here).
    # Capped: each overlap body is another solid to tessellate on export, and a wild move (or a
    # shell mid-edit) can clash with everything at once — 12 of them pushed the editor rebuild past
    # 5 min. The scorecard still lists every clash in text; rows past the cap just fall back to
    # highlighting the two parts.
    if os.environ.get("HSM_EDITOR") and any(c.id == "pack-closes" and c.status == "fail" for c in sc.checks):
        for a, b, shape in scorecard.clash_solids(solids, pack.pieces, limit=8):
            try:
                assy.add(shape, name=f"clash__{a}__{b}", color=CLASH_COLOR)
            except Exception as e:  # a degenerate overlap body shouldn't sink the whole editor build
                print(f"  (skipped clash render {a} ∩ {b}: {e})")

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

    # Same for _lines.py: the nozzle-outlet lanes' stations are derived from the pack, so the
    # prose quoting them is fed from the runs rather than typed alongside them.
    substitute_py_comments(
        Path(_lines.__file__),
        variables=_lines.lane_stations(),
        expected_counts={
            "NOZ_DECK_Z": 2, "NOZ_LANE_OUTER_X": 1, "NOZ_LANE_INNER_X": 1,
            "NOZ_POCKET_STEP": 1,
        },
    )
    print("-> _lines.py")


if __name__ == "__main__":
    main()
