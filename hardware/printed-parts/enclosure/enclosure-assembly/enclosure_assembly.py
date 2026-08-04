"""Thin Edition enclosure assembly — the four enclosure pieces wrapped
around the contents.

Combines the four `../enclosure/enclosure-*.step` pieces with the placed
parts from `_contents.build()`, the through-wall connector bodies from
`_contents.panel_bodies()`, the display, and the hopper funnel, in their
shared coordinates. The contents keep their per-part colors; the pieces are
translucent so the arrangement (and both seams) reads through them.

Export computes the enclosure scorecard (scorecard.py) over the placed solids
and the four pieces — the gates (pack closes, part↔part clearance, pieces fit
the bed, seams mate, parts sourced) and the three goal axes (shaped / routed /
held) — and prints the verdict.

There is no failure exit. The .step and the scorecard sidecar are written whatever
the gates say, a pack that does not close carries its real overlapping geometry, and
`.githooks/pre-commit` reports the enclosure's verdict without gating on it."""

import hashlib
import json
import math
import os
import pickle
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
# An edition whose root IS the repo root is the default one; the rest are named by their dir.
# Matches web/lib/editions.js, which the render tool resolves `--edition` through.
_edition = "kitchen" if _repo == _tools.parent else _repo.name
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly
from docgen import substitute_md, substitute_py_comments
import _boxes
import _contents as contents
import _lines
import fresh
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
    PCB hole (`enclosure.display_centre_x` + display_body_offset). That carries its
    glass, which overhangs the body the opposite way, onto the centred counterbore."""
    outer = enclosure._dims().outer
    a, _n, origin, _dy, _dz = enclosure._facet_geom(outer)
    target = (
        enclosure.display_centre_x(outer) + enclosure.display_body_offset_x,
        origin[1] + enclosure.display_body_offset_slope * math.cos(a),
        origin[2] + enclosure.display_body_offset_slope * math.sin(a),
    )
    disp = cq.importers.importStep(str(DISPLAY_STEP)).val()
    return disp.rotate((0, 0, 0), (1, 0, 0), -45.0).translate(target)


# --- The editor's moves ------------------------------------------------------
# The 3D viewer's dev-only component editor drags a body and writes the move to a sidecar
# beside the .step, then re-runs this script. The sidecar and its schema belong to
# `_contents.MOVES_PATH`, and the PACK applies it: each move composes onto the seat its body
# took, at `place` time, so the body's own stations ride it and anything seated on it follows
# (`_placing.Pack`). Nothing is applied to a finished solid here — that is the one route by
# which metal could move without the routes and the gates hearing about it.
#
# The bodies below are the ones seated OUTSIDE that pack — the through-wall panel fittings,
# the display, the funnel, and the four printed pieces. A move naming one of them still moves
# its metal, so a drag is never silently dropped, but its stations do not ride: `_moved_apart`
# names any that are moved this way, at every build, rather than leaving it to be discovered.


def _step(shape, step):
    """One dragged step on a bare shape: a turn about the shape's own centre, then a shift."""
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


def _apart(name, shape, moves):
    """A move on a body the pack did not seat — metal only. See the block above."""
    steps = moves.get(name)
    if not steps:
        return shape
    for step in ([steps] if isinstance(steps, dict) else steps):
        shape = _step(shape, step)
    return shape


def _moved_apart(moves, pack):
    """The moved bodies whose stations did NOT ride, named at every build so the split between
    the two routes is never something the reader has to find out the hard way."""
    return sorted(n for n in moves if n not in pack.solids)


def _components():
    """The interior components (contents.build()) — name → (shape, color). These alone define
    the interior extent the box is sized around; the extras below mount through or on the wall.
    Already moved: the pack seated them, editor's move and all."""
    return dict(contents.build())


def _extras(moves):
    """The placed solids that are not interior components — the through-wall panel bodies, the
    display, the hopper funnel — name → (shape, color). In the pack for the assembly and the
    clash gates, out of the interior-extent measure."""
    out = dict(contents.panel_bodies())
    out["display"] = (_placed_display(), DISPLAY_COLOR)
    out["hopper-funnel"] = (contents.placed_funnel(), FUNNEL_COLOR)
    return {n: (_apart(n, s, moves), c) for n, (s, c) in out.items()}


def _pieces_shapes(moves):
    """The four enclosure pieces, name → shape."""
    return {n: _apart(n, cq.importers.importStep(str(p)).val(), moves)
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


def _build_pack(moves):
    """Build the whole pack once — components, extras, pieces, and the authored line runs."""
    return _Pack(
        components=_components(),
        extras=_extras(moves),
        pieces=_pieces_shapes(moves),
        lines=_lines.build(),
    )


def build(pack=None):
    """The full assembly. Pass a prebuilt pack to reuse main()'s single build; with none, build a
    fresh pack (standalone / interactive use)."""
    if pack is None:
        pack = _build_pack(contents._moves())

    assy = cq.Assembly(name="kitchen-edition-enclosure-assembly")
    for name, shape in pack.pieces.items():
        assy.add(shape, name=name, color=PIECE_COLORS[name])
    for name, (shape, color) in pack.solids.items():
        assy.add(shape, name=name, color=color)
    # The authored runs (_lines.py), in the pack's coordinates. Lines, not components: outside
    # the component registry and its gates. They are drawn to the pack's own stations, so a
    # dragged body's runs follow it — the seat it moved on is the seat `_lines` reads.
    for name, (shape, color) in pack.lines.items():
        assy.add(shape, name=name, color=color)
    return assy


# --- Scorecard cache ---------------------------------------------------------
# The component gates + audits (pack-closes clash, part↔part clearance, shaped, placed, located,
# seams, bed fit) are a pure function of the placed components — they never read the tube routes.
# So a build that only changed _lines.py (route iteration) recomputes the identical component
# verdict — ~40s of OCC booleans + distances — for nothing. This caches that verdict, keyed on what
# determines it: each placed solid's bounding box, plus the source that places and measures them
# (_contents.py, this file, enclosure.py, scorecard.py, the editor's moves) and the STEP files they
# import — but NOT _lines.py / _routing.py. On a hit the cheap _lines-dependent checks — the routed
# axis and the lines-clear + bend-radius gates — are recomputed fresh, so neither the routed % nor
# the tube-clash and bend-grade verdicts go stale. A miss or any error falls through to a full
# build_scorecard, so the pack-closes gate is never served stale.
_SCORECARD_CACHE_PATH = _here.parent / ".enclosure-assembly.scorecard-cache.pkl"


def _step_inputs():
    """Every STEP the pack imports — the four pieces, the display, the funnel, and each .step Path
    _contents declares (the component assemblies). A change to any of them invalidates the cache."""
    steps = set(PIECES.values()) | {DISPLAY_STEP, contents.FUNNEL_STEP}
    steps |= {v for v in vars(contents).values() if isinstance(v, Path) and v.suffix == ".step"}
    return sorted(steps)


def _bbox_key(bb):
    return tuple(round(v, 4) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax))


def _source_digest():
    """The sources that place and measure the pack, hashed AT IMPORT — the code that is
    actually about to run. Reading them later would hash whatever is on disk when the
    build ends, so a source edited while a build is in flight would key that build's
    verdict to code it never executed, and every later build would hit it."""
    h = hashlib.sha256()
    for p in (Path(contents.__file__), _here, Path(scorecard.__file__),
              Path(enclosure.__file__), contents.MOVES_PATH):
        h.update(b"PY:" + str(p).encode())
        h.update(p.read_bytes() if p.exists() else b"")
    # The declared connector set itself, not just the file that lists it. PORTS is what
    # the located axis reads, and its coordinates are resolved through modules that are
    # NOT in the list above — a foam-shell station comes from the cold core's own copper
    # plug stack. Moving a station inside the shared slot changes no bounding box and
    # rewrites no STEP, so nothing else in this key would move and the cached verdict
    # would keep reporting where that port used to be.
    h.update(b"PORTS:" + repr([(p.component, p.name, p.kind, p.pos, p.face, p.diam)
                               for p in scorecard.PORTS]).encode())
    return h.digest()


_SOURCE_DIGEST = _source_digest()


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
    h.update(_SOURCE_DIGEST)
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
                # build): the routed goal and the lines-clear + bend-radius gates. gates_pass is
                # refreshed too, since two of the three are gates.
                routed_ck, routed = scorecard.routed_check(solids)
                bend_ck, bend_rows = scorecard.bend_radius_check()
                fresh = {"routed": routed_ck, "bend-radius": bend_ck,
                         "lines-clear": scorecard.lines_clear_check(solids, pieces)}
                sc.checks = [fresh.get(c.id, c) for c in sc.checks]
                sc.routed = routed
                sc.bends = bend_rows
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
    moves = contents._moves()
    pack = _build_pack(moves)
    solids = {n: s for n, (s, _c) in pack.solids.items()}

    apart = _moved_apart(moves, contents.packed())
    if apart:
        print(f"moved apart from the pack — metal only, stations did not ride: "
              f"{', '.join(apart)}")

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
        # The pack is written whether or not it closes: an overlap is a thing to look at, and a
        # build that writes nothing leaves the change that caused it invisible and the sidecar
        # frozen at the last pack that happened to pass. The .step carries the real overlapping
        # geometry and the sidecar carries the failing verdict, which is what the pre-commit hook
        # and the viewer both read.
        print("NOT BUILD-READY — " + msg)

    # The scorecard sidecar the 3D viewer reads — the same verdict, beside the model. Written
    # before the .step so the dev watcher's .step broadcast implies the sidecar is already fresh.
    sc_path = _here.parent / "enclosure-assembly.scorecard.json"
    card = scorecard.scorecard_dict(sc)
    # What this card was built from, so a reader can tell whether it still describes the tree
    # without building one of its own: fresh.py, and the `source` block in the sidecar contract.
    card[fresh.STAMP_KEY] = fresh.stamp(_step_inputs() + [contents.MOVES_PATH])
    sc_path.write_text(json.dumps(card, indent=2) + "\n")
    print(f"-> {sc_path.name}")

    assy = build(pack)
    # Editor build of a clashing pack: render each overlap VOLUME as a bright solid named
    # `clash__a__b`, so the viewer's clash row can x-ray to the exact overlapping region (not just
    # the two whole parts). `a`/`b` match the scorecard's `a ∩ b` rows one-for-one; the ASCII name
    # (spaces/∩ don't survive a STEP round-trip cleanly) is what scorecard-3d.js reconstructs. Gone
    # the moment the pack is clean, and drawn only under the editor: each overlap body is another
    # solid to tessellate on export, and a wild move (or a shell mid-edit) can clash with
    # everything at once — 12 of them pushed the editor rebuild past 5 min. Every build writes the
    # clashing pack itself; the scorecard lists every clash in text, and rows past the cap fall
    # back to highlighting the two parts.
    if os.environ.get("HSM_EDITOR") and any(c.id == "pack-closes" and c.status == "fail" for c in sc.checks):
        for a, b, shape in scorecard.clash_solids(solids, pack.pieces, limit=8):
            try:
                assy.add(shape, name=f"clash__{a}__{b}", color=CLASH_COLOR)
            except Exception as e:  # a degenerate overlap body shouldn't sink the whole editor build
                print(f"  (skipped clash render {a} ∩ {b}: {e})")

    out = _here.parent / "enclosure-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")

    render_elevations(out)

    # The stations the authored runs swept, fed back into _lines.py's own prose so a corridor
    # is described by the numbers a tube was built along, not a second hand-kept copy of them.
    stations = _lines.lane_stations()
    if stations:
        # Every station reads once in _lines' own prose except the two that read in
        # _contents' instead — the front chain's, in the aft band comment, and the loft
        # tee's headroom, in the turn that lays its branch west.
        _in_contents = ("FRONT_CHAIN_GAP", "LOFT_TEE_HEADROOM")
        substitute_py_comments(Path(_lines.__file__), variables=stations,
                               expected_counts={k: 1 for k in stations
                                                if k not in _in_contents})
        print("-> _lines.py")
        # The junction bay's fence in _contents.py names the two bands that pin it, the aft
        # band's names its own forward chain, and Y-F's turn names what closes the column over
        # it; those figures live in the same stations dict, so each fence is described by the
        # numbers the tubes were built along too.
        substitute_py_comments(Path(contents.__file__), variables=stations,
                               expected_counts={"OUTLET_LANE": 1, "FRONT_CHAIN_GAP": 1,
                                                "LOFT_TEE_HEADROOM": 1})
        print("-> _contents.py")
        # water-5's cut instruction quotes the run it is cutting — two legs, the lean the
        # first leaves its collet on, the arc the corner between them turns at, and what the
        # deck leaves between this bore and reservoir B's riser. The builder reads the same
        # figures the tube was drawn along.
        substitute_md(_repo / "hardware" / "assembly" / "internal-plumbing.md",
                      variables=stations,
                      expected_counts={"W5_LEG": 1, "W5_FALL": 1, "W5_LEAN": 1,
                                       "W5_RISER_GAP": 1, "LLDPE_MIN_BEND": 1})
        print("-> internal-plumbing.md")


# The three orthographic elevations, written beside the STEP as `enclosure-assembly.<view>.png`.
#
# The `.step.png` the export already writes is a grid thumbnail: one small isometric composite,
# at the size a browsing card wants. Isometric is the projection a coordinate cannot be read in,
# and at that size a fitting's clocking is not visible at all — so an arrangement has, until now,
# had no picture anyone could read it off. These are what a drawing is: plan, front and right,
# each on a millimetre grid with numbered ticks and a scale bar measured through the projection
# actually used, with the four printed pieces x-rayed so the pack reads through the shell rather
# than being hidden by it.
#
# The set costs one viewer boot. Parsing a 20 MB STEP is the whole expense of a render; moving
# the camera and recomposing is milliseconds, which is what `--views` exists for.
ELEVATIONS = "top,front,right"


def render_elevations(step: Path) -> None:
    """Write one elevation per ELEVATIONS view beside `step`.

    Best-effort, like the thumbnail hook it sits beside: a drawing that fails to render must
    never take an export with it, and `HSM_SKIP_VIEWS` drops it outright for a build that only
    Skipped when the STEP is byte-identical to the one these elevations were last drawn from.
    Parsing it is the whole expense, and a build that moved no body writes the same bytes — a
    comment, a rename, a registry note, a docgen writeback all land here with the geometry
    where it was. The stamp is the STEP's own digest beside the PNGs; delete it, or any one of
    them, to draw again."""
    if os.environ.get("HSM_SKIP_VIEWS"):
        return
    stamp = step.with_name(f".{step.stem}.views.sha")
    drawn = [step.with_suffix("").with_suffix(f".{v}.png") for v in ELEVATIONS.split(",")]
    digest = hashlib.sha256(step.read_bytes()).hexdigest()
    try:
        if (stamp.read_text().strip() == digest
                and all(p.is_file() for p in drawn)):
            print(f"  (elevations unchanged: {step.name} is the geometry they were drawn from)")
            return
    except OSError:
        pass
    node = shutil.which("node")
    tool = _tools / "render" / "render-view.js"
    if node is None or not tool.is_file():
        why = "node not on PATH" if node is None else "render tool missing"
        print(f"  (elevations skipped: {why})")
        return
    # render-view takes the step path relative to the edition's content root, and names each
    # output `<stem>.<view>.png` — so the stem given here must not be the .step.png thumbnail's.
    step_rel = step.relative_to(_repo / "hardware")
    stem = step.with_suffix(".png")
    try:
        r = subprocess.run(
            [node, str(tool), str(step_rel), str(stem),
             "--edition", _edition, "--views", ELEVATIONS, "--ortho",
             "--xray", "enclosure_*", "--size", "1600x1200"],
            cwd=str(_tools.parent), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            timeout=900, check=False)
        if r.returncode:
            print(f"  (elevations skipped: render-view exited {r.returncode})")
            return
    except Exception as exc:
        print(f"  (elevations skipped: {exc})")
        return
    try:
        stamp.write_text(digest + "\n")
    except OSError:
        pass
    for v in ELEVATIONS.split(","):
        print(f"-> {stem.with_suffix('').name}.{v}.png")


if __name__ == "__main__":
    main()
