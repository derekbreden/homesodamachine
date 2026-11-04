"""What one build knows, written down so the readers do not each build it again.

    tools/cad-venv/bin/python hardware/scripts/_facts.py            # exit 2 if it moved
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

AND THE TREE RIDES WITH THE RUN. `card` and `step` hold the three artifacts to one run; nothing
in them holds that run to this tree, and a stale triple agrees with itself perfectly. `sources`
is the third digest — every file `tools/bazel/graph.json` traced the generator opening that no
generator writes — so a reading taken off a machine that has since moved says so instead of
reading green.
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
# WHAT THE RUN THAT WRITES THIS READS, as the tree's own account of it. `tools/bazel/graph.json`
# records the files each generator was traced OPENING, so the sources behind the assembly are
# already named and nothing here has to guess at them.
GRAPH = _ROOT / "tools" / "bazel" / "graph.json"
GENERATOR = "hardware/manifold-layout/enclosure_assembly.py"


def _request(op, **values):
    from _rust_data import request
    return request('machine-data', 'machine-data', {'op': op, **values})


def _read_graph() -> dict:
    from _cadq_export import note_read
    note_read(GRAPH)
    return _request('read_json', path=str(GRAPH), optional=True)


def _source_names(graph: dict) -> list:
    """The generator's source projection, computed by Rust from the declared graph."""
    return _request('facts_sources', graph=graph)


def sources() -> list:
    """The files this artifact is taken FROM — what the generator reads and no generator writes.

    A DERIVED INPUT CARRIES ITS OWN GENERATOR'S FRESHNESS AND NOT THIS ONE'S. The run opens 205
    files and 98 of them are solids, meshes and cards some other generator drew; the sources
    those were drawn from are in this list already, so a digest over the solids as well says
    nothing the code does not and costs thirty seconds of hashing to say it. `writes` over the
    whole graph is what names them, so the split is the graph's and not a suffix list of ours.

    Empty when the graph is not on this disk or does not name the generator. A reading that
    cannot be taken is not a reading that failed."""
    return _source_names(_read_graph())


def _source_digest(graph: dict):
    paths = _source_names(graph)
    return _realized.digest([_ROOT / p for p in paths]) if paths else None


def source_digest():
    """One name for what the whole of `sources()` computes, or None when the graph names none.

    `_realized.code_digest` names a Python file by its PARSED CODE, so a comment moved is not a
    tree moved and a doc pass does not redden this."""
    return _source_digest(_read_graph())

# The pairs whose exact distance a document states and the card does not carry. The card
# reports a pair only when it closes to within its own `REPORT_NEAR`, so a sentence naming a
# gap wider than that floor has nothing to read, and takes it here instead.
#
# A pair under the floor is already in `checks[clearance-floor].detail`, so it belongs to the
# reader rather than to this list. NAMES ARE THE PLACED BODIES'; a run is not one of them,
# and a pair naming a run raises here rather than going quietly missing from the artifact.
DECLARED_GAPS = ()

# The runs a document names the neighbours of, each with the horizon its own sentence reaches.
# This keeps, per run, what it passes and how close — nearest first — so a driver can say which
# two bodies a lane runs between without standing the machine to find out.
#
# THE HORIZON IS THIS LIST'S, the way `DECLARED_GAPS`' is. What a lane's two sides measure and
# where the tight end of the pack lies are two questions, so a sentence naming a neighbour at
# five millimetres has a reading here whatever the card's `REPORT_NEAR` stops at.
DECLARED_RUN_NEIGHBOURS = ()

# Placed port frames used by routing illustrations and bench inspection tools.
# The two flavour bulkheads are distinct bodies, so each has its own frame.
CARD_PORT_BODIES = (
    "asse1022-assembly",
    "bulkhead-carb",
    "bulkhead-drain",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-water",
    "digiten-flow",
    "foam-assembly",
    "vk-solenoid",
    "water-split",
    "gas-regulator",
    "gas-check",
    "jg-pp061208w",
    "suction-reducer",
    "discharge-reducer",
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


_BOX_FACT_ORDER = (
    "inner outer y_joint splits z_seam_passes front_ports back_ports east_ports "
    "west_ports funnel c14 east_bosses east_mount_fills side_wells floor_bosses west_cradle "
    "cond_cradle cond_mount cond_airway asse_cradle flow_meter_anchors tube_anchors "
    "ceiling_reliefs flank_reliefs front_flank_reliefs port_field nameplate valve_trays pump_trays core_stops core_holds "
    "vent_chase column_reliefs collet_plate pump_bay").split()
_BOX_FACT_EXCLUDED = {
    "pack",    # container copied field-by-field above
    "placed",  # solids
    "keystone",  # repeated as KEYSTONE_STATION in constants
}


def _box_plain(box):
    """The Box as the artifact carries it: the shell's own figures and the pack's stations in
    one row, the order the readers of this file have always had them in.

    A Box stands its Pack rather than copying it, so a station is reached through `box.pack`.
    The artifact is read by drivers that take a station by name off `f.box`, and `placed` is
    left out because it holds solids and a fact is numbers."""
    src = {**box.pack._asdict(), **box._asdict()}
    missing = set(src) - set(_BOX_FACT_ORDER) - _BOX_FACT_EXCLUDED
    extra = set(_BOX_FACT_ORDER) - set(src)
    if missing or extra:
        raise KeyError(
            f"box fact projection is stale: missing {sorted(missing)}, extra {sorted(extra)}")
    return {k: _plain(src[k]) for k in _BOX_FACT_ORDER}


def _tube_handoff(whole):
    """The route consumer's exact metadata, bound to this producer's fine outputs."""
    import _tube_export
    import _mesh_payload

    def artifact(path):
        return {"path": path.relative_to(_ROOT).as_posix(),
                "sha256": _mesh_payload.source_digest(path)}

    return {
        "schema": 1,
        "step": artifact(STEP),
        "fine_model": artifact(Path(str(STEP) + ".npz")),
        "scene": artifact(STEP.with_suffix(".scene.npz")),
        "routing": _plain(_tube_export.route_metadata(whole)),
    }


def write(facts) -> Path:
    """Write a producer's plain facts table beside its scorecard."""
    from _cadq_export import _atomic_write

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
        """`(plane, sign, ((x, z), …))` per deck, as `enclosure.Pack.valve_trays` is.

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
        placed it. Shared by routing illustrations and bench inspection tools;
        the selected bodies are listed in `CARD_PORT_BODIES`."""
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

    def agrees_with_sources(self):
        """Whether the tree beside this artifact is the one it was taken from.

        None when it carries no digest for them, or when the graph is not here to take one.
        An artifact written before this datum existed is SILENT about the tree and not wrong
        about it — every artifact in the tree predates the key and gains one when it is next
        written — so a reader gets None and says so rather than reading a fault into a
        reading that was never taken."""
        held = self._f.get("sources")
        if held is None:
            return None                  # and the tree is not walked to say so
        here = source_digest()
        return None if here is None else held == here

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
        if self.agrees_with_sources() is False:
            out.append(
                f"{ARTIFACT.name} was taken from a different tree — it holds "
                f"{self._f.get('sources')} for the {len(sources())} sources behind "
                f"{GENERATOR}, which stand at {source_digest()} here. The three artifacts "
                f"agree with each other and describe a machine that has since moved.")
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
            f"tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py")
    from _cadq_export import note_read
    note_read(ARTIFACT)
    note_read(SCORECARD)
    return Facts(_request('read_json', path=str(ARTIFACT)),
                 _request('read_json', path=str(SCORECARD)))


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

    # THE THIRD DIGEST, HELD ON ARTIFACTS THIS RUN MAKES UP. A stale triple agrees with itself,
    # so the readings that matter are the ones no real artifact here can show at once: a tree
    # that matches, a tree that has moved, and an artifact written before the datum existed.
    silent = Facts({k: v for k, v in f._f.items() if k != "sources"}, f._c)
    assert silent.agrees_with_sources() is None, \
        "an artifact carrying no source digest reads as a fault instead of a silence"
    assert not [ln for ln in silent.stale() if "different tree" in ln], \
        "an artifact silent about its sources is reported stale for it"
    graph = _read_graph()
    names = _source_names(graph)
    index = GRAPH.relative_to(_ROOT).as_posix()
    assert index not in names, "the whole build graph is treated as an enclosure source"
    foreign = {
        **graph,
        "selftest/unrelated-fixture.py": {
            "reads": ["selftest/unrelated-fixture-input.py"],
            "writes": ["selftest/unrelated-fixture.step"],
        },
    }
    assert _source_digest(foreign) == _source_digest(graph), \
        "an unrelated generator changes the enclosure source digest"
    here = _source_digest(graph)
    if here is not None:
        fresh = Facts({**f._f, "sources": here}, f._c)
        moved = Facts({**f._f, "sources": "0" * 32}, f._c)
        assert fresh.agrees_with_sources() is True, \
            "a source digest naming this tree does not read current"
        assert moved.agrees_with_sources() is False, \
            "a source digest naming another tree reads current"
        assert any("different tree" in ln for ln in moved.stale()), \
            "a tree that has moved writes no line a reader can act on"
        print(f"  {len(sources())} sources behind {GENERATOR} name this tree {here}")
    else:
        print(f"  no source digest: {GRAPH.relative_to(_ROOT)} names no {GENERATOR}")
    print("_facts selftest OK")


def main(argv):
    if "selftest" in argv:
        return selftest()
    if "--write" in argv:
        sys.exit("Facts are written by hardware/manifold-layout/enclosure_assembly.py")
    stale = read().stale()
    if stale:
        print("\n".join(stale), file=sys.stderr)
        return 2
    print("the facts describe this tree's assembly outputs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)
