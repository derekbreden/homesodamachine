"""What one build knows, written down so the readers do not each build it again.

    tools/cad-venv/bin/python hardware/scripts/_facts.py            # write the artifact
    tools/cad-venv/bin/python hardware/scripts/_facts.py --check    # exit 2 if it moved
    tools/cad-venv/bin/python hardware/scripts/_facts.py selftest

    import _facts
    f = _facts.read()
    f.box.outer                      # the Box, field for field
    f.body("compressor").box         # a placed body's bounding box
    f.run("fluid-18").length         # a drawn run, measured
    f.port("bulkhead-carb", "tube-in").pos
    f.check("clearance-floor").status

THE DOC DRIVERS WANT NUMBERS, NOT SOLIDS. Of the figures they substitute, the overwhelming
majority is arithmetic over module constants and needs no geometry at all; most of the rest
is already in `enclosure-assembly.scorecard.json`, which carries every placed body's boxes,
every port's world position, every run's length and corners, and the whole fastening table.
What is left is the handful this file adds — the `Box` the walls are cut from, the wall
bores, the printed pieces' own boxes, a named face, a carried point, and a few exact
distances between declared pairs.

So a driver reads two files and stands no machine. `enclosure-assembly.scorecard.json` is
written by the assembly's own run; this artifact is written beside it.

THE DIGEST RIDES WITH THE VALUES. `sources` is the same reading the scorecard carries — the
digest of every file the drawing reads — so a reader that has the artifact can still answer
"was this made from the tree as it now stands" without importing the CAD.
"""

import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = _HERE.parent.parent
_ROOT = _HW.parent

for _p in (_HW / "scripts", _HW / "manifold-layout", _HW / "printed-parts" / "enclosure" / "enclosure", _HW / "reference" / "digiten-flow-sensor"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

ARTIFACT = _HW / "manifold-layout" / "enclosure-assembly.facts.json"
SCORECARD = _HW / "manifold-layout" / "enclosure-assembly.scorecard.json"
SCHEMA = 1

# The pairs whose exact distance a document states and the card does not carry. The card
# reports a pair only when it closes to within its own `REPORT_NEAR`, so a sentence naming a
# gap wider than that floor has nothing to read, and takes it here instead.
#
# A pair under the floor is already in `checks[clearance-floor].detail`, so it belongs to the
# reader rather than to this list. NAMES ARE THE PLACED BODIES'; a run is not one of them,
# and a pair naming a run raises here rather than going quietly missing from the artifact.
DECLARED_GAPS = (
    ("coil-v-a", "coil-v-b", 32.0),
)


def _plain(v):
    """A value as JSON holds it. Namedtuples keep their field names; anything this does not
    recognise raises, so a Box that grows a field of a new kind is a failure here and not a
    row that quietly goes missing downstream."""
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if hasattr(v, "_asdict"):
        return {k: _plain(x) for k, x in v._asdict().items()}
    if isinstance(v, dict):
        return {str(k): _plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set, frozenset)):
        return [_plain(x) for x in v]
    if hasattr(v, "x") and hasattr(v, "y") and hasattr(v, "z"):        # a cq Vector
        return [float(v.x), float(v.y), float(v.z)]
    raise TypeError(f"{type(v).__name__} has no plain form — teach `_plain` about it")


def gather():
    """Every fact this file adds, off ONE build of the machine."""
    import _boxes
    import _clearing
    import enclosure_assembly as ea
    import enclosure as _enc
    import _realized

    a, p, box = ea.machine()
    whole = ea.build_enclosure_assembly()
    solids = {n: s for n, (s, _c) in ea._solids(whole).items()}

    # AT THE PRECISION THE DRAWING HAD. The card rounds a length for reading, and a document
    # that rounds again off that reads a different last digit than the machine drew — so the
    # runs are carried here unrounded and the card's rows stay what they are, a reading.
    runs = [{"id": r.id, "frm": r.frm, "to": r.to,
             "length": float(r.length), "corners": len(r.bends)}
            for r in getattr(whole, "runs", ())]

    pieces, _rest = _enc.build_pieces(box)
    piece_boxes = {}
    for name, wp in pieces.items():
        bb = _boxes.boxed(wp.val() if hasattr(wp, "val") else wp)
        piece_boxes[name] = {"box": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax]}

    union = ea.back_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
    co2 = ea.co2_wall_port(a.co2_inlet_carry)

    gaps = {}
    for x, y, horizon in DECLARED_GAPS:
        missing = [n for n in (x, y) if n not in solids]
        if missing:
            raise KeyError(f"{', '.join(missing)} is not a placed body, so no gap can be taken "
                           f"for {x}|{y} — {len(solids)} bodies are placed")
        gaps[f"{x}|{y}"] = round(float(_clearing.gap(solids[x], solids[y], horizon)), 4)

    faces = {}
    if "foam-assembly" in solids:
        faces["foam-assembly.cap"] = round(float(ea.cap_face(solids["foam-assembly"])), 4)

    carried = {}
    if "digiten-flow" in getattr(a, "carries", {}):
        import digiten_flow_sensor as _digiten
        pos, axis = a.carries["digiten-flow"](_digiten.wire_exit())
        carried["digiten-flow.wire_exit"] = {"pos": _plain(pos), "axis": _plain(axis)}

    # WHAT A DRIVER WOULD IMPORT THE CAD TO READ. These are module-level and cost no build,
    # but reaching them means loading cadquery and the forty modules behind it — which is the
    # whole of what `_electronics_shelf_sync` pays to learn how many poles a Wago row has.
    constants = {
        "C14_STATION": _plain(ea.C14_STATION),
        "DIGITEN_COLLET_FREE": _plain(ea.DIGITEN_COLLET_FREE),
        "FLOOR_GROMMET_SQUEEZE": _plain(ea.FLOOR_GROMMET_SQUEEZE),
        "PANEL_X": _plain(ea.PANEL_X),
        "PORT_NUT_GAP": _plain(ea.PORT_NUT_GAP),
        "WAGO_POLES": _plain(ea.WAGO_POLES),
        "appliance_width": _plain(_enc.appliance_width),
        "side_rib_inset": _plain(_enc.side_rib_inset),
        "wall": _plain(_enc.wall),
    }

    # Derived off the box, by the functions that derive them. A driver that recomputed any of
    # these would be keeping a second copy of the rule.
    z_stations = _plain(_enc._z_stations(box.inner, box.y_joint))
    hopper_hole = _plain(_enc._hopper_hole(box.funnel))

    # The strap that closes round a seated body and its rib, for every seat radius the machine
    # actually stands one on — keyed by the radius, which is what a caller has.
    seats = {round(float(s[-1]), 4)
             for s in list(getattr(a, "tube_anchors", ()) or ())
             + list(getattr(a, "body_anchors", ()) or ())
             if s and isinstance(s[-1], (int, float))}
    strap_loops = {f"{r:.4f}": round(float(_enc.tube_anchor_strap_loop(r)), 4)
                   for r in sorted(seats)}

    return {
        "schema": SCHEMA,
        "sources": _realized.digest(_realized.source_files(
            Path(ea.__file__).resolve())),
        "box": _plain(box),
        "constants": constants,
        "z_stations": z_stations,
        "hopper_hole": hopper_hole,
        "strap_loops": strap_loops,
        "manifold_bodies": sorted(n for n in solids if ea._manifold(n)),
        "pack": {
            "placed": sorted(p.placed),
            "body_anchors": _plain(getattr(a, "body_anchors", ())),
            "tube_anchors": _plain(getattr(a, "tube_anchors", ())),
        },
        "runs": runs,
        "wall_ports": {"union": _plain(union), "co2": _plain(co2)},
        "pieces": piece_boxes,
        "faces": faces,
        "carried_points": carried,
        "gaps": gaps,
    }


def write(facts=None) -> Path:
    from _cadq_export import _atomic_write

    facts = facts if facts is not None else gather()
    text = json.dumps(facts, indent=1, sort_keys=True) + "\n"
    _atomic_write(ARTIFACT, lambda p: Path(p).write_text(text))
    return ARTIFACT


# --- the reader --------------------------------------------------------------


class _Row(dict):
    """A scorecard row, reachable by attribute so a driver reads `.length` and not `["length"]`."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError as exc:
            raise AttributeError(k) from exc


class Facts:
    """The artifact and the scorecard behind one object."""

    def __init__(self, facts, card):
        self._f, self._c = facts, card

    # --- what this file adds ---
    @property
    def box(self):
        return _Row(self._f["box"])

    @property
    def pack(self):
        return _Row(self._f["pack"])

    @property
    def wall_ports(self):
        return _Row(self._f["wall_ports"])

    @property
    def pieces(self):
        return {k: _Row(v) for k, v in self._f["pieces"].items()}

    @property
    def gaps(self):
        return self._f["gaps"]

    @property
    def faces(self):
        return self._f["faces"]

    @property
    def carried_points(self):
        return {k: _Row(v) for k, v in self._f["carried_points"].items()}

    @property
    def sources(self):
        return self._f["sources"]

    @property
    def constants(self):
        """What a driver would otherwise import the CAD to read."""
        return _Row(self._f["constants"])

    @property
    def z_stations(self):
        return self._f["z_stations"]

    @property
    def hopper_hole(self):
        return self._f["hopper_hole"]

    @property
    def manifold_bodies(self):
        return self._f["manifold_bodies"]

    def strap_loop(self, seat_r: float) -> float:
        """The strap that closes round a body seated on a rib of this radius."""
        key = f"{round(float(seat_r), 4):.4f}"
        try:
            return self._f["strap_loops"][key]
        except KeyError as exc:
            raise KeyError(
                f"no strap is recorded for a seat of {seat_r} — the machine stands one on "
                f"{sorted(self._f['strap_loops'])}") from exc

    # --- what the scorecard already carried ---
    @property
    def mounts(self):
        return [_Row(r) for r in self._c.get("mounts", ())]

    @property
    def runs(self):
        """The drawn runs as the machine measured them — unrounded. `card_runs` is the card's
        own rows, which carry the grades and the corner geometry at reading precision."""
        return [_Row(r) for r in self._f.get("runs", ())]

    @property
    def card_runs(self):
        return [_Row(r) for r in self._c.get("bends", ())]

    def body(self, component):
        for r in self._c.get("shapes", ()):
            if r.get("component") == component:
                row = _Row(r)
                row["box"] = r["boxes"][0] if r.get("boxes") else None
                return row
        raise KeyError(f"{component} is not among the {len(self._c.get('shapes', ()))} bodies "
                       f"the card carries")

    def run(self, rid):
        for r in self._c.get("bends", ()):
            if r.get("id") == rid:
                return _Row(r)
        raise KeyError(f"{rid} is not among the {len(self._c.get('bends', ()))} runs the card carries")

    def port(self, component, name):
        for r in self._c.get("ports", ()):
            if r.get("component") == component and r.get("name") == name:
                return _Row(r)
        raise KeyError(f"{component}/{name} is not among the {len(self._c.get('ports', ()))} "
                       f"ports the card carries")

    def check(self, cid):
        for r in self._c.get("checks", ()):
            if r.get("id") == cid:
                return _Row(r)
        raise KeyError(f"{cid} is not among the {len(self._c.get('checks', ()))} checks")

    def agrees_with_card(self) -> bool:
        """Whether both files were made from the same tree."""
        return self._f.get("sources") == self._c.get("sources")


def read() -> Facts:
    if not ARTIFACT.is_file():
        raise FileNotFoundError(
            f"{ARTIFACT.relative_to(_ROOT)} is not written — run "
            f"tools/cad-venv/bin/python hardware/scripts/_facts.py")
    return Facts(json.loads(ARTIFACT.read_text()), json.loads(SCORECARD.read_text()))


def selftest():
    f = read()
    assert f.box.outer, "the box states no outer bound"
    assert f.pack.placed, "no placed bodies"
    assert f.body("compressor").box, "the compressor has no box"
    assert f.run("fluid-18").length > 0, "fluid-18 has no length"
    assert f.pieces, "no printed pieces"
    print(f"  the box states an outer bound of {f.box.outer}")
    print(f"  {len(f.pack.placed)} placed bodies, {len(f.pieces)} printed pieces, "
          f"{len(f.runs)} runs, {len(f.mounts)} fastening rows")
    print(f"  declared gaps: {f.gaps}")
    print(f"  artifact and card agree on the tree: {f.agrees_with_card()}")
    print("_facts selftest OK")


def main(argv):
    if "selftest" in argv:
        return selftest()
    if "--check" in argv:
        was = json.loads(ARTIFACT.read_text()) if ARTIFACT.is_file() else None
        now = gather()
        if was == now:
            print("the facts are the ones the tree makes")
            return 0
        print("the facts have moved — run this without --check", file=sys.stderr)
        return 2
    print(f"-> {write().relative_to(_ROOT)}")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("HSM_SKIP_VIEWS", "1")
    sys.exit(main(sys.argv[1:]) or 0)
