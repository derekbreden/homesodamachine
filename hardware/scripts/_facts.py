"""What one build knows, written down so the readers do not each build it again.

    tools/cad-venv/bin/python hardware/scripts/_facts.py            # exit 2 if it moved
    tools/cad-venv/bin/python hardware/scripts/_facts.py --write    # write it anyway
    tools/cad-venv/bin/python hardware/scripts/_facts.py selftest

    import _facts
    f = _facts.read()
    f.box.outer                      # the Box, field for field
    f.runs                           # the drawn runs, measured
    f.check("clearance-floor").status

THE DOC DRIVERS WANT NUMBERS, NOT SOLIDS. Of the figures they substitute, the overwhelming
majority is arithmetic over module constants and needs no geometry at all; the rest is what
this file adds — the `Box` the walls are cut from, the wall bores, the printed pieces' own
boxes, a named face, a carried point, the drawn runs, and a few exact distances between
declared pairs. `enclosure-assembly.scorecard.json` is beside it for a driver that wants a
check's own verdict.

So a driver reads two files and stands no machine. `enclosure-assembly.scorecard.json` is
written by the assembly's own run; this artifact is written beside it.

THE CARD RIDES WITH THE VALUES. `card` names what `enclosure-assembly.scorecard.json` measured
at the moment this was written beside it, so a reader holding both can tell whether they came
off the same machine without importing the CAD.
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = _HERE.parent.parent
_ROOT = _HW.parent

for _p in (_HW / "scripts", _HW / "manifold-layout", _HW / "printed-parts" / "enclosure" / "enclosure", _HW / "reference" / "digiten-flow-sensor", _HW / "reference" / "wr1110-regulator", _HW / "reference" / "jg-bulkhead-union"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _realized                                                        # noqa: E402

ARTIFACT = _HW / "manifold-layout" / "enclosure-assembly.facts.json"
SCORECARD = _HW / "manifold-layout" / "enclosure-assembly.scorecard.json"
STEP = _HW / "manifold-layout" / "enclosure-assembly.step"
SCHEMA = 2

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

# The runs a document names the neighbours of, each with the horizon its own sentence reaches.
# This keeps, per run, what it passes and how close — nearest first — so a driver can say which
# two bodies a lane runs between without standing the machine to find out.
#
# THE HORIZON IS THIS LIST'S, the way `DECLARED_GAPS`' is. What a lane's two sides measure and
# where the tight end of the pack lies are two questions, so a sentence naming a neighbour at
# five millimetres has a reading here whatever the card's `REPORT_NEAR` stops at.
DECLARED_RUN_NEIGHBOURS = (
    ("fluid-4", 6.0),
)

# The bodies whose ports a printed card holds its own sentence against — `assembly/cards/`,
# which is the only reader of `card_ports`. A name here is a name a card asserts on; the
# machine's other seventy-odd bodies present ports this file does not write down.
# The two flavour bulkheads are not named in that source — the deck reaches them by walking
# `constants["PANEL_X"]`, so a column added there needs a row here.
CARD_PORT_BODIES = (
    "asse1022-assembly",
    "bulkhead-carb",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-water",
    "digiten-flow",
    "foam-assembly",
    "vk-solenoid",
    "water-split",
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


def gather(whole=None, module=None):
    """Every fact this file adds, off ONE build of the machine.

    `whole` is a machine somebody already stood. The assembly's own run has one in hand when
    it writes the STEP and the card, and handing it here is the difference between a chain
    that derives the appliance twice and one that derives it once."""
    import _boxes
    import _clearing
    import enclosure as _enc

    # THE CALLER'S OWN MODULE, when it has one. `_manifold` answers off `_ROUTED`, a module set
    # that fills as runs are authored — so a SECOND copy of `enclosure_assembly`, which is what
    # `import` hands back while the first is running as `__main__`, has never authored a run and
    # calls every tube part of the pack. Same names, different machine.
    if module is None:
        import enclosure_assembly as module
    ea = module

    # ONE DERIVATION. `build_enclosure_assembly` calls `machine` itself and hangs the box it
    # sized on what it hands back, so asking for both stands the appliance twice.
    whole = whole if whole is not None else ea.build_enclosure_assembly()
    a, box = whole, whole.box
    p = whole.pack
    solids = {n: s for n, (s, _c) in ea._solids(whole).items()}

    # AT THE PRECISION THE DRAWING HAD. The card rounds a length for reading, and a document
    # that rounds again off that reads a different last digit than the machine drew — so the
    # runs are carried here unrounded and the card's rows stay what they are, a reading.
    runs = [{"id": r.id, "frm": r.frm, "to": r.to,
             "length": float(r.length), "corners": len(r.bends),
             "bend": float(r.bend), "diam": float(r.diam)}
            for r in getattr(whole, "runs", ())]

    # Every placed body's OPTIMAL box, taken by the same call a reader would have taken. The
    # card carries boxes too, but a figure read off one and a figure read off the other are
    # two readings of one body, and a document that quotes both quotes two machines.
    bodies = {}
    for name, s in solids.items():
        bb = _boxes.boxed(s)
        bodies[name] = [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax]

    # The assembly producer carries the exact materialized walls it checked. Older callers that
    # hand this collector an assembly without that field keep the direct-source fallback.
    pieces = getattr(whole, "pieces", None)
    if pieces is None:
        pieces, _rest = _enc.build_pieces(box)
    piece_boxes = {}
    for name, wp in pieces.items():
        bb = _boxes.boxed(wp.val() if hasattr(wp, "val") else wp)
        piece_boxes[name] = {"box": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax]}

    union = ea.y_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
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

    # A reference module's own point, carried to where the machine stands the body. A driver
    # that wants one otherwise loads the reference module AND the placement to apply it.
    carried = {}
    carries = getattr(a, "carries", {})
    if "digiten-flow" in carries:
        import digiten_flow_sensor as _digiten
        pos, axis = carries["digiten-flow"](_digiten.wire_exit())
        carried["digiten-flow.wire_exit"] = {"pos": _plain(pos), "axis": _plain(axis)}
    if "wr1110" in carries:
        import wr1110_regulator as _wr1110
        carried["wr1110.barrel"] = {"pos": _plain(carries["wr1110"](_wr1110.barrel()[0])[0])}

    # THE PORTS THE PRINTED CARDS ARE HELD AGAINST, as the machine placed them, unrounded.
    # `assembly/cards/_cards_ip.py` and `_cards_fs.py` assert a card's sentence against these:
    # the core's three cap conduits opening upward, the union's inboard collet and the ASSE
    # chain's inlet standing on one point, the split's branch axis, the meter against the carb
    # union, V-K's outlet facing +Y, the vent tip facing down, and `bulkhead-water` presenting
    # both collets. A BODY IS HERE BECAUSE A CARD NAMES IT — the rest of the machine's ports are
    # not written down, and a card reaching for one gets a KeyError rather than a wrong sentence.
    ports = {}
    for _body in CARD_PORT_BODIES:
        _fr = (getattr(a, "frames", {}) or {}).get(_body)
        if _fr is None:
            raise KeyError(
                f"{_body!r} is recorded for the card deck to assert on and no placed body "
                f"carries that name — rename it in assembly/cards/ too, or drop it from "
                f"`CARD_PORT_BODIES`.")
        ports[_body] = {n: {"pos": _plain(_pos), "axis": _plain(_ax), "diam": float(_d)}
                        for n, (_pos, _ax, _d) in _fr.ports.items()}

    # The mouth a bulkhead presents, carried to where the machine stands it — the same station
    # `y_wall_ports` strikes its bore on, so a document and a hole cannot land on two columns.
    import jg_bulkhead_union as _jg
    mouths = {}
    if hasattr(a, "bulkhead_carry"):
        mouths["bulkhead-water"] = _plain(a.bulkhead_carry(_jg.port(-1.0))[0])
    for _n, _c in getattr(a, "panel_carries", {}).items():
        mouths[_n] = _plain(_c(_jg.port(-1.0))[0])

    # What a named run passes, nearest first — the exact solid distance, boxes as a prefilter.
    # A run's own two end bodies are out of its population: the tube seats into their collets by
    # construction and reads 0 there, which is the same exemption `run_clearances` takes off the
    # same `run_world`.
    import _scorecard as _card
    _bodies_only = _card._split_placed(whole)[0]
    _body_boxes = {n: _boxes.loose(s) for n, s in _bodies_only.items()}
    run_near = {}
    for rid, horizon in DECLARED_RUN_NEIGHBOURS:
        tubes, ends, _rest = _card.run_world(
            whole, [r for r in getattr(whole, "runs", ()) if r.id == rid])
        if rid not in tubes:
            raise KeyError(f"{rid} is not drawn, so the lane it threads has no reading — a "
                           f"document naming its neighbours is describing a run the machine "
                           f"no longer draws")
        tube_box = _boxes.loose(tubes[rid])
        rows = []
        for name, solid in _bodies_only.items():
            if name in ends[rid] or _clearing.box_gap(tube_box, _body_boxes[name]) >= horizon:
                continue
            g = float(_clearing.gap(tubes[rid], solid, horizon))
            if g < horizon:
                rows.append((g, name))
        if not rows:
            raise KeyError(f"{rid} passes no body inside {horizon:g} mm — a document naming "
                           f"its neighbours is describing a lane the machine no longer has")
        run_near[rid] = [[other, round(g, 4)] for g, other in sorted(rows)]

    # WHAT A DRIVER WOULD IMPORT THE CAD TO READ. These are module-level and cost no build,
    # but reaching them means loading cadquery and the forty modules behind it — which is the
    # whole of what `_power_column_sync` pays to learn how many poles a Wago row has.
    constants = {
        "C14_STATION": _plain(ea.C14_STATION),
        "DIGITEN_COLLET_FREE": _plain(ea.DIGITEN_COLLET_FREE),
        "FLOOR_GROMMET_SQUEEZE": _plain(ea.FLOOR_GROMMET_SQUEEZE),
        "PANEL_X": _plain(ea.PANEL_X),
        "CRADLE_TOL": _plain(ea.CRADLE_TOL),
        "PORT_NUT_GAP": _plain(ea.PORT_NUT_GAP),
        "WAGO_POLES": _plain(ea.WAGO_POLES),
        "appliance_width": _plain(_enc.appliance_width),
        "side_band_inset": _plain(_enc.side_band_inset),
        "wall": _plain(_enc.wall),
    }

    # Derived off the box, by the function that derives it. A driver that recomputed this
    # would be keeping a second copy of the rule.
    hopper_hole = _plain(_enc._funnel_hole(box.funnel))

    return {
        "schema": SCHEMA,
        # THE CARD THIS WAS TAKEN BESIDE, by what it measured. One run writes the card and then
        # this, so a reader holding both can tell whether they came off the same machine.
        "card": _realized.code_digest(SCORECARD),
        # AND THE SOLID IT WAS MEASURED OFF. The run writes the STEP, then the card, then
        # this, so each digest here names one of the two that went before it.
        "step": _realized.code_digest(STEP),
        "box": _plain(box),
        "constants": constants,
        "hopper_hole": hopper_hole,
        "manifold_bodies": sorted(n for n in solids if ea._manifold(n)),
        # What the two plate generators draw from. Both read their bodies out of a placed
        # machine by name, so they take this one rather than standing a second.
        "valve_trays": _plain(ea.valve_tray_plans(whole)),
        # And the decks as the WALL is handed them — plane, which way the valves' own +Z runs
        # off it, and the seats. The plans above are what a plate is DRAWN from, in the plate's
        # own frame; these are where the box stands one.
        "valve_tray_stations": _plain(ea.valve_tray_stations(whole.pack.placed)),
        "pump_trays": _plain(ea.pump_tray_plans(whole, box)),
        "pack": {
            "placed": sorted(whole.pack.placed),
            "body_anchors": _plain(getattr(a, "body_anchors", ())),
            "tube_anchors": _plain(getattr(a, "tube_anchors", ())),
        },
        "bodies": bodies,
        "mouths": mouths,
        "card_ports": ports,
        "run_near": run_near,
        "runs": runs,
        "wall_ports": {"union": _plain(union), "co2": _plain(co2)},
        "pieces": piece_boxes,
        "faces": faces,
        "carried_points": carried,
        "gaps": gaps,
    }


def write(facts=None, whole=None, module=None) -> Path:
    from _cadq_export import _atomic_write

    facts = facts if facts is not None else gather(whole, module)
    text = json.dumps(facts, indent=1, sort_keys=True) + "\n"
    _atomic_write(ARTIFACT, lambda p: Path(p).write_text(text))
    return ARTIFACT


# --- the reader --------------------------------------------------------------


class _BB:
    """A body's box as the artifact holds it, answering what `_boxes.boxed` answers: the six
    faces, the three spans, and the union with another."""

    __slots__ = ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")

    def __init__(self, xmin, ymin, zmin, xmax, ymax, zmax):
        self.xmin, self.ymin, self.zmin = xmin, ymin, zmin
        self.xmax, self.ymax, self.zmax = xmax, ymax, zmax

    def add(self, other):
        return _BB(min(self.xmin, other.xmin), min(self.ymin, other.ymin),
                   min(self.zmin, other.zmin), max(self.xmax, other.xmax),
                   max(self.ymax, other.ymax), max(self.zmax, other.zmax))

    @property
    def xlen(self):
        return self.xmax - self.xmin

    @property
    def ylen(self):
        return self.ymax - self.ymin

    @property
    def zlen(self):
        return self.zmax - self.zmin

    def __repr__(self):
        return (f"_BB(x[{self.xmin:.3f},{self.xmax:.3f}] y[{self.ymin:.3f},{self.ymax:.3f}] "
                f"z[{self.zmin:.3f},{self.zmax:.3f}])")


class _Frame:
    """One placed body's ports, reachable the way the assembly's own frame is."""

    __slots__ = ("ports",)

    def __init__(self, d):
        self.ports = {n: (tuple(v["pos"]), tuple(v["axis"]), v["diam"]) for n, v in d.items()}


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
    def valve_trays(self):
        """`name -> (width, ((u, v), …))`, as `enclosure_assembly.valve_tray_plans` reads it."""
        return {k: (w, tuple(tuple(s) for s in seats))
                for k, (w, seats) in self._f["valve_trays"].items()}

    @property
    def valve_tray_stations(self):
        """`(plane, sign, ((x, z), …))` per deck, as `enclosure.Box.valve_trays` is.

        What the plans cannot carry: the world plane a deck's valves stand their mounting
        faces on, and which way their own +Z runs off it. A valve seats the same way on
        either deck, so there is nothing per-deck beyond where it stands."""
        return tuple((p, g, tuple(tuple(t) for t in seats))
                     for p, g, seats in self._f["valve_tray_stations"])

    @property
    def pump_trays(self):
        return dict(self._f["pump_trays"])

    @property
    def gaps(self):
        return self._f["gaps"]

    @property
    def faces(self):
        return self._f["faces"]

    @property
    def card_ports(self):
        """`card_ports[body].ports[name]` -> (pos, axis, diam), at the precision the machine
        placed it. Read by `assembly/cards/_cards_ip.py` and `_cards_fs.py`, and holding only
        the bodies those two name (`CARD_PORT_BODIES`)."""
        return {b: _Frame(v) for b, v in self._f["card_ports"].items()}

    @property
    def carried_points(self):
        return {k: _Row(v) for k, v in self._f["carried_points"].items()}

    @property
    def card_digest(self):
        """What the card measured when this artifact was taken beside it."""
        return self._f["card"]

    @property
    def constants(self):
        """What a driver would otherwise import the CAD to read."""
        return _Row(self._f["constants"])

    @property
    def hopper_hole(self):
        return self._f["hopper_hole"]

    @property
    def manifold_bodies(self):
        return self._f["manifold_bodies"]

    @property
    def mouths(self):
        """A bulkhead's mouth, carried to where the machine stands it."""
        return self._f["mouths"]

    def near(self, rid):
        """What a run passes, nearest first, as (body, gap)."""
        try:
            return [(n, g) for n, g in self._f["run_near"][rid]]
        except KeyError as exc:
            raise KeyError(f"{rid}'s neighbours are not recorded — add it to "
                           f"DECLARED_RUN_NEIGHBOURS") from exc

    @property
    def bodies(self):
        """Every placed body's name, against its box — iterates and counts like the dict of
        placed solids a driver used to build to get."""
        return self._f["bodies"]

    def bb(self, name: str):
        """One placed body's optimal box, the reading `_boxes.boxed` took of it."""
        try:
            return _BB(*self._f["bodies"][name])
        except KeyError as exc:
            raise KeyError(
                f"{name} is not among the {len(self._f['bodies'])} bodies the machine places "
                f"— it has been renamed or dropped, and the figure reading it is stale. "
                f"Have: {', '.join(sorted(self._f['bodies']))}") from exc

    def group(self, pick):
        """The box holding every placed body `pick` accepts."""
        out = None
        for name in self._f["bodies"]:
            if not pick(name):
                continue
            b = self.bb(name)
            out = b if out is None else out.add(b)
        if out is None:
            raise ValueError("no placed body matched — this measurement has nothing in it")
        return out

    @property
    def runs(self):
        """The drawn runs as the machine measured them — unrounded."""
        return [_Row(r) for r in self._f.get("runs", ())]

    # --- what the scorecard already carried ---
    def check(self, cid):
        for r in self._c.get("checks", ()):
            if r.get("id") == cid:
                return _Row(r)
        raise KeyError(f"{cid} is not among the {len(self._c.get('checks', ()))} checks")

    def agrees_with_card(self) -> bool:
        """Whether the card beside this artifact is the one it was taken beside."""
        return self._f.get("card") == _realized.code_digest(SCORECARD)

    def agrees_with_step(self) -> bool:
        """Whether the solid beside this artifact is the one it was measured off.

        None when the STEP is not on this disk: it is fetched from the bundle rather than
        committed."""
        here = _realized.code_digest(STEP)
        return None if here is None else self._f.get("step") == here

    def stale(self) -> list:
        """What this artifact names that the tree no longer holds, as lines a reader can act
        on. Empty is current.

        A digest it does not carry and a digest that names something else are two readings,
        and each says so: the first stands for an artifact older than the datum, the second
        for one off another run."""
        out = []
        if not self.agrees_with_card():
            out.append(_disagrees(SCORECARD.name, "taken beside",
                                  self._f.get("card"), _realized.code_digest(SCORECARD)))
        if self.agrees_with_step() is False:
            out.append(_disagrees(STEP.name, "measured off",
                                  self._f.get("step"), _realized.code_digest(STEP)))
        return out


def _disagrees(other: str, verb: str, held, here) -> str:
    """One line naming what the facts carry for another artifact against what is beside them."""
    if held is None:
        return f"{ARTIFACT.name} carries no digest for {other}; {other} here is {here}"
    return (f"{ARTIFACT.name} was {verb} a different {other} — "
            f"it holds {held}, {other} here is {here}")


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
    assert f.check("clearance-floor").status, "the card carries no clearance-floor verdict"
    assert f.pieces, "no printed pieces"
    print(f"  the box states an outer bound of {f.box.outer}")
    print(f"  {len(f.pack.placed)} placed bodies, {len(f.pieces)} printed pieces, "
          f"{len(f.runs)} runs")
    print(f"  declared gaps: {f.gaps}")
    print(f"  artifact and card agree on the tree: {f.agrees_with_card()}")
    print("_facts selftest OK")


def main(argv):
    if "selftest" in argv:
        return selftest()
    # WRITING IS `enclosure_assembly.py`'S. It stands the machine once and writes the STEP, the
    # card and this off that one derivation; standing it again here to write only this is the
    # same artifact for a second full build. `--write` is for a hand run that wants one anyway.
    if "--check" in argv or "--write" not in argv:
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
    sys.exit(main(sys.argv[1:]) or 0)
