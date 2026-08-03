"""Selects-source assembly: the source pair over the selects pair, joined as an H.

Four valves and one junction. The [fluid-topology](../../../topology/fluid-topology.md)
front end asks for a single node with four leaves on it — V-A (tap) and V-B (hopper)
feeding, V-C (channel A) and V-D (channel B) drawing — and every mode opens exactly one
of the feeders and exactly one of the drawers, so the only traffic the node ever carries
is one source to one select.

Two trays a `tray_stack_pitch` apart put those four ports in TWO COLUMNS, one above the
other:

    V-A ──┬────────────── V-B        source tray
          │              │
        (tee)══crossbar══(tee)       the junction
          │              │
    V-C ──┴────────────── V-D        selects tray

A Tee takes two ports lying in line — which is what a column is — so each column is one
Tee's RUN, and the two branches face each other across the gap with one length of tube
between them. Verticals first, then the crossbar that joins them.

`../two-valve-tray/`'s own docstring is where this comes from: "a Y-divider takes two
ports side by side, a Tee takes one above the other, and that is the tray's pose in the
enclosure rather than anything the tray declares." Both trays here are in the pose that
makes it a Tee.

Origin = the column pair's centre in X, the trays' own centre in Y, Z = 0 at the SELECTS
tray's valve mounting plane. Forward is −Y: all four junction ports face that way, and
the aft four are the boundary (`boundary_collets`).
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw / "printed-parts" / "valve-manifold" / "two-valve-tray",
    _hw / "printed-parts" / "enclosure" / "enclosure-assembly",
):
    sys.path.insert(0, str(_p))
# `tools/` is shared machinery, so it anchors on the repo root that holds it —
# not on this edition's own root, which has no tools/ of its own.
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_md, substitute_py_comments
import _contents as contents
import _routing as R
import two_valve_tray as tray

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)   # PETG tan
VALVE_COLOR = cq.Color(0.20, 0.22, 0.26)  # solenoid body/coil, dark
TEE_COLOR = cq.Color(0.92, 0.92, 0.92)    # the union tee, the enclosure's own
TUBE_COLOR = cq.Color(0.90, 0.90, 0.94)   # LLDPE, the enclosure's own

# --- What the two trays fix -----------------------------------------------
# The stack pitch is the ENCLOSURE's: this assembly is a pose the manifold column puts
# its trays in, not a pose it invents, so the two plates stand exactly as far apart here
# as they do in the machine and the H is measured against the real gap.
STACK_PITCH = contents.tray_stack_pitch()
PORT_Z = tray.port_z                     # both trays' port axis, over its own plate
SEAT_X = tray.seat_x                     # a column's own X — half the valve seat pitch
PORT_HALF = tray.port_half               # collet tip from the valve centre
BORE = 6.35                              # 1/4" tube, the manifold's one size

# --- What the fitting fixes ------------------------------------------------
# All three off the tee STEP, through `_contents`, so this reads the same numbers the
# enclosure routes its own six tees on.
RUN_HALF = contents.TEE_RUN_HALF         # run collet face from the body centre
BRANCH_REACH = contents.TEE_BRANCH_REACH  # branch collet face from the same centre
BEND = contents.LLDPE_BEND               # what soft 1/4" LLDPE turns on
# The exposed tube between two collet faces butted down one line — the enclosure's own
# figure for a tee's run legs, and the crossbar is that same joint lying sideways.
CROSSBAR_MIN = contents.TEE_RUN_LEAD

# --- Where the columns stand ----------------------------------------------
# The enclosure's, not this file's: `junction_column_x` stands the columns on the four
# ports and gives way only to what the fitting cannot — two branches facing each other need
# `2 × BRANCH_REACH` between their bodies' centres before there is any tube at all, and that
# is [40.14](FACING_SPAN) mm against a valve seat pitch of [34.25](SEAT_PITCH), so each
# column stands [4.94](COLUMN_SPREAD) mm off its seat on the stand-in. This assembly is that
# junction lifted out of the machine, so the pose it draws is the pose the machine builds and
# the two cannot drift; the guards those functions raise are the guards on this file.
_WEST, _EAST = contents.junction_column_x()
COLUMN_X = (_EAST - _WEST) / 2.0
COLUMN_SPREAD = COLUMN_X - SEAT_X
CROSSBAR = contents.junction_crossbar()      # exposed tube, branch face to branch face
# The straight a leg runs off its collet before it turns, and how far FORWARD of the collet
# plane the column stands — the leg goes straight out on axis for exactly one lead, then
# turns down the column in one gentle move that carries the spread with it.
LEG_LEAD = contents.JUNCTION_LEG_LEAD
COLUMN_Y = -(PORT_HALF + LEG_LEAD)
# The tee sits midway down its column, so the two legs off it are one length and neither
# is the short one. What is left between a run collet face and the port plane it reaches
# is `TEE_STANDOFF`, and it is the room both corners of a leg are turned in.
TEE_Z = PORT_Z + STACK_PITCH / 2.0
TEE_STANDOFF = STACK_PITCH / 2.0 - RUN_HALF
contents.junction_tee_pos("tee-y-a")         # raises if the run has filled the stack pitch

# --- The four junction ports ----------------------------------------------
# Each tray's FORWARD pair. On the source tray those are the outlets, on the selects tray
# the inlets — the trays are clocked as `../../enclosure/enclosure-assembly/_contents`
# clocks them, both pairs facing the junction.
FORWARD = (0.0, -1.0, 0.0)
SOURCE_Z = PORT_Z + STACK_PITCH

COLUMNS = (
    # name, source port, select port, the column's X sign
    ("tee-ac", "V-A-O", "V-C-I", -1.0),   # tap water over channel A's select
    ("tee-bd", "V-B-O", "V-D-I", +1.0),   # hopper over channel B's select
)


def tray_pos(which: str) -> tuple:
    """A tray's own origin in this assembly's frame."""
    return (0.0, 0.0, STACK_PITCH if which == "source" else 0.0)


def valve_ports(which: str) -> dict:
    """One tray's four collets, named for the topology: `{V-x-I|O: (pos, axis)}`.

    `two_valve_tray.port_collets` hands out four bare collets keyed by sign, and which end
    of a port is the inlet is the pose's question, not the tray's. The source pair faces
    the junction with its OUTLETS and the selects pair with its INLETS, so the two trays
    read their four the same way round and the H joins outlet to inlet across it."""
    west, east = ("V-A", "V-B") if which == "source" else ("V-C", "V-D")
    fwd = "O" if which == "source" else "I"
    aft = "I" if which == "source" else "O"
    ox, oy, oz = tray_pos(which)
    out = {}
    for seat, nm in (("xn", west), ("xp", east)):
        for tag, end in (("yn", fwd), ("yp", aft)):
            pos, axis = tray.port_collets()[f"{seat}-{tag}"]
            out[f"{nm}-{end}"] = ((pos[0] + ox, pos[1] + oy, pos[2] + oz), axis)
    return out


def tee_pos(sign: float) -> tuple:
    """A tee's body centre: on its column, midway down the stack pitch."""
    return (sign * COLUMN_X, COLUMN_Y, TEE_Z)


# The tee's three collets in the STEP's OWN frame: the run on Z, faces at ±RUN_HALF, and
# the branch out +Y. A column needs no turn at all to take the run — the file is already
# stood the right way up — so the yaw below is the whole of this fitting's pose, and it is
# there for the branch alone.
_TEE_LOCAL = {
    "1": ((0.0, 0.0, +RUN_HALF), (0.0, 0.0, +1.0)),   # run, facing the source tray
    "2": ((0.0, 0.0, -RUN_HALF), (0.0, 0.0, -1.0)),   # run, facing the selects tray
    "3": ((0.0, +BRANCH_REACH, 0.0), (0.0, +1.0, 0.0)),   # the branch, the H's bar
}


def tee_yaw(sign: float) -> float:
    """The one turn a tee takes, body and ports alike: the yaw that lays its branch across
    at the OTHER column. Local +Y goes to −`sign` X, so the west tee's branch points east
    and the east tee's west, and the two face each other down the crossbar's line."""
    return sign * 90.0


def _yaw_z(v: tuple, deg: float) -> tuple:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])


def tee_ports(tee: str) -> dict:
    """A tee's three collets in this assembly's frame: `{name: (pos, axis)}`, numbered from
    the SOURCE end — 1 the run collet facing the source tray, 2 the run collet facing the
    selects tray, 3 the branch.

    Position and axis are carried through the same `tee_yaw` the solid takes, and then the
    same translation, so a port is never turned by hand alongside a body turned by hand.
    `selftest` holds them to it: every collet face here must land on the placed solid."""
    sign = next(s for nm, _f, _t, s in COLUMNS if nm == tee)
    tag = tee.split("-")[1].upper()
    centre, deg = tee_pos(sign), tee_yaw(sign)
    out = {}
    for num, (pos, axis) in _TEE_LOCAL.items():
        pos, axis = _yaw_z(pos, deg), _yaw_z(axis, deg)
        out[f"{tag}-{num}"] = (tuple(p + o for p, o in zip(pos, centre)), axis)
    return out


def boundary_collets() -> dict:
    """The assembly's boundary: the four AFT collets, the ones the H does not take.

    V-A-I takes the flow regulator, V-B-I the hopper drain, V-C-O and V-D-O leave for the
    two pump-inlet junctions. Everything forward of the trays is this assembly's own."""
    out = {}
    for which in ("source", "selects"):
        for nm, port in valve_ports(which).items():
            if nm.endswith("-I" if which == "selects" else "-O"):
                continue
            out[nm] = port
    return out


def _place_tee(sign: float):
    """The tee solid on its column, under `tee_yaw` — the same turn `tee_ports` carries its
    three collets through, in the same order."""
    body = cq.importers.importStep(str(contents.TEE_CONNECTOR)).val()
    return body.rotate((0, 0, 0), (0, 0, 1), tee_yaw(sign)).translate(tee_pos(sign))


def build_parts() -> dict:
    """Every placed body: two trays, four valves, two tees. Tubes are `build_runs`."""
    parts = {}
    for which in ("source", "selects"):
        ox, oy, oz = tray_pos(which)
        parts[f"{which}-tray"] = (
            tray.build_two_valve_tray().val().translate((ox, oy, oz)))
        west, east = ("V-A", "V-B") if which == "source" else ("V-C", "V-D")
        for seat, nm in (("xn", west), ("xp", east)):
            parts[nm] = tray.place_valve(*tray.seats[seat]).translate((ox, oy, oz))
    for nm, _f, _t, sign in COLUMNS:
        parts[nm] = _place_tee(sign)
    return parts


def build_runs() -> list:
    """The five lengths of tube: two down each column, one across.

    A column leg leaves its collet on axis for one `LEG_LEAD` and enters the tee's run
    collet on axis for another, and the single diagonal between them carries the drop and
    the column's spread in one gentle move — `bent`'s own idiom, and the reason the spread
    costs no corner of its own. The crossbar is one straight length: the two branch
    collets face each other down one line, so it leaves and enters with nothing to turn."""
    parts = build_parts()
    for which in ("source", "selects"):
        ports = {nm: (pos, axis, BORE) for nm, (pos, axis) in valve_ports(which).items()}
        R.frame(f"{which}-tray-assembly", parts[f"{which}-tray"], ports)
    for nm, _f, _t, _s in COLUMNS:
        ports = {p: (pos, axis, BORE) for p, (pos, axis) in tee_ports(nm).items()}
        R.frame(nm, parts[nm], ports)

    runs = []
    for tee, src, sel, _sign in COLUMNS:
        tag = tee.split("-")[1].upper()
        runs.append(R.bent(
            f"{src}→{tee}", f"source-tray-assembly.{src}", f"{tee}.{tag}-1",
            kind="fluid", bend=BEND, lead=LEG_LEAD,
            note=f"{src} down the column into the tee's run"))
        runs.append(R.bent(
            f"{tee}→{sel}", f"{tee}.{tag}-2", f"selects-tray-assembly.{sel}",
            kind="fluid", bend=BEND, lead=LEG_LEAD,
            note=f"the tee's run on down the column into {sel}"))
    runs.append(R.route(
        "crossbar", "tee-ac.AC-3", "tee-bd.BD-3",
        kind="fluid", bend=BEND, stub=0.0,
        note="the H's bar: branch to branch, one straight length"))
    return runs


# How far a collet face may sit off its own bore wall before `selftest` calls it adrift.
COLLET_TOL = 0.25


def _beyond(pos: tuple, axis: tuple, span: float = 120.0):
    """The half-space `COLLET_TOL` past a collet face, along the way it opens — what none of
    the fitting behind it may reach into. World-aligned axes only, which every collet here
    is; a clocked one would need the box turned with it and says so rather than guessing."""
    off = [i for i in range(3) if abs(axis[i]) > 1e-9]
    if len(off) != 1 or abs(abs(axis[off[0]]) - 1.0) > 1e-9:
        raise ValueError(
            f"collet axis {tuple(round(c, 3) for c in axis)} is off the world axes — "
            f"`_beyond` cannot box it without being turned with it")
    i, sign = off[0], axis[off[0]]
    lo = [p - span / 2.0 for p in pos]
    lo[i] = pos[i] + COLLET_TOL if sign > 0 else pos[i] - COLLET_TOL - span
    return (cq.Workplane("XY")
            .box(span, span, span, centered=(False, False, False))
            .translate(tuple(lo)).val())


def paths() -> dict:
    """Port to port through the junction, for each of the four modes the topology opens:
    the tube each leg cuts, plus the fitting bodies the path actually passes through.

    A straight column is one tee's whole run. A crossed pair is half a run, a branch, the
    crossbar, the other branch, and half the other run. Both are quoted the same way, so
    the two are comparable to each other and to the arrangement they replace."""
    by_id = {r.id: r.length for r in build_runs()}
    out = {}
    for tee, src, sel, _sign in COLUMNS:
        legs = by_id[f"{src}→{tee}"] + by_id[f"{tee}→{sel}"]
        out[f"{src[:3]}→{sel[:3]}"] = legs + 2.0 * RUN_HALF
    for tee, src, _sel, _s in COLUMNS:
        other, _o, sel, _os = next(c for c in COLUMNS if c[0] != tee)
        out[f"{src[:3]}→{sel[:3]}"] = (
            by_id[f"{src}→{tee}"] + RUN_HALF + BRANCH_REACH
            + by_id["crossbar"] + BRANCH_REACH + RUN_HALF + by_id[f"{other}→{sel}"])
    return out


def selftest() -> None:
    """The instrument, not the layout.

    Two things, and the first is the one that matters: every collet a run is authored to
    must land ON the body that declares it. A port table is a second implementation of the
    pose its solid already has, and the two can disagree silently — a run leaves the
    position it was told and arrives nowhere near the fitting, with no volume shared by
    anything to show for it. So each collet face is measured against its own placed solid
    exactly, and must sit on its surface.

    Then that nothing stands in anything else: every placed body against every other. A
    tube butts its collet face and stops, so a shared volume anywhere is a fault, not a
    fit."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp

    parts = build_parts()
    adrift = []
    ports = {nm: tee_ports(nm) for nm, _f, _t, _s in COLUMNS}
    for which in ("source", "selects"):
        ports[f"{which}-tray"] = valve_ports(which)
    for owner, table in ports.items():
        for nm, (pos, axis) in table.items():
            # A valve's collet stands on the VALVE, not on the plate under it.
            body = parts[nm.rsplit("-", 1)[0]] if nm.startswith("V-") else parts[owner]
            # A collet face is the mouth of a bore, so its centre is not ON material — the
            # nearest is the bore wall, one bore radius out. Two measurements pin it:
            # material within that radius, and NONE of the body past the face. Either alone
            # can be passed by a body that is merely near; together they say the face is
            # where the port says it is, and which way the fitting is turned.
            probe = cq.Vertex.makeVertex(*pos)
            dss = BRepExtrema_DistShapeShape(probe.wrapped, body.wrapped)
            if not dss.IsDone():
                raise RuntimeError(f"distance failed for {owner}.{nm} — unknown, not clear")
            if dss.Value() > BORE / 2.0 + COLLET_TOL:
                adrift.append(
                    f"{owner}.{nm} stands {dss.Value():.2f} mm off its own body — no "
                    f"material within a bore radius of the collet face")
            past = _beyond(pos, axis)
            common = BRepAlgoAPI_Common(past.wrapped, body.wrapped)
            if not common.IsDone():
                raise RuntimeError(f"intersection failed past {owner}.{nm} — unknown")
            props = GProp_GProps()
            BRepGProp.VolumeProperties_s(common.Shape(), props)
            if props.Mass() > 1.0:
                adrift.append(
                    f"{owner}.{nm} has {props.Mass():.0f} mm³ of its own body past it, "
                    f"along {tuple(round(c, 1) for c in axis)} — that is not an open face")
    if adrift:
        raise ValueError(
            "collets are not on the bodies that declare them — the port table and the "
            "placed solid disagree:\n  " + "\n  ".join(adrift))
    print(f"selftest: {sum(len(t) for t in ports.values())} collets, all on their bodies")

    bodies = dict(parts)
    for run in build_runs():
        bodies[run.id] = R.tube(run)
    names = sorted(bodies)
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            common = BRepAlgoAPI_Common(bodies[a].wrapped, bodies[b].wrapped)
            if not common.IsDone():
                raise RuntimeError(f"intersection failed for {a} ∩ {b} — unknown, not clear")
            props = GProp_GProps()
            BRepGProp.VolumeProperties_s(common.Shape(), props)
            vol = props.Mass()
            if vol > 1e-6:
                bad.append(f"{a} ∩ {b}: {vol:.1f} mm³")
    if bad:
        raise ValueError("bodies share volume:\n  " + "\n  ".join(bad))
    print(f"selftest: {len(names)} bodies, {len(names) * (len(names) - 1) // 2} pairs, all clear")
    for mode, mm in sorted(paths().items()):
        print(f"  {mode}: {mm:.1f} mm port to port")


def build() -> cq.Assembly:
    assy = cq.Assembly(name="selects-source-assembly")
    parts = build_parts()
    for nm, shape in parts.items():
        color = (TRAY_COLOR if nm.endswith("-tray")
                 else TEE_COLOR if nm.startswith("tee-") else VALVE_COLOR)
        assy.add(shape, name=nm, color=color)
    for run in build_runs():
        assy.add(R.tube(run), name=run.id, color=TUBE_COLOR)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "selects-source-assembly.step"))
    print("-> selects-source-assembly.step")
    runs = build_runs()
    walk = paths()
    variables = {
        "STACK_PITCH": f"{STACK_PITCH:.4g}",
        "SEAT_PITCH": f"{2 * SEAT_X:.4g}",
        "FACING_SPAN": f"{2 * BRANCH_REACH:.4g}",
        "COLUMN_SPREAD": f"{COLUMN_SPREAD:.3g}",
        "COLUMN_PITCH": f"{2 * COLUMN_X:.4g}",
        "CROSSBAR": f"{CROSSBAR:.4g}",
        "RUN_HALF": f"{RUN_HALF:.4g}",
        "BRANCH_REACH": f"{BRANCH_REACH:.4g}",
        "LEG_LEAD": f"{LEG_LEAD:.4g}",
        "TEE_STANDOFF": f"{TEE_STANDOFF:.4g}",
        "TUBE_TOTAL": f"{sum(r.length for r in runs):.4g}",
        "STRAIGHT_PATH": f"{walk['V-A→V-C']:.4g}",
        "CROSSED_PATH": f"{walk['V-A→V-D']:.4g}",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={
            "STACK_PITCH": 1, "SEAT_PITCH": 1, "FACING_SPAN": 1, "COLUMN_SPREAD": 1,
            "COLUMN_PITCH": 1, "CROSSBAR": 1, "RUN_HALF": 1, "BRANCH_REACH": 1,
            "LEG_LEAD": 1, "TEE_STANDOFF": 1, "TUBE_TOTAL": 1,
            "STRAIGHT_PATH": 2, "CROSSED_PATH": 2,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        _here,
        variables={"FACING_SPAN": variables["FACING_SPAN"],
                   "SEAT_PITCH": variables["SEAT_PITCH"],
                   "COLUMN_SPREAD": variables["COLUMN_SPREAD"]},
        expected_counts={"FACING_SPAN": 1, "SEAT_PITCH": 1, "COLUMN_SPREAD": 1},
    )
    print(f"-> {_here.name} (self)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    else:
        main()
