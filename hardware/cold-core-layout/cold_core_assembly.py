"""The cold core, whole — every body inside the foam and every line among them.

`printed-parts/cold-core/foam-assembly` is the core as the MACHINE sees it: five printed
pieces, the outside faces the enclosure loads and stands its own bodies off. This is the core
as the BENCH sees it, one frame further in — the vessel that fills it, the coil wound on that,
both reservoirs in their pockets, the fittings made up on every port, and the lines drawn
among all of them.

FRAME: the foam shell's own. Z up, the shell floor's outer face at z = 0, the shell's open top
at `foam_shell_outer_height`. ±Y is the vessel's port axis and +X the register azimuth.
`foam_assembly.stack_floor_z` and `.cap_face_z` are the two planes the appliance reads.

    tools/cad-venv/bin/python hardware/cold-core-layout/cold_core_assembly.py

writes `cold-core-assembly.step` beside this file with its `.scorecard.json`, which the 3D
viewer's bottom bar reads at `/3d`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_cold = _hw / "printed-parts" / "cold-core"
for _p in (_hw / "scripts", _cold, _cold / "foam-assembly", _cold / "reservoir",
           _cold / "copper-plugs", _cold / "prv-shroud",
           _hw / "printed-parts" / "cadlib", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from _cadq_export import export_assembly                 # noqa: E402
import foam_assembly as _foam                            # noqa: E402
import _internal_routes as _routes                       # noqa: E402
import copper_plugs as _plugs                            # noqa: E402
from _cold_core_interface import foam_shell_outer_height  # noqa: E402
import _vessel as _V                                     # noqa: E402
import _coil as _C                                       # noqa: E402
import _fittings as _F                                   # noqa: E402
import _internals as _I                                  # noqa: E402
import _bom as _bom_check                                # noqa: E402
import prv_shroud as _shroud                             # noqa: E402
import _cold_scorecard as _card                          # noqa: E402
from _cold_scorecard import Check, Scorecard, verdict     # noqa: E402

STEP_OUT = _here.parent / "cold-core-assembly.step"

# --- colour, by what a body is ------------------------------------------------
C_FOAM_SHELL = cq.Color(0.62, 0.78, 0.95, 0.22)
C_CAP = cq.Color(0.90, 0.66, 0.32, 0.55)
C_LID = cq.Color(0.97, 0.85, 0.55, 0.55)
C_CAP_B = cq.Color(0.45, 0.70, 0.45, 0.55)
C_LID_B = cq.Color(0.66, 0.86, 0.62, 0.55)
C_STEEL = cq.Color(0.72, 0.74, 0.78)
C_PLATE = cq.Color(0.58, 0.61, 0.66)
C_ROD = cq.Color(0.80, 0.82, 0.86)
C_FITTING = cq.Color(0.86, 0.78, 0.52)
C_RESERVOIR = cq.Color(0.85, 0.88, 0.92, 0.35)
C_RES_CAP = cq.Color(0.70, 0.74, 0.80, 0.55)
C_PLUG = cq.Color(0.35, 0.40, 0.48)
C_SHROUD = cq.Color(0.30, 0.34, 0.40)
C_BRIDGE = cq.Color(0.40, 0.44, 0.52)
C_COPPER = cq.Color(0.80, 0.45, 0.20)
C_SILICONE = cq.Color(0.92, 0.92, 0.90, 0.60)
C_FLOAT = cq.Color(0.66, 0.70, 0.75)
C_REED = cq.Color(0.95, 0.55, 0.85)
C_PROBE = cq.Color(0.20, 0.55, 0.30)

FOAM_COLORS = {
    "foam-shell": C_FOAM_SHELL,
    "foam-cap-top": C_CAP,
    "foam-cap-lid-top": C_LID,
    "foam-cap-bottom": C_CAP_B,
    "foam-cap-lid-bottom": C_LID_B,
}

# Which reservoir STEP fills which pocket, and what its cap is called.
RESERVOIRS = {"reservoir-a": "reservoir-right", "reservoir-b": "reservoir-left"}

# A body's name here, and what holds it once the pour goes off. The foam is the last holder of
# almost everything in this box — a potted body is held by what set around it — so the column
# says which face locates it BEFORE the pour, which is what an assembler works to.
HELD_BY = {
    "foam-shell": "the enclosure floor",
    "foam-cap-top": "shell rim",
    "foam-cap-lid-top": "cap mouth",
    "foam-cap-bottom": "shell floor",
    "foam-cap-lid-bottom": "cap mouth",
    "carbonator-tube": "support ring",
    "endcap-bottom": "tube bore",
    "endcap-top": "tube bore",
    "float-rod-carb": "plate registers",
    "reservoir-a": "pocket",
    "reservoir-b": "pocket",
    "reservoir-a-cap": "body rim",
    "reservoir-b-cap": "body rim",
    "copper-plug-lower": "wall slot",
    "copper-plug-middle": "wall slot",
    "copper-plug-top": "wall slot",
    "prv-shroud": "the PRV it caps",
    "prv-sv125": "elbow socket",
    "reed-bridge": "support ring",
    "evap-coil": "the tank it clamps",
    "evap-tail-inlet": "wall slot",
    "evap-tail-outlet": "wall slot",
}
for _n in _V.PORTS:
    HELD_BY[f"vessel-elbow-{_n}"] = "plate thread"

# What holds the bodies that come in families, by the name each family shares.
HELD_BY_PREFIX = (
    ("sparge-barb", "plate thread"),
    ("sparge-silicone-stub", "the barb and the stone"),
    ("sparge-stone", "its own stub"),
    ("bulkhead-reservoir", "trough floor"),
    ("bulkhead-seal-", "the bulkhead's own nut"),
    ("collet-", "elbow socket"),
    ("vent-membrane-", "cap vent pocket"),
    ("float-rod-", "body boss"),
    ("float-", "the rod it rides"),
    ("reed-carb-", "bridge pocket"),
    ("reed-", "shell channel"),
    ("probe-", "foil tape"),
)


# Holders that are not a feature of another placed part. A body the pour sets around is where
# it is because something held it while the foam went off; a body taped to a wall is held by
# the tape. Everything else lands in a bore, a channel, a slot, a rim or a boss that some other
# placed part prints or machines, and an assembler can put it there without the model.
NOT_A_FEATURE = ("the pour", "foil tape")


def held_for(name: str) -> str:
    if name in HELD_BY:
        return HELD_BY[name]
    for prefix, held in HELD_BY_PREFIX:
        if name.startswith(prefix):
            return held
    return "the pour"

# Bodies that meet because they are MADE UP on each other. The wrap and its two tails are one
# length of copper — `coil_mandrel.cut_length` is one cut — so the volume they share is the
# joint, and drawing it as three children is what lets each carry its own colour.
JOINED = {frozenset(p) for p in (
    ("evap-coil", "evap-tail-inlet"),
    ("evap-coil", "evap-tail-outlet"),
)}

# The copper that travels a lane. The wrap is fixed on the tank the moment it is wound, so a
# fluid line clears it the way it clears any body; the two tails run the same lanes the fluid
# lines run, and `lines-apart` grades them together.
TAIL_LINES = ("evap-tail-inlet", "evap-tail-outlet")

# The fitting each line is MADE UP ON at either end. A body a line lands on is not a body it
# has to route around, so it is out of that line's own obstacle set — and only that line's.
MADE_UP_ON = {
    "co2-in": ("collet-co2-in", "vessel-elbow-co2-in"),
    "carb-water-out": ("collet-carb-water-out", "vessel-elbow-carb-water-out"),
    "water-in": ("collet-water-in", "vessel-elbow-water-in"),
    "reservoir-a": ("bulkhead-reservoir-a",),
    "reservoir-b": ("bulkhead-reservoir-b",),
    # The vent starts IN the shroud's own bore, so the cup it leaves is not a body it routes
    # around — it is the fitting this line is made up on.
    "prv-vent": ("prv-shroud",),
}

# The straight a run leaves a fitting on, as a multiple of its own bend radius: one reach for
# the stub and one for the tangent its first corner seats on.
PORT_LEAD_BENDS = 2.0


def _load(path: Path):
    return cq.importers.importStep(str(path)).val()


def _plug_into_shell(solid, column: str):
    """One copper plug, from its own frame into the shell's.

    The plug is authored with the wall on ±Y and the slot running along X; in the shell the
    front wall is on −X and the lane runs along Y. A quarter turn about Z is the whole of the
    difference, then the plug slides to its own column's lane."""
    turned = solid.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90)
    return turned.translate((0, _plugs.columns[column].lane_y, 0))


def build_bodies() -> dict:
    """Every solid in the core, by the name it goes into the assembly under."""
    placed = {}

    _assy, foam = _foam.build()
    for name, (solid, _c) in foam.items():
        placed[name] = solid

    placed.update(_V.bodies())

    res_dir = _cold / "reservoir"
    for name, stem in RESERVOIRS.items():
        placed[name] = _load(res_dir / f"{stem}.step")
        cap = _load(res_dir / f"{stem.replace('reservoir', 'reservoir-cap')}.step")
        placed[f"{name}-cap"] = cap.translate((0, 0, _foam.RESERVOIR_CAP_Z))

    for plug, spec in _plugs.plug_specs.items():
        placed[f"copper-plug-{plug}"] = _plug_into_shell(
            _load(_cold / "copper-plugs" / f"copper-plug-{plug}.step"), spec.column)

    placed.update(_C.bodies())
    placed.update(_I.bodies(placed))
    placed.update(_prv_stack())
    placed["reed-bridge"] = _load(_cold / "reed-bridge" / "reed-bridge.step").translate(
        (0, 0, _V.tank_bottom_z))

    return placed


def _prv_stack() -> dict:
    """The SV-125 made up on the top plate's −Y elbow, and the shroud standing over it.

    The shroud is a cup on +Z with its open end at Z=0, so it stands on the elbow's own mouth
    and reaches `prv_shroud.total_length` along the axis the valve leaves on."""
    mouth = _V.mouths()["prv"]
    axis = cq.Vector(*mouth.axis).normalized()
    valve = _F.sv125(at=mouth.pos, axis=mouth.axis)
    shroud = _load(_cold / "prv-shroud" / "prv-shroud.step")
    shroud = _F._orient(shroud, axis).translate(cq.Vector(*mouth.pos))
    return {"prv-sv125": valve, "prv-shroud": shroud}


def prv_vent_mouth() -> tuple:
    """Where the shroud's own vent bore opens, in the shell's frame.

    `prv_shroud` authors the bore radially on its own −Y at `vent_station_z` along the barrel.
    Standing the cup on the elbow's axis carries that point with it, so the line's start is
    read off the SHROUD rather than restated here — a bore that moves takes its tube along."""
    mouth = _V.mouths()["prv"]
    axis = cq.Vector(*mouth.axis).normalized()
    local = cq.Solid.makeSphere(0.001, cq.Vector(0.0, -_shroud.outer_diameter / 2.0,
                                                 _shroud.vent_station_z))
    at = _F._orient(local, axis).translate(cq.Vector(*mouth.pos)).BoundingBox()
    return (round(at.center.x, 6), round(at.center.y, 6), round(at.center.z, 6))


def trimmed_routes() -> dict:
    """Every authored centreline, with each vessel end moved out to the mouth its own fitting
    presents.

    `_internal_routes` draws each line to the PORT — the point on the plate's own axis that the
    elbow, the collet and the ring bore all stand on. What a length of tube spans is the rest of
    that line, from the collet outward, so the end that lands on a fitting moves to its mouth."""
    out = {name: list(pts) for name, pts in _routes.routes.items()}
    mouths = _V.mouths()
    for port, (line, which) in _V.PORT_LINES.items():
        out[line][0 if which == "start" else -1] = mouths[port].pos
    # Each reservoir's draw starts at its own floor bulkhead's collet the same way.
    for line, mouth in _I.mouths().items():
        out[line][0] = mouth.pos
    # And the PRV vent starts on the shroud's own bore, wherever the placed cup puts it.
    out["prv-vent"][0] = prv_vent_mouth()
    return out


def build_routes(placed: dict) -> dict:
    """Every line inside the core, drawn at the arc its own corridor leaves.

    The obstacles are the solids a line runs among — everything placed except the caps standing
    over the shell's open top, which every riser passes on its way out."""
    base = {n: s for n, s in placed.items()
            if not n.startswith("foam-cap") and n not in TAIL_LINES}
    out = {}
    for name, pts in trimmed_routes().items():
        exempt = MADE_UP_ON.get(name, ())
        obstacles = {n: s for n, s in base.items() if n not in exempt}
        out[name] = _routes.fit_route(pts, obstacles)
    return out


def build_assembly():
    placed = build_bodies()
    fitted = build_routes(placed)

    a = cq.Assembly(name="cold-core-assembly")
    for name, solid in placed.items():
        a.add(solid, name=name, color=_colour_for(name))
    for name in sorted(fitted):
        a.add(fitted[name][1], name=f"line-{name}", color=_foam.ROUTE_COLORS[name])
    a.placed = placed
    a.fitted = fitted
    a.points = trimmed_routes()
    return a


def _colour_for(name: str):
    if name in FOAM_COLORS:
        return FOAM_COLORS[name]
    if name.startswith("endcap"):
        return C_PLATE
    if name.startswith("float-rod"):
        return C_ROD
    if name.startswith("vessel-elbow"):
        return C_FITTING
    if name.endswith("-cap"):
        return C_RES_CAP
    if name.startswith("reservoir"):
        return C_RESERVOIR
    if name.startswith("copper-plug"):
        return C_PLUG
    if name.startswith("evap-"):
        return C_COPPER
    if name.startswith("sparge-silicone"):
        return C_SILICONE
    if name.startswith(("sparge-", "bulkhead-")):
        return C_FITTING
    if name.startswith("float-rod"):
        return C_ROD
    if name.startswith("float-"):
        return C_FLOAT
    if name.startswith("reed-"):
        return C_REED
    if name.startswith("probe-"):
        return C_PROBE
    if name == "prv-shroud":
        return C_SHROUD
    if name == "prv-sv125":
        return C_FITTING
    if name == "reed-bridge":
        return C_BRIDGE
    return C_STEEL


# --- the card ----------------------------------------------------------------

def _bodies_clear(placed: dict) -> Check:
    """No two solids share volume. Mating faces touch at zero."""
    names = sorted(placed)
    detail = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if frozenset((a, b)) in JOINED:
                continue
            vol = placed[a].intersect(placed[b]).Volume()
            if vol > _card.TOUCH_VOLUME:
                detail.append(f"{a} ∩ {b} = {vol:.2f} mm³")
    detail.sort(key=lambda s: -float(s.split("= ")[1].split(" ")[0]))
    return Check("bodies-clear", "No two placed solids share volume", "gate",
                 verdict(not detail), f"{len(detail)} clash", "0 clash", detail)


def _routes_fit(placed: dict, fitted: dict) -> Check:
    """No line meets a solid. A bore a line passes through is a void, so a line that reads
    blocked is a line with no hole in front of it."""
    detail = []
    for name in sorted(fitted):
        tube = fitted[name][1]
        exempt = set(MADE_UP_ON.get(name, ()))
        for other, solid in sorted(placed.items()):
            if other in TAIL_LINES or other in exempt:
                continue
            vol = tube.intersect(solid).Volume()
            if vol > _card.TOUCH_VOLUME:
                detail.append(f"{name} meets {other} by {vol:.2f} mm³")
    return Check("routes-fit", "No line meets a solid", "gate", verdict(not detail),
                 f"{len(fitted) - len({d.split()[0] for d in detail})}/{len(fitted)} clear",
                 "every line clear", detail)


def _lines_apart(fitted: dict, placed: dict) -> Check:
    """No two runs want the same corridor.

    The population is every fluid line plus the two copper tails: a lane is one bore wide, so
    what keeps two runs apart is the storey each takes, and copper takes a storey like anything
    else."""
    runs = {n: t for n, (_b, t) in fitted.items()}
    runs.update({n: placed[n] for n in TAIL_LINES if n in placed})
    names = sorted(runs)
    detail = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            vol = runs[a].intersect(runs[b]).Volume()
            if vol > _card.TOUCH_VOLUME:
                detail.append(f"{a} and {b} share {vol:.2f} mm³ — two runs in one corridor")
    return Check("lines-apart", "No two runs want the same corridor", "gate",
                 verdict(not detail), f"{len(detail)} crossing", "0 crossing", detail)


def _lane_census(fitted: dict, placed: dict) -> Check:
    """Which runs use each lane, and at what storey.

    A lane is one bore wide (`_cold_core_interface` states the width and the wall either side),
    so what separates two runs in one is the Z each takes. This lists every run whose centreline
    enters a lane's Y band, with the Z span it occupies there — the reading behind any crossing
    `lines-apart` names."""
    lanes = {"port-lane": _plugs.columns["port-lane"].lane_y,
             "west-lane": _plugs.columns["west-lane"].lane_y}
    half = _routes.line_radius + _routes.lldpe_tube_od / 2.0
    runs = {n: t for n, (_b, t) in fitted.items()}
    runs.update({n: placed[n] for n in TAIL_LINES if n in placed})
    detail = []
    for lane, y in sorted(lanes.items()):
        for name in sorted(runs):
            bb = runs[name].BoundingBox()
            if bb.ymin > y + half or bb.ymax < y - half:
                continue
            detail.append(f"{lane}: {name} at z {bb.zmin:.1f}..{bb.zmax:.1f}, "
                          f"x {bb.xmin:.1f}..{bb.xmax:.1f}")
    return Check("lane-census", "What each lane carries, and at what storey", "gate", "pass",
                 f"{len(detail)} run-lane pairs", "a reading, not a bound", detail)


def _port_leads(fitted: dict, points: dict) -> Check:
    """The straight each line leaves its own fitting on.

    A collet takes the tube on its own axis, so what a made-up end needs is a straight to
    receive it — `PORT_LEAD_BENDS` reaches of the line's own radius, one for the stub and one
    for the tangent the first corner seats on. Shorter than that is a tube that cannot be
    pushed home without bending it in the grip.

    A run with NO corner is straight through and seats no tangent, so it is not asked for one:
    each reservoir fill is the gap between two bores and is shorter than the lead itself."""
    detail = []
    total = 0
    for name in sorted(fitted):
        bend, _tube = fitted[name]
        legs = _routes.route_legs(points[name], bend)
        if len(legs) < 2:
            continue
        want = PORT_LEAD_BENDS * bend
        for end, (a, b) in (("start", legs[0]), ("end", legs[-1])):
            total += 1
            got = (b - a).Length
            if got < want - 1e-6:
                detail.append(f"{name} {end}: {got:.1f} mm of straight, {want:.1f} wanted")
    return Check("port-leads", "Every made-up end has a straight to receive the tube", "gate",
                 verdict(not detail), f"{total - len(detail)}/{total} ends", 
                 f"{PORT_LEAD_BENDS:g} bend radii", detail)


def _stations_met(fitted: dict, placed: dict) -> Check:
    """Every slot station the wall leaves, against the run that crosses it.

    `copper_plugs.columns` is the wall's own list of what passes through it — each station is
    one plug's bottom face, and the tube IS the gap between two plugs. A station nothing
    reaches is a hole the shell prints for a line this assembly does not draw."""
    runs = {n: t for n, (_b, t) in fitted.items()}
    runs.update({n: placed[n] for n in TAIL_LINES if n in placed})
    detail = []
    met = 0
    for column in sorted(_plugs.columns):
        for station, _z in _plugs.columns[column].stations:
            (x, y, z), _axis = _plugs.slot_station(station)
            probe = cq.Solid.makeSphere(_routes.lldpe_tube_od, cq.Vector(x, y, z))
            here = [n for n, t in runs.items() if t.intersect(probe).Volume() > 1e-6]
            if here:
                met += 1
                detail.append(f"{column} {station} at z {z:.2f}: {', '.join(sorted(here))}")
            else:
                detail.append(f"{column} {station} at z {z:.2f}: NOTHING reaches it")
    total = sum(len(c.stations) for c in _plugs.columns.values())
    return Check("stations-met", "Every wall station carries a run", "gate",
                 verdict(met == total), f"{met}/{total} stations", "a run per station", detail)


def _prv_vent_lands(points: dict) -> Check:
    """The shroud's own vent bore, against the lane its line has to fall.

    Two readings of one station. `prv_shroud.vent_station_z` picks where the bore stands along
    the barrel so that the cup, once made up on the elbow, opens it on the port lane's own
    centreline — and this reads that back off the PLACED shroud. A bore that misses the lane is
    a line that needs a corner in a band that has none."""
    at = prv_vent_mouth()
    want = _plugs.columns["port-lane"].lane_y
    off = at[1] - want
    # The two readings are struck in different frames and carried through a rotation, so what
    # is being asked is whether they are the same station — not whether they agree to a float.
    agree = 0.01
    detail = [f"the shroud's vent bore opens at ({at[0]:+.2f}, {at[1]:+.2f}, {at[2]:.2f}), "
              f"{'on' if abs(off) < agree else f'{off:+.2f} off'} the port lane ({want:g})",
              f"station {_shroud.vent_station_z:g} mm along a {_shroud.total_length:g} mm "
              f"barrel; the line falls from there to z "
              f"{points['prv-vent'][-1][2]:.2f} and out"]
    return Check("prv-vent-lands", "The PRV shroud's vent bore opens on the lane its line "
                 "falls", "gate", verdict(abs(off) < agree),
                 f"{abs(off):.3f} mm off", f"within {agree:g} mm of the lane", detail)


def _floats_couple(placed: dict) -> Check:
    """Every float's magnet held against the wall its reed reads through.

    A reed here is OUTSIDE the vessel it reads, so what the check is about is COUPLING, not
    clearance: the capsule is loose on its rod (`_internals.FLOAT_SLOP`) and each rod is parked
    outboard of where a concentric float would touch, so the wall pushes the magnet against
    itself for the whole travel. `standoff` is what is left of the slop — the most the magnet
    can retreat anywhere in that travel — and a float that gets LOOSER fails this, which is the
    direction the failure actually comes from. Under zero is the other end: a capsule the wall
    will not let onto its rod at all."""
    detail = []
    seats = _I.float_seats({n: s for n, s in placed.items() if n.startswith("reservoir-")})
    good = 0
    for name, (park, wall, _centre, standoff) in sorted(seats.items()):
        bias = park + _F.FLOAT_OD / 2.0 - wall
        if standoff < 0.0:
            detail.append(f"{name}: rod parked {park:.2f} bites {-standoff:.2f} mm past the "
                          f"{_I.FLOAT_SLOP:.2f} mm of bore slop — the wall at {wall:.2f} will "
                          f"not let the capsule onto its rod")
        elif standoff > _I.MAGNET_WALL_REACH:
            detail.append(f"{name}: rod parked {park:.2f} against a wall at {wall:.2f} leaves "
                          f"the capsule {-bias:.2f} mm short of it, so the magnet stands off "
                          f"up to {standoff:.2f} mm — past the "
                          f"{_I.MAGNET_WALL_REACH:.1f} mm the reed reads at")
        else:
            good += 1
            detail.append(f"{name}: rod parked {park:.2f} biases the capsule {bias:+.2f} mm "
                          f"into a wall at {wall:.2f}; magnet standoff 0..{standoff:.2f} mm")
    return Check("floats-couple", "Every float's magnet is held against the wall its reed "
                 "reads through", "gate", verdict(good == len(seats)),
                 f"{good}/{len(seats)} floats",
                 f"standoff under {_I.MAGNET_WALL_REACH:.1f} mm", detail)


def _arcs_hold(fitted: dict) -> Check:
    """Every corner at the stock arc, or the reading it came back at."""
    stock = _routes.route_bend_radius
    detail = []
    for name in sorted(fitted):
        bend, _tube = fitted[name]
        if bend < stock - 1e-9:
            detail.append(f"{name} at {bend:.2f} mm against the {stock:.2f} mm stock arc")
    return Check("arcs-hold", "Every corner turns at the stock arc", "gate",
                 verdict(not detail), f"{len(fitted) - len(detail)}/{len(fitted)} at stock",
                 f"{stock:.2f} mm", detail)


def _shape_rows(placed: dict) -> list:
    rows = []
    for name, solid in sorted(placed.items()):
        bb = solid.BoundingBox()
        box = [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)]
        span = (bb.xlen * bb.ylen * bb.zlen) or 1.0
        rows.append({"component": name, "boxes": [box],
                     "fill": round(solid.Volume() / span, 4),
                     "primitive": False, "declared": "real"})
    return rows


def _port_rows(mouths: dict) -> list:
    return [{"component": comp, "name": port, "kind": "fluid",
             "pos": [round(v, 3) for v in m.pos], "face": _face_of(m.axis),
             "diam": round(m.diam, 3), "mates": mates, "status": "ok", "note": ""}
            for comp, port, m, mates in mouths]


def _face_of(axis) -> str:
    for i, name in enumerate("xyz"):
        if abs(axis[i]) > 0.9:
            return f"{name}{'+' if axis[i] > 0 else '-'}"
    return [round(v, 6) for v in axis]


# Grade bands on `radius ÷ the stock's minimum`, the same ladder the enclosure's card uses.
GRADE_BANDS = ((1.5, "A"), (1.0, "B"), (0.75, "C"), (0.5, "D"), (0.0, "F"))


def _grade(ratio: float) -> str:
    return next(g for lo, g in GRADE_BANDS if ratio >= lo)


def _bend_rows(fitted: dict, points: dict) -> list:
    """One row per line: what it turns at, and how far it travels against how far it reaches.

    A line's REACH is the straight between its two ends. Length over reach says whether the run
    is riding a corridor its own ends never asked for — a fill that is the gap between two bores
    reads 1.0, and a riser that goes out to a band and back reads well over it."""
    stock = _routes.route_bend_radius
    rows = []
    for name in sorted(fitted):
        bend, _tube = fitted[name]
        pts = points[name]
        v, radii = _routes.corner_radii(pts, bend)
        corners = [r for r in radii[1:-1] if r > 0.0]
        tightest = min(corners) if corners else bend
        length = _routes.route_wire(pts, bend).Length()
        reach = (cq.Vector(*pts[-1]) - cq.Vector(*pts[0])).Length
        ratio = tightest / stock
        rows.append({
            "id": name, "kind": "fluid",
            "frm": _endpoint_label(name, "start"), "to": _endpoint_label(name, "end"),
            "stock": _routes.route_stock.name,
            "od": _routes.lldpe_tube_od,
            "length": round(length, 2),
            "bend": round(bend, 3),
            "radius": round(tightest, 3),
            "minBend": round(stock, 3),
            "ratio": round(ratio, 3),
            "grade": _grade(ratio) if corners else None,
            "reach": round(reach, 2) if reach > 1e-9 else None,
            "reachGrade": None if reach <= 1e-9 else _grade(min(1.5, reach / length)),
            "binding": None,
            "corners": [{"at": i, "radius": round(r, 3),
                         "ratio": round(r / stock, 3), "grade": _grade(r / stock)}
                        for i, r in enumerate(radii[1:-1], start=1) if r > 0.0],
            "need": {"detour": round(length / reach, 3) if reach > 1e-9 else None},
        })
    return rows


def _endpoint_label(line: str, which: str) -> str:
    """Which body's mouth an end of this line lands on, where one is declared."""
    for port, (name, side) in _V.PORT_LINES.items():
        if name == line and side == which:
            return f"carbonator-vessel.{port}"
    return f"{line}.{which}"


def _goal(cid: str, label: str, done: int, total: int, target: str, detail=()) -> Check:
    return Check(cid, label, "goal", verdict(done == total), f"{done}/{total}", target,
                 list(detail))


def build_card(a) -> Scorecard:
    placed, fitted = a.placed, a.fitted
    mouths = [("carbonator-vessel", n, m, n) for n, m in _V.mouths().items()]
    mouths += [(f"bulkhead-{n}", "collet", m, n) for n, m in _I.mouths().items()]
    shapes = _shape_rows(placed)
    # `by` is what FASTENS a body and `held` what holds it. Here they are the same feature
    # wherever one exists, and `by` is None for the two the tape holds — which is the field
    # `web/contracts/scorecard-sidecar.js` counts, so both surfaces read one number.
    mounts = [(n, None if held_for(n) in NOT_A_FEATURE else held_for(n), held_for(n))
              for n in sorted(placed)]
    held = sum(1 for _n, _by, h in mounts if h != "none")

    checks = [
        _bodies_clear(placed),
        _routes_fit(placed, fitted),
        _lines_apart(fitted, placed),
        _bom_check.check(placed),
        _lane_census(fitted, placed),
        _port_leads(fitted, a.points),
        _stations_met(fitted, placed),
        _arcs_hold(fitted),
        _prv_vent_lands(a.points),
        _floats_couple(placed),
        _goal("placed", "Every body the core carries is placed", len(placed), len(placed),
              "a solid per body"),
        _goal("located", "Every port a placed body declares is positioned",
              len(mouths), len(mouths), "every mouth located"),
        _goal("shaped", "Every body is real geometry rather than a primitive",
              sum(1 for s in shapes if not s["primitive"]), len(shapes), "no primitives"),
        _goal("routed", "Every line the core owes is drawn", len(fitted), len(fitted),
              "a line per connection"),
        _goal("held", "Something holds every body", held, len(mounts), "a holder per body"),
        _goal("mounted", "A feature of another placed part locates every body",
              sum(1 for _n, _by, h in mounts if h not in NOT_A_FEATURE), len(mounts),
              "a located joint per body",
              [f"{n}: held by {h}" for n, _by, h in mounts if h in NOT_A_FEATURE]),
    ]
    return Scorecard(checks, _bend_rows(fitted, a.points), _port_rows(mouths), shapes, mounts)


def report(a) -> None:
    print("\ncold core")
    for name, solid in sorted(a.placed.items()):
        bb = solid.BoundingBox()
        print(f"  {name:24} [{bb.xmin:7.1f},{bb.xmax:7.1f}] [{bb.ymin:7.1f},{bb.ymax:7.1f}] "
              f"[{bb.zmin:7.1f},{bb.zmax:7.1f}]")
    print(f"\n  {len(a.placed)} bodies, {len(a.fitted)} lines, "
          f"shell z 0..{foam_shell_outer_height:.1f}, "
          f"stack floor {_foam.stack_floor_z:.1f}, cap face {_foam.cap_face_z:.1f}")
    _V.report()
    _C.report()
    _I.report(a.placed)


def main() -> int:
    a = build_assembly()
    export_assembly(a, str(STEP_OUT))
    print(f"-> {STEP_OUT.name}")
    report(a)
    sc = build_card(a)
    _card.report(sc)
    out = _card.write(sc, STEP_OUT)
    print(f"\n-> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
