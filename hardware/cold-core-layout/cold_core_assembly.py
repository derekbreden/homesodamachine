"""The cold core, whole — every body inside the foam and every line among them.

`printed-parts/cold-core/foam-assembly` is the core as the MACHINE sees it: five printed
pieces, the outside faces the enclosure loads and stands its own bodies off. This is the core
as the BENCH sees it, one frame further in — the carbonator that fills it, the coil wound on that,
both reservoirs in their pockets, the fittings made up on every port, and the lines drawn
among all of them.

FRAME: the foam shell's own. Z up, the shell floor's outer face at z = 0, the shell's open top
at `foam_shell_outer_height`. ±Y is the carbonator's port axis and +X the register azimuth.
`foam_assembly.stack_floor_z` and `.cap_face_z` are the two planes the appliance reads.

    tools/cad-venv/bin/python hardware/cold-core-layout/cold_core_assembly.py

writes `cold-core-assembly.step` beside this file with its `.scorecard.json`, which the 3D
viewer's bottom bar reads at `/3d`. THE SAME CARD IS WRITTEN BESIDE `foam-assembly.step`, the
outer model of this same core: a reader who opens either one is looking at the cold core, and
the cold core has one verdict.
"""

from __future__ import annotations

import math
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

from _cadq_export import export_assembly, import_step                 # noqa: E402
import _overlap                                          # noqa: E402
import foam_assembly as _foam                            # noqa: E402
import _internal_routes as _routes                       # noqa: E402
import copper_plugs as _plugs                            # noqa: E402
from _cold_core_interface import foam_shell_outer_height  # noqa: E402
import _carbonator as _V                                     # noqa: E402
import _coil as _C                                       # noqa: E402
import _fittings as _F                                   # noqa: E402
import _internals as _I                                  # noqa: E402
import _bom as _bom_check                                # noqa: E402
import prv_shroud as _shroud                             # noqa: E402
import _cold_scorecard as _card                          # noqa: E402
import _cold_core_style as _style                        # noqa: E402
from _card import Check, grade_of, verdict                # noqa: E402
from _cold_scorecard import Scorecard                     # noqa: E402

STEP_OUT = _here.parent / "cold-core-assembly.step"
# The OTHER model of this same core: five printed pieces and the faces the enclosure loads
# (`foam_assembly`). It is not superseded — `enclosure_assembly` places THAT, not this — but a
# reader who opens it is looking at the cold core, and the cold core has one verdict. So the
# card below is written beside both STEPs.
FOAM_STEP = _cold / "foam-assembly" / "foam-assembly.step"

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
    "copper-plug-west": "wall slot",
    "copper-plug-port": "wall slot",
    "prv-shroud": "the PRV it caps",
    "prv-sv125": "elbow socket",
    "reed-bridge": "support ring",
    "evap-coil": "the carbonator it clamps",
    "evap-tail-inlet": "wall slot",
    "evap-tail-outlet": "wall slot",
    "water-inlet-jet-cap-nominal": "water elbow tip weld (unqualified)",
}
for _n in _V.PORTS:
    HELD_BY[f"carbonator-elbow-{_n}"] = "plate thread"

# What holds the bodies that come in families, by the name each family shares.
HELD_BY_PREFIX = (
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
# length of copper — `_coil.cut_length` is one cut — so the volume they share is the
# joint, and drawing it as three children is what lets each carry its own colour.
JOINED = {frozenset(p) for p in (
    ("evap-coil", "evap-tail-inlet"),
    ("evap-coil", "evap-tail-outlet"),
)}

# Bodies the wrap RIDES ON rather than routes around. THE CARBONATOR IS THE ONE IT IS WOUND ON:
# `_coil` stands the wrap's centreline one tube radius off the carbonator's OD, so the copper's inner
# surface and the cylinder's outer are the same surface, and the thermal tape is what lies in
# `coil_radial_clearance` between them. The reed bridge stands on the carbonator on the register
# azimuth and carries the two carbonator reeds in pockets `reed_bridge.pocket_depth` proud of
# the wall; the copper crossing it lifts onto the bridge's own plateau, and that lift IS what
# leaves the glass its `copper_clearance_over_glass`. `_coil.wrap_length` carries the length
# that costs and `bom.md` §5 bills it — but the drawn SOLID is the wrap's nominal circle
# (`_coil.helix_wire` says why), so in this frame all four read as shared volume. The clearance
# itself is checked where the bridge is built, against the bridge's own pocket.
RIDES_ON = {frozenset(p) for p in (
    ("evap-coil", "carbonator-tube"),
    ("evap-coil", "reed-bridge"),
    ("evap-coil", "reed-carb-1"),
    ("evap-coil", "reed-carb-2"),
)}

# The copper that travels a lane. The wrap is fixed on the carbonator the moment it is wound, so a
# fluid line clears it the way it clears any body; the two tails run the same lanes the fluid
# lines run, and `lines-apart` grades them together.
TAIL_LINES = ("evap-tail-inlet", "evap-tail-outlet")

# The fitting each line is MADE UP ON at either end. A body a line lands on is not a body it
# has to route around, so it is out of that line's own obstacle set — and only that line's.
MADE_UP_ON = {
    "co2-in": ("collet-co2-in", "carbonator-elbow-co2-in"),
    "carb-water-out": ("collet-carb-water-out", "carbonator-elbow-carb-water-out"),
    "water-in": ("collet-water-in", "carbonator-elbow-water-in"),
    "reservoir-a": ("bulkhead-reservoir-a",),
    "reservoir-b": ("bulkhead-reservoir-b",),
    # The vent starts IN the shroud's own bore, so the cup it leaves is not a body it routes
    # around — it is the fitting this line is made up on.
    "prv-vent": ("prv-shroud",),
}



def _load(path: Path):
    return import_step(str(path)).val()


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
        (0, 0, _V.carbonator_bottom_z))

    return placed


# The shroud's own frame, as two directions. The cup is authored on +Z with its vent bored
# radially through its own −Y (`prv-shroud/prv_shroud.py`), and standing it on the elbow's axis
# fixes only two of its three freedoms — the roll about that axis is left, and the VENT is what
# spends it. The bore has to open on the barrel's underside so the line leaves already pointing
# down the lane it falls; a cup rolled any other way sends the tube sideways into the cap.
VENT_LOCAL = (0.0, -1.0, 0.0)
VENT_WORLD = (0.0, 0.0, -1.0)


def _turn(v: cq.Vector, axis: cq.Vector) -> cq.Vector:
    """`_fittings._orient`'s own rotation, applied to a direction rather than a solid."""
    z = cq.Vector(0, 0, 1)
    dot = max(-1.0, min(1.0, z.dot(axis)))
    if dot > 1 - 1e-12:
        return v
    if dot < -1 + 1e-12:
        return cq.Vector(v.x, -v.y, -v.z)          # the 180° about +X `_orient` takes
    n = z.cross(axis).normalized()
    angle = math.acos(dot)
    return (v.multiply(math.cos(angle))
            + n.cross(v).multiply(math.sin(angle))
            + n.multiply(n.dot(v) * (1.0 - math.cos(angle))))


def _stand_shroud(solid):
    """One body of the shroud's own frame, placed on the PRV elbow's mouth.

    `_fittings._orient` stands the cup's +Z on the mouth's axis and picks the roll
    INCIDENTALLY — it rotates about `z × axis`, and which way that lands the vent flips with
    the sign of the port's own Y. So the roll is struck here instead of inherited: whatever
    `_orient` leaves, this turns about the mouth's axis until the vent faces the shell's own
    −Z. Both the cup and `prv_vent_mouth`'s marker go through this one placement, so the bore
    the line starts on and the bore in the printed part cannot drift apart."""
    mouth = _V.mouths()["prv"]
    axis = cq.Vector(*mouth.axis).normalized()
    vent = _turn(cq.Vector(*VENT_LOCAL), axis)
    down = cq.Vector(*VENT_WORLD)
    roll = math.degrees(math.atan2(axis.dot(vent.cross(down)), vent.dot(down)))
    return (_F._orient(solid, axis)
            .rotate(cq.Vector(0, 0, 0), axis, roll)
            .translate(cq.Vector(*mouth.pos)))


def _prv_stack() -> dict:
    """The SV-125 made up on the top plate's PRV elbow, and the shroud standing over it.

    The shroud is a cup on +Z with its open end at Z=0, so it stands on the elbow's own mouth
    and reaches `prv_shroud.total_length` along the axis the valve leaves on."""
    mouth = _V.mouths()["prv"]
    valve = _F.sv125(at=mouth.pos, axis=mouth.axis)
    shroud = _stand_shroud(_load(_cold / "prv-shroud" / "prv-shroud.step"))
    return {"prv-sv125": valve, "prv-shroud": shroud}


def prv_vent_mouth() -> tuple:
    """Where the shroud's own vent bore opens, in the shell's frame.

    `prv_shroud` authors the bore radially on its own −Y at `vent_station_z` along the barrel.
    Standing the cup on the elbow's axis carries that point with it, so the line's start is
    read off the SHROUD rather than restated here — a bore that moves takes its tube along."""
    local = cq.Solid.makeSphere(0.001, cq.Vector(0.0, -_shroud.outer_diameter / 2.0,
                                                 _shroud.vent_station_z))
    at = _stand_shroud(local).BoundingBox()
    return (round(at.center.x, 6), round(at.center.y, 6), round(at.center.z, 6))


def trimmed_routes() -> dict:
    """Every authored centreline, with each carbonator end moved out to the mouth its own fitting
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
        a.add(solid, name=name, color=_style.colour_for(name))
    for name in sorted(fitted):
        a.add(fitted[name][1], name=f"line-{name}", color=_style.ROUTE_COLORS[name])
    a.placed = placed
    a.fitted = fitted
    a.points = trimmed_routes()
    return a


# --- the card ----------------------------------------------------------------

def _bodies_clear(placed: dict) -> Check:
    """No two solids share volume. Mating faces touch at zero."""
    names = sorted(placed)
    detail = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if frozenset((a, b)) in JOINED or frozenset((a, b)) in RIDES_ON:
                continue
            vol = _overlap.volume(placed[a], placed[b])
            if vol > _card.TOUCH_VOLUME:
                detail.append(f"{a} ∩ {b} = {vol:.2f} mm³")
    detail.sort(key=lambda s: -float(s.split("= ")[1].split(" ")[0]))
    detail += [f"{' ∩ '.join(sorted(p))}: the wrap rides it — see RIDES_ON"
               for p in sorted(RIDES_ON, key=lambda q: sorted(q))]
    return Check("bodies-clear", "No two placed solids share volume", "gate",
                 verdict(not [d for d in detail if "RIDES_ON" not in d]),
                 f"{len([d for d in detail if 'RIDES_ON' not in d])} clash", "0 clash", detail)


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
            vol = _overlap.volume(tube, solid)
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
            vol = _overlap.volume(runs[a], runs[b])
            if vol > _card.TOUCH_VOLUME:
                detail.append(f"{a} and {b} share {vol:.2f} mm³ — two runs in one corridor")
    return Check("lines-apart", "No two runs want the same corridor", "gate",
                 verdict(not detail), f"{len(detail)} crossing", "0 crossing", detail)


def _floats_couple(placed: dict) -> Check:
    """Running clearance and float-edge to reed-center distance within the design limit.

    This is geometry, not installed reed actuation or liquid calibration.
    """
    detail = []
    seats = _I.float_seats({n: s for n, s in placed.items() if n.startswith("reservoir-")})
    good = 0
    for name, (park, wall, _centre, standoff) in sorted(seats.items()):
        minimum_gap = standoff - 2 * _I.FLOAT_SLOP
        reed_axis = _I.carbonator_reed_x() if name == "float-carb" else _I.REED_COLUMN_X
        edge_path = _I._float.reed_edge_distance(park, reed_axis)
        float_path = _I._float.reed_float_edge_distance(park, reed_axis)
        good += minimum_gap >= 1.0 and float_path <= _I.FLOAT_EDGE_DESIGN_MAXIMUM
        detail.append(f"{name}: body/wet-wall gap {minimum_gap:.3f}..{standoff:.3f} mm; "
                      f"float-edge to reed-centre at most {float_path:.3f} mm; "
                      f"reed-centre to RC62 edge at most {edge_path:.3f} mm; "
                      "installed switching height unmeasured")
    return Check("floats-couple", "Aero floats clear their walls within the float-edge reed distance limit",
                 "gate", verdict(good == len(seats)), f"{good}/{len(seats)} floats",
                 f">=1 mm body clearance, <={_I.FLOAT_EDGE_DESIGN_MAXIMUM:g} mm float-edge to reed-centre; geometry only", detail)


def _arcs_hold(fitted: dict, points: dict) -> Check:
    """Every corner at the stock arc, or the reading it came back at.

    A line is fitted at ONE arc, and that arc is what its corners ask for. What each one turns
    at is what `_internal_routes.corner_radii` hands back: every corner starts at the line's arc
    and comes down until every leg holds the setbacks its two ends want. So a line fitted at
    stock can still turn a corner under it where a leg runs short, and the reading is each
    corner's own."""
    stock = _routes.route_bend_radius
    detail = []
    total = 0
    for name in sorted(fitted):
        bend, _tube = fitted[name]
        v, radii = _routes.corner_radii(points[name], bend)
        for i, r in enumerate(radii[1:-1], start=1):
            total += 1
            if r < stock - 1e-9:
                detail.append(f"{name} corner {i} at ({v[i].x:.1f}, {v[i].y:.1f}, {v[i].z:.1f}) "
                              f"turns at {r:.2f} mm against the {stock:.2f} mm stock arc")
    return Check("arcs-hold", "Every corner turns at the stock arc", "gate",
                 verdict(not detail), f"{total - len(detail)}/{total} corners at stock",
                 f"{stock:.2f} mm", detail)


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
            "grade": grade_of(ratio) if corners else None,
            "reach": round(reach, 2) if reach > 1e-9 else None,
            "reachGrade": None if reach <= 1e-9 else grade_of(min(1.5, reach / length)),
            "binding": None,
            "corners": [{"at": i, "radius": round(r, 3),
                         "ratio": round(r / stock, 3), "grade": grade_of(r / stock)}
                        for i, r in enumerate(radii[1:-1], start=1) if r > 0.0],
            "need": {"detour": round(length / reach, 3) if reach > 1e-9 else None},
        })
    return rows


def _endpoint_label(line: str, which: str) -> str:
    """Which body's mouth an end of this line lands on, where one is declared."""
    for port, (name, side) in _V.PORT_LINES.items():
        if name == line and side == which:
            return f"carbonator.{port}"
    return f"{line}.{which}"


def _goal(cid: str, label: str, done: int, total: int, target: str, detail=()) -> Check:
    return Check(cid, label, "goal", verdict(done == total), f"{done}/{total}", target,
                 list(detail))


def build_card(a) -> Scorecard:
    placed, fitted = a.placed, a.fitted
    mouths = [("carbonator", n, m, n) for n, m in _V.mouths().items()]
    mouths += [(f"bulkhead-{n}", "collet", m, n) for n, m in _I.mouths().items()]
    # `by` is what FASTENS a body and `joint` the construction it stands on. Here they are the
    # same feature wherever one exists, and `by` is None for the two the tape holds — which is
    # what the `mounted` goal below counts.
    mounts = [(n, None if held_for(n) in NOT_A_FEATURE else held_for(n), held_for(n))
              for n in sorted(placed)]

    checks = [
        _bodies_clear(placed),
        _routes_fit(placed, fitted),
        _lines_apart(fitted, placed),
        _bom_check.check(placed),
        _arcs_hold(fitted, a.points),
        _floats_couple(placed),
        Check("inlet-jet-qualified", "The inlet jet's actual joint and fit are qualified",
              "goal", "warn", "nominal layout only", "measured fit and qualified weld",
              ["The cap is drawn at nominal 9.5 mm diameter, 2 mm thickness and a 1/16-inch passage.",
               "The elbow bore and installed tip projection are unmeasured layout assumptions; "
               "the model does not establish the weld land, penetration or pressure integrity.",
               "Qualify the coupon, passage and made-up port using assembly/water-inlet-jet.md."]),
        Check("gas-adapter-envelope", "The gas collet matches its acquired PI010822S",
              "goal", "warn", "shared nominal envelope", "measured gas-adapter envelope",
              ["The gas port carries the PI010822S identity and gray acetal material; "
               "its envelope is represented by the existing PP010822E layout reference until measured."]),
        _goal("placed", "Every body the core carries is placed", len(placed), len(placed),
              "a solid per body"),
        _goal("located", "Every port a placed body declares is positioned",
              len(mouths), len(mouths), "every mouth located"),
        _goal("routed", "Every line the core owes is drawn", len(fitted), len(fitted),
              "a line per connection"),
        _goal("mounted", "A feature of another placed part locates every body",
              sum(1 for _n, by, _j in mounts if by is not None), len(mounts),
              "a located joint per body",
              [f"{n}: {j}" for n, by, j in mounts if by is None]),
    ]
    return Scorecard(checks, _bend_rows(fitted, a.points), sorted(placed))


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
    # AND THE FLUTED SURFACES INTO THE PAYLOAD THE VIEWER READS. The shell and both caps carry a
    # show skin that is in the printed mesh and not in the solid (`cold-core/_show_skin.py`), so
    # the payload written beside this STEP holds three smooth prisms until they are put back.
    # `loadStepFile` prefers that payload to the STEP, so this is what /3d draws.
    #
    # IMPORTED HERE AND NOT AT THE TOP, the way `enclosure_assembly` does it: `flute_payload`
    # pulls in a decimator and a proximity index that only the run which cuts an assembly uses.
    #
    # AND ASKED FOR THE CORE'S TREE, not the disk. This assembly holds cold-core bodies and no
    # others, so the box's six fluted pieces are surfaces it can never graft — and indexing them
    # makes the action hold the whole enclosure to read six payloads it puts down again.
    import flute_payload                                                # noqa: E402
    _grafted = flute_payload.graft(Path(str(STEP_OUT) + ".mesh"),
                                   flute_payload.surfaces(flute_payload.COLD_CORE_DIRS))
    if _grafted:
        print(f"-> {Path(str(STEP_OUT)).name}.mesh  ({_grafted} fluted piece(s))")
    print(f"-> {STEP_OUT.name}")
    report(a)
    sc = build_card(a)
    _card.report(sc)
    for step in (STEP_OUT, FOAM_STEP):
        out = _card.write(sc, step)
        print(f"\n-> {out.relative_to(_hw)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
