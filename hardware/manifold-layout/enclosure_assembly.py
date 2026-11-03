"""Rust machine assembly entry point and scalar construction questions."""
from __future__ import annotations

from pathlib import Path
import sys

_here = Path(__file__).resolve()
_hw = _here.parents[1]
sys.path.insert(0, str(_hw / 'scripts'))


def main():
    import _machine_layout
    return _machine_layout.main()


if __name__ == '__main__':
    main()
    raise SystemExit(0)


for _p in (_hw / "scripts", _here.parent,
           _hw / "reference" / "compressor",
           _hw / "reference" / "condenser-block",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "valve-seat",
           _hw / "printed-parts" / "zone-c" / "funnel",
           _hw / "printed-parts" / "zone-c" / "funnel-cover",
           _hw / "reference" / "jg-pp0408w",
           _hw / "reference" / "neofit-stem-elbow",
           _hw / "printed-parts" / "diaphragm-pump-sleeve",
           _hw / "reference" / "waveshare-43b-display",
           _hw / "reference" / "meanwell-irm90",
           _hw / "reference" / "teyleten-relay",
           _hw / "printed-parts" / "electronics",
           _hw / "printed-parts" / "electronics" / "pcba-tray",
           _hw / "reference" / "asse1022-assembly",
           _hw / "reference" / "flare38-14ptc",
           _hw / "reference" / "mq6-gas-sensor",
           _hw / "reference" / "sf76e-thermal-fuse",
           _hw / "printed-parts" / "refrigeration" / "fuse-clamp",
           _hw / "reference" / "water-split",
           _hw / "reference" / "shok-blok-regulator",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "iec-c14-inlet",
           _hw / "reference" / "riteav-keystone",
           _hw / "reference" / "neofit-bulkhead",
           _hw / "reference" / "neofit-drain-bulkhead",
           _hw / "reference" / "gasher-check-valve",
           _hw / "reference" / "wr1110-regulator",
           _hw / "reference" / "digiten-flow-sensor",
           _hw / "cold-core-layout",
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "foam-assembly",
           _hw / "printed-parts" / "enclosure" / "bulkhead-ring",
           _hw / "printed-parts" / "faucet" / "tube-collar",
           _hw / "printed-parts" / "enclosure" / "nameplate",
           _hw / "printed-parts" / "enclosure" / "valve-tray",
           _hw / "printed-parts" / "enclosure" / "pump-tray",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "printed-parts" / "enclosure" / "display-cover",
           _hw / "printed-parts" / "enclosure" / "display-gasket",
           _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(_p))

import _enclosure_datums as cq
cq.install()

import collections
import math
from pathlib import Path
import fits
import _boxes
import above_core as _above
import _stated_bounds as _stated
import compressor as _comp
import enclosure as _enc
import _anchor_cap_interface as _anchor_cap
import funnel_frame as _funnel_frame
import manifold_layout as ml
import asse1022_assembly as _asse
import flare38_14ptc as _oad
import mq6_gas_sensor as _mq6
import foam_assembly as _foam
import _cold_core_interface as _cci
import riteav_keystone as _keystone
import jg_bulkhead_union as _jg
import bulkhead_ring as _ring
import nameplate as _np
import pump_tray as _tray
import dock_structure as _dock
import water_split as _split
import neofit_drain_bulkhead as _drain_bulkhead
import _drain
import neofit_bulkhead as _neofit
import wr1110_regulator as _wr1110
import _gas_chain
import digiten_flow_sensor as _digiten
import _scorecard as _card


_here = Path(__file__).resolve()


_hw = next(p for p in _here.parents if p.name == "hardware")


PSU_STEP = _hw / "reference" / "meanwell-irm90" / "meanwell-irm90.step"


PCBA_STEP = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-board.step"


RELAY_STEP = _hw / "reference" / "teyleten-relay" / "teyleten-relay.step"


WAGO_STEPS = {
    "413": _hw / "reference" / "wago-221" / "wago-221-413.step",
    "415": _hw / "reference" / "wago-221" / "wago-221-415.step",
    "420": _hw / "reference" / "wago-221" / "wago-221-420.step",
}


def wago_step(size):
    return WAGO_STEPS[size]


WAGO_POLES = ("wago-v12", "wago-gnd", "wago-g", "wago-h", "wago-n")


CLUSTER_WAGOS = {
    "wago-mana": (+1, 169.0, 280.0, "420"),
    "wago-manb": (+1, 169.0, 246.0, "415"),
    "wago-reeds-b": (-1, 335.0 - 2.0 * _enc.wago_pitch, 270.0, "413"),
    "wago-sensors": (-1, 335.0, 270.0, "413"),
}


FOAM_STEP = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"


FUNNEL_STEP = _hw / "printed-parts" / "zone-c" / "funnel" / "funnel.step"


FUNNEL_COVER_STEP = _hw / "printed-parts" / "zone-c" / "funnel-cover" / "funnel-cover.step"


FOAM_YAW = 90.0


COMPRESSOR_YAW = 90.0


FUNNEL_ROT = 0.0


def box(shape):
    # Through `_boxes` rather than straight at the shape. An optimal box costs
    # ~0.2 s on a pack solid and this is the layout's own way of asking for one:
    # the arrangement reads a body's faces every time it stands something against
    # them, and the same body is asked about nine times over a build.
    return _boxes.boxed(shape)


def _shift(b, *, cx=None, x0=None, x1=None, cy=None, y0=None, y1=None, z0=None, dz=None):
    return cq.Vector(
        (0.0 if cx is None else cx - (b.xmin + b.xmax) / 2.0)
        + (0.0 if x0 is None else x0 - b.xmin) + (0.0 if x1 is None else x1 - b.xmax),
        (0.0 if cy is None else cy - (b.ymin + b.ymax) / 2.0)
        + (0.0 if y0 is None else y0 - b.ymin) + (0.0 if y1 is None else y1 - b.ymax),
        (0.0 if z0 is None else z0 - b.zmin) + (dz or 0.0))


def _turned(v, axis, deg):
    """Rodrigues: the vector `v` turned `deg` about the unit `axis` through the origin — the same
    turn `Shape.rotate` gives the body, applied to a point or a direction on it."""
    a = cq.Vector(*axis).normalized()
    th = math.radians(deg)
    c, s_ = math.cos(th), math.sin(th)
    return (cq.Vector(*v) * c) + (a.cross(cq.Vector(*v)) * s_) + (a * (a.dot(cq.Vector(*v)) * (1.0 - c)))


Seat = collections.namedtuple("Seat", "turns rule got room members")


SEATS: dict = {}


_FACE = {"cx": lambda b: (b.xmin + b.xmax) / 2.0,
         "x0": lambda b: b.xmin, "x1": lambda b: b.xmax,
         "cy": lambda b: (b.ymin + b.ymax) / 2.0,
         "y0": lambda b: b.ymin, "y1": lambda b: b.ymax,
         "z0": lambda b: b.zmin}


def record_seat(name, *, turns=(), planes=None, station=None, got=None, members=()):
    """Enter one placement in the ledger, replacing any row of the same name.

    `got` is the placed geometry the rule is read back off: a bounding box for a plane rule, a
    world point for a station. A row is entered by the construction that owns the pose, so a
    body placed by something other than `seat_body` — the base pair, the manifold pack — is in
    the ledger on the same terms as one that is."""
    if station is None:
        rule = {k: v for k, v in (planes or {}).items() if v is not None}
        read = {k: _FACE[k](got) for k in rule if k in _FACE}
    else:
        rule, read = {"station": tuple(station)}, {"station": tuple(got)}
    SEATS[name] = Seat(tuple(turns), rule, read, [], tuple(members) or (name,))
    return SEATS[name]


def record_pump_dock_seats(box_spec, dock_parts):
    """World-authored dock parts at the bore face, and their returns' elbows."""
    plate = box_spec.pack.collet_plate
    fore = _dock.plumbing.tee_axis_y(plate['fore_y']) - _dock.tee.BRANCH_REACH
    for _station, tee_name, x, z in _dock.stations(plate):
        # Each tee stands with its extended branch collet in its recess ahead of the bore face,
        # its run upright on the pump tube's axis.
        name = 'tee-' + tee_name.lower()
        record_seat(name, planes={'y0': fore, 'cx': x, 'z0': z - _dock.plumbing.RUN_FACE},
                    got=box(dock_parts[name]))
        # Its return's two elbows: each stem bottomed in its collet, both sockets level.
        target = plate['return_ports'][str(x)]
        lower = _dock.plumbing.tee_ports(plate['fore_y'], x, z)['lower']['point']
        line = _dock.plumbing.elbow_return(lower, tuple(target['point']))
        for host, port_z, row, inserted in (
                (tee_name, lower[2], line['elbows'][0], _dock.plumbing.RUN_INSERTION),
                (target['valve'], target['point'][2], line['elbows'][1],
                 _dock.plumbing.VALVE_INSERTION_NOMINAL)):
            name = 'stem-elbow-' + host.lower()
            record_seat(name, planes={'z0': line['floor_z'], 'z1': port_z + inserted},
                        got=box(dock_parts[name]))


def note_room(name, what, want, got):
    """Record where a derived pose fell against a band its construction states.

    `want` is the clearance the construction asked for and `got` is what the placed geometry
    actually leaves, measured the same way the strike measured it. `None` for `got` is a pose
    with nothing to fall short of — a body the band does not bound."""
    if name in SEATS:
        SEATS[name].room.append((what, want, got))


BASE_YAW = -90.0


COMPRESSOR_FRONT = 11.0


PACK_CROWN = 151.0


def east_lane_free(cond) -> float:
    """How far the block may go east off the plane the mating puts it on, read off the placed
    body and the wall it is going toward.

    THE SEAM'S FURNITURE IS NOT THE FENCE HERE, and saying so is the whole of this. The front
    column's seam furniture on a flank is the hooked rail, and the rail lives in the seam's
    own storey — `z_seam` up to the rim — while this block's crown comes up UNDER that mouth.
    A body under the storey is beside nothing, and charging it the rail's whole reach would be
    charging it for a lane it never enters.

    WHAT IS THERE IS ITS OWN AFT MOUNT. The block hangs off a fin fused to the wall's inner face
    (`condenser_mount`, `enclosure._cond_mount`), standing one `enclosure.cond_mount_clear` off
    the block's east flank — so the lane the block may take is the lane that leaves the fin one
    printable `enclosure.wall` of section. The block answers to the thing that holds it.

    AND THAT FIN IS THE WALL. The block stands wholly under the front Z seam, and a flank under a
    seam carries its lip's own wall down to the slab (`enclosure._lip_underwall`) — `2 * wall` of
    it. So the section the fin needs is section the wall already has: what the lane leaves is one
    `enclosure.cond_mount_clear` of air off `front_bottom_flank_face`, and the fingers root on
    the flank itself. The two readings come to the same plane, so the block RIDES the thickening
    — it stands off whatever section that flank carries, into the lane it has always had between
    its own west flank and the compressor's tangent. What crosses the lane behind it is
    `_lines._refrig_2`, which leaves and enters on its ports\' own normals and turns between
    them."""
    b = box(cond)
    storey_z = _enc.z_seam
    # The block's own front face is what goes in: the fore end of the run comes back struck on
    # it and is not read, this block being cradled on the front wall already. What is read is
    # the aft end, which the box states about itself.
    band_aft = _enc.front_band_free_y(b.ymin)[1]
    if b.zmax > storey_z + 1e-9 or b.ymax > band_aft + 1e-9:
        raise ValueError(
            f"the condenser reaches y {b.ymax:g} and z {b.zmax:g}, out of the corner of the ±X "
            f"band the front column leaves empty — under z {storey_z:g}, forward of y "
            f"{band_aft:g}. A block that stands up into the slide's storey answers to the "
            f"rail's whole reach and not to its own fin, so it stands off "
            f"`enclosure.side_band_inset` instead.")
    return (_enc.front_bottom_flank_face()[1] - _enc.cond_mount_clear) - b.xmax


FUSE_TURN = (((1.0, 0.0, 0.0), 90.0), ((0.0, 0.0, 1.0), 90.0))


FUSE_FACE_NORMAL = (1.0, 0.0, 0.0)


def power_face_station(comp_carry):
    """The centre of the compressor's power face in the machine, for a body laid flat on it.

    Both bodies that go there — the cutoff and the clamp that holds it — are drawn in ONE frame
    with Z = 0 on that face, and `FUSE_TURN` is the pair of quarters that lays that plane on it.
    So both read this one station, and a yaw that swung the face off +X is caught once here
    rather than seating one of them on a wall and the other in the open."""
    (pos, normal) = comp_carry(_comp.power_face())
    got = tuple(round(v, 9) for v in normal)
    if got != FUSE_FACE_NORMAL:
        raise ValueError(
            f"the compressor's power face looks {got} in the machine and the cutoff's quarters "
            f"lay its contact line on {FUSE_FACE_NORMAL} — the base has been turned out "
            f"from under this pose, and the case is now bedded in the cover rather than on it.")
    return pos


CORE = "cold-core"


def cap_face(foam):
    """The Z THE CORE PRESENTS TO THE MACHINE — its top lid's outer face, which is the plane
    every body standing on the core is placed off.

    NOT the box's own top, and the difference is the whole of this function: the cap prints a
    valve cradle at each station in `_cold_core_interface.cap_cradles`, those pads stand off
    that face, and so the solid's `zmax` is a valve seat. A body seated on it would be standing
    on one. `foam_assembly` states how far the face stands over the floor the stack is set down
    on, and this reads it there."""
    return box(foam).zmin + _foam.cap_face_over_floor


MQ6_Y0 = 38.3


def mq6_cradle(carry):
    """The strip's card-slot station, `(x, y, z)` — the card's own mid-plane, and its centre
    along the strip and in height. Nothing else, because nothing else varies: the slot is one
    board's envelope and one slip fit, and both the cradle and the flank's well read those off
    the reference module itself.

    STRUCK ON `mq6_gas_sensor.card_plane` and not on the placed box, because the box is the pins
    and the can as well, and the two are not the same depth — its centre stands west of the card
    they hang off. The slot cannot land anywhere but on the card."""
    pos = carry(_mq6.card_plane())[0]
    return ((pos[0], pos[1], pos[2]),)


Bound = collections.namedtuple("Bound", "id label ok value target detail kind",
                               defaults=("gate",))


BOUNDS: list = []


def record_bound(bound: Bound) -> Bound:
    """Enter one bound's reading in the ledger, replacing any of the same id."""
    BOUNDS[:] = [b for b in BOUNDS if b.id != bound.id] + [bound]
    return bound


def carry_enclosure_bounds() -> None:
    """The bounds `enclosure` states about the box it draws, entered in this ledger — its
    stated width and height against what the pack demands, the two seam planes against
    the print bed and the display housing, and the funnel throat against the frame the top wall
    has left. Same record, same rendering, and the same reason for not raising.

    `enclosure` keeps its own list rather than importing this one, because this module is what
    places the pack it sizes the box on and the import only runs one way."""
    for b in _enc.BOUNDS:
        record_bound(Bound(*b))


def carry_stated_bounds() -> None:
    """The bounds the pack's own modules state about their constants, entered in this ledger.

    They were read when those modules were imported — the manifold's two source runs against
    the two arcs they step on, the fuse clamp against the compressor it closes on, and the cold
    core's screws, conduit columns, cradles and anchors against each other. A raise there would
    take the STEP, the three elevations and this card with it before `build_enclosure_assembly`
    ran a line, which is why they do not raise; this is where they arrive instead.

    `_stated_bounds` keeps the list rather than this module keeping it, because the modules
    that record into it are the ones this module imports and the import only runs one way."""
    for b in _stated.records():
        record_bound(Bound(*b))


CRADLE_TOL = 0.001


def _core_frame(foam_carry):
    """The cold core's own frame in world — `(origin, +X, +Y)` — read off the placement the
    core actually took rather than restated from the yaw that produced it."""
    o = cq.Vector(*foam_carry(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))[0])
    ex = cq.Vector(*foam_carry(((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)))[0]) - o
    ey = cq.Vector(*foam_carry(((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)))[0]) - o
    return o, ex, ey


def cap_xy(foam_carry, world_xy) -> tuple:
    """A world `(x, y)` in the CAP'S OWN frame — the frame `_cold_core_interface` authors in.

    Two hops: the core's placement carries the assembly's frame, and the cap installs spun a
    half turn inside it (`foam_assembly.spin_xy`), which is its own inverse."""
    o, ex, ey = _core_frame(foam_carry)
    d = cq.Vector(world_xy[0] - o.x, world_xy[1] - o.y, 0.0)
    return _foam.spin_xy((d.dot(ex), d.dot(ey)))


def cradle_rows(foam, foam_carry, placed: dict) -> list:
    """Each cradle as `(name, has, wants)` — the row the cap carries and the row the placed
    valve asks for, both `(x, y, yaw, seat)` in the cap's own frame.

    The Beduan's symmetric cap and port extremes keep its horizontal bounding envelope centred
    on the mounting datum, although its terminals and collet ears are asymmetric. The box
    centre is therefore the seat centre, its long horizontal span is the port axis, and its
    `zmin` is the four-foot mounting plane the cradle puts under it."""
    o, ex, ey = _core_frame(foam_carry)
    face = cap_face(foam)
    rows = []
    for name, station in _cci.cap_cradles.items():
        b = box(placed[name])
        # The valve's own spans along the cap's two axes. Both frames are axis-aligned in
        # world, so a span reads off the box directly.
        along = tuple(abs(v.x) * b.xlen + abs(v.y) * b.ylen for v in (ex, ey))
        yaw = 0.0 if along[0] >= along[1] else 90.0
        x, y = cap_xy(foam_carry, ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0))
        rows.append((name, station, (x, y, yaw, b.zmin - face), max(along), min(along)))
    return rows


CRADLE_TOL = 0.01


def cradles_land(rows) -> list:
    """The cradles whose printed station is not where the placed valve asks for one.

    `cradle_rows` reads both sides and nothing else did; without this the cap would go on
    printing a plinth at the old station while the valve stood beside it, and no gate on
    this card would say so — the sockets are a press fit, and a valve off one of them is
    off all four."""
    out = []
    for name, station, wants, _long, _short in rows:
        has = (station.centre[0], station.centre[1], station.yaw, station.seat)
        if any(abs(h - w) > CRADLE_TOL for h, w in zip(has, wants)):
            out.append((name, has, wants))
    return out


TRAY_SEAT_SLIP = 0.2


def _valve_up(placed: dict, name: str) -> tuple:
    """One valve's own +Z in world, as `(axis, sign)` — the way its coil stands off it."""
    coil = name.replace("valve-", "coil-")
    if coil not in placed:
        raise KeyError(
            f"{name} is placed and {coil} is not, so nothing says which way it faces — a "
            f"Beduan's coil stands on its crown and that is what tells a tray which of the "
            f"body's six faces its four posts stand on.")
    vb, cb = box(placed[name]), box(placed[coil])
    d = [(cb.xmin + cb.xmax - vb.xmin - vb.xmax) / 2.0,
         (cb.ymin + cb.ymax - vb.ymin - vb.ymax) / 2.0,
         (cb.zmin + cb.zmax - vb.zmin - vb.zmax) / 2.0]
    axis = max(range(3), key=lambda i: abs(d[i]))
    return axis, (1.0 if d[axis] > 0.0 else -1.0)


def _bodies(placed: dict) -> dict:
    """`placed` reaches these readers in either of the two shapes the tree hands round —
    `{name: solid}` from the stand, and the pack's own `{name: (solid, colour)}`. Both mean
    the same bodies, so take the solid either way rather than making every caller remember
    which one it is holding."""
    return {n: (b[0] if isinstance(b, tuple) else b) for n, b in placed.items()}


def _tray_valve(name):
    return (name.startswith('valve-v-') and name not in _above.valve_names()
            and name not in _cci.cap_cradles and name not in _above.core_equipment_names())


def valve_tray_decks_from_bounds(bounds: dict) -> dict:
    """The tray arithmetic from explicit ``name -> (lower, upper)`` readings."""
    groups = collections.defaultdict(list)
    for name in bounds:
        if not _tray_valve(name):
            continue
        coil = name.replace('valve-', 'coil-')
        if coil not in bounds:
            raise KeyError(
                f"{name} is placed and {coil} is not, so nothing says which way it faces — a "
                f"Beduan's coil stands on its crown and that is what tells a tray which of the "
                f"body's six faces its four posts stand on.")
        lower, upper = bounds[name]
        coil_lower, coil_upper = bounds[coil]
        delta = [(coil_lower[i] + coil_upper[i] - lower[i] - upper[i]) / 2.0
                 for i in range(3)]
        axis = max(range(3), key=lambda i: abs(delta[i]))
        sign = 1.0 if delta[axis] > 0.0 else -1.0
        centre = tuple((lower[i] + upper[i]) / 2.0 for i in range(3))
        plane = (lower if sign > 0 else upper)[axis]
        groups[(axis, sign, round(plane, 6))].append((name, centre))
    out = {}
    for (axis, sign, plane), members in sorted(groups.items()):
        across = 0 if axis != 0 else 1
        along = next(i for i in range(3) if i not in (axis, across))
        seats = tuple((n, c[across], c[along]) for n, c in sorted(members))
        out[tray_name(axis, sign, plane, out)] = (axis, sign, plane, seats)
    return out


def valve_tray_decks(placed: dict) -> dict:
    """The valves a tray holds, grouped by the plane they stand on.

    `name -> (axis, sign, plane, ((valve, u, v), …))` — which world axis the valves' own +Z
    runs on, which way it points, the world coordinate of their shared mounting plane, and each
    valve's centre in the plate's two in-plane axes.

    The selected above-core valves are excluded: their integral back-top or
    lid seats follow the native placement, and each body has one holder."""
    placed = _bodies(placed)
    requested = {name for name in placed if _tray_valve(name)}
    requested |= {name.replace('valve-', 'coil-') for name in requested}
    bounds = {}
    for name, shape in placed.items():
        if name in requested:
            b = box(shape)
            bounds[name] = ((b.xmin, b.ymin, b.zmin), (b.xmax, b.ymax, b.zmax))
    return valve_tray_decks_from_bounds(bounds)


def tray_name(axis: int, sign: float, plane: float, taken: dict) -> str:
    """The body name one tray goes into the assembly under — where in the machine the plate
    itself stands, which is opposite the way its valves' coils point."""
    where = {(0, 1.0): "west", (0, -1.0): "east", (1, 1.0): "fore", (1, -1.0): "aft",
             (2, 1.0): "bottom", (2, -1.0): "top"}[(axis, sign)]
    name = f"valve-tray-{where}"
    return name if name not in taken else f"{name}-{plane:.0f}"


def valve_tray_stations(placed: dict) -> tuple:
    """Every deck as `enclosure.Pack.valve_trays` — `(plane, sign, ((x, z), …))` per tray.

    The world Y a deck's valves stand their mounting faces on, which way their own +Z runs off
    it, and each valve's footprint centre. This is the whole of what the wall is handed: the
    plate's extent is the seats' own, and its thickness, margin and seat height are
    `valve_tray`'s.

    Each fixed valve seats its whole post in its socket and lands its body on
    the tray face. The permanent junctions and supported purchased elbows connect
    to those seated ports through straight upper links and bent lower tubes and short
    elbow-to-valve links."""
    return _valve_tray_stations(valve_tray_decks(placed))


def valve_tray_stations_from_bounds(bounds) -> tuple:
    """The existing tray station rows from explicit lower/upper readings."""
    return _valve_tray_stations(valve_tray_decks_from_bounds(bounds))


def _valve_tray_stations(decks):
    out = []
    for _name, (axis, sign, plane, seats) in sorted(decks.items()):
        if axis != 1:
            raise ValueError(
                f"a valve deck stands its valves' own +Z on {'xyz'[axis]} and "
                f"`enclosure._valve_trays` fuses a plate across the box's width on a Y plane — "
                f"a deck on another axis needs the builder to learn it, not this table.")
        out.append((plane, sign,
                    tuple((round(u, 6), round(v, 6)) for _n, u, v in seats)))
    return tuple(out)


PUMP_TRAY_SLIP = 0.2


def _pump_up(placed: dict, head: str) -> tuple:
    """One pump's own depth axis in world, as `(axis, sign)` — the way its motor can stands off
    its head."""
    can = head.replace("-head", "-motor")
    if can not in placed:
        raise KeyError(
            f"{head} is placed and {can} is not, so nothing says which way it faces — a Kamoer's "
            f"can stands on the boss behind its head, and that is what tells a tray which of the "
            f"head's six faces it lies on.")
    hb, cb = box(placed[head]), box(placed[can])
    d = [(cb.xmin + cb.xmax - hb.xmin - hb.xmax) / 2.0,
         (cb.ymin + cb.ymax - hb.ymin - hb.ymax) / 2.0,
         (cb.zmin + cb.zmax - hb.zmin - hb.zmax) / 2.0]
    axis = max(range(3), key=lambda i: abs(d[i]))
    return axis, (1.0 if d[axis] > 0.0 else -1.0)


def pump_tray_seats(placed: dict) -> dict:
    """The pump stations the cartridge uses, `head -> (axis, sign, centre)`.

    `centre` is the world point the head datum meets its bracket plane. The motor can supplies
    the two transverse coordinates because it is cylindrical, after removing the reference
    pump's stated rear-stack offset; the head supplies the depth face. The head is not assumed
    symmetric about its datum: its measured skirt and outlet-side relief may give it an
    asymmetric bounding box."""
    bounds = {}
    for name, shape in placed.items():
        if name.startswith('pump-') and name.endswith(('-head', '-motor')):
            b = box(shape)
            bounds[name] = ((b.xmin, b.ymin, b.zmin), (b.xmax, b.ymax, b.zmax))
    return pump_tray_seats_from_bounds(bounds)


def pump_tray_seats_from_bounds(bounds) -> dict:
    """The same head/can station arithmetic from explicit lower/upper readings."""
    out = {}
    for head in sorted(bounds):
        if not (head.startswith("pump-") and head.endswith("-head")):
            continue
        can = head.replace("-head", "-motor")
        if can not in bounds:
            raise KeyError(f'{head} is placed and {can} is not')
        lower, upper = bounds[head]
        can_lower, can_upper = bounds[can]
        d = [(can_lower[i] + can_upper[i] - lower[i] - upper[i]) / 2.0
             for i in range(3)]
        axis = max(range(3), key=lambda i: abs(d[i]))
        sign = 1.0 if d[axis] > 0.0 else -1.0
        centre = [(can_lower[i] + can_upper[i]) / 2.0 for i in range(3)]
        centre[axis] = (upper if sign > 0 else lower)[axis]
        # In this machine pose the pump reference's local Y is world Y. Its rear boss/can axis
        # is one millimetre toward Y-, but the cartridge station belongs to the unchanged head
        # and lower cradle. The removable cap applies the same reference offset to its rear-stack
        # openings; keeping it out of this station prevents that correction moving the cradle.
        if (axis, sign) == (2, 1.0):
            centre[1] -= _tray.rear_axis_y_shift
            # The pump body seats below the nominal flange plane. Restore that
            # offset only for the holder datum, preserving the fitted skirt lands.
            centre[2] += _enc._interface.pump_seated_drop
        out[head] = (axis, sign, tuple(round(c, 6) for c in centre))
    return out


def pump_tray_stations(placed: dict) -> tuple:
    """Every pump as legacy `enclosure.Pack.pump_trays` — one world `centre` each.

    This is the whole of what the cartridge builder is handed; its cradle, clamp and clearances
    are enclosure and `pump_tray` figures."""
    out = []
    for head, (axis, sign, centre) in sorted(pump_tray_seats(placed).items()):
        if (axis, sign) != (2, 1.0):
            raise ValueError(
                f"{head} stands its can on {'+' if sign > 0 else '-'}{'xyz'[axis]} and "
                f"`enclosure.build_pump_cartridge` lays a plate on a Z face — a pump on another "
                f"axis "
                f"needs the builder to learn it, not this table.")
        out.append(centre)
    return tuple(out)


def collet_plate_spec(mcarry, tray_stations, valve_trays=()) -> dict:
    """The bay bulkhead, its collet plate and the four tee stations behind it."""
    holes, upper_ports, return_ports = [], {}, {}
    for name in sorted(ml.BARB_OF):
        (px, _py, pz), _axis = mcarry((ml.barb_station(name), (0., 0., 1.)))
        x = round(px, 6)
        holes.append((x, round(pz, 6)))
        upper_valve, return_valve = ml.PUMP_VALVES[name]
        for ports, valve, end in ((upper_ports, upper_valve, 'front'),
                                  (return_ports, return_valve, 'back')):
            point, axis = mcarry((ml.port(valve, end), ml.port_axis(valve, end)))
            ports[str(x)] = {'point': tuple(point), 'axis': tuple(axis), 'valve': valve}
    holes = sorted(holes)
    fore = round(ml.pump_wall_fore_y(), 6)
    plumbing = _dock.plumbing
    return {"holes": tuple(holes), "fore_y": fore,
            "aft_y": round(plumbing.plate_aft_y(fore), 6),
            "wall_aft_y": round(_dock.wall_aft_y(fore), 6),
            "x0": _enc.interior_x()[0], "x1": _enc.interior_x()[1],
            "z0": _enc.z_seam, "z1": 218.85,
            "hole_d": 2.0 * _dock.HOLE_R,
            "seat_z": round(_enc.bay_floor_z(tray_stations)[1],6),
            "upper_ports": upper_ports, "return_ports": return_ports,
            "valve_trays": tuple(valve_trays),
            "fixture_print_bed_z": _enc.z_seam + _enc.slide_slip,
            "tee_axis_y": round(plumbing.tee_axis_y(fore), 6),
            "seated_tube_bottom_y": round(plumbing.tip_y(fore), 6),
            "pump_tube_cut": round(ml.PUMP_TUBE_CUT, 6),
            "tube_bottom_y": round(plumbing.tip_y(fore), 6),
            "assembly_state": "seated"}


COND_PROBE_INSET = 0.5


COND_AIR_INSET = 0.05


_COND_UNPRINTED = "NOT PRINTED — no piece owns this station"


_CORE_HOLD_EAST_EDGE = _above.specification()['rear_wall']['interior_panel_relief']['xmin']


CORE_HOLD_LANES = ((-43.6, -37.5), (_CORE_HOLD_EAST_EDGE-9., _CORE_HOLD_EAST_EDGE))


def vent_chase(foam, foam_carry) -> tuple:
    """Where the cold core's PRV relief line arrives at the west wall, as
    `enclosure.Pack.vent_chase` — one `(x, y, z)` in the machine's own frame.

    The X is the west face of the core's foil envelope, `casing_foil_allowance` off its flank,
    which is the plane the chase's lip lands on and the plane the tube is cut off at; the Y and
    Z are that tube's own axis where it comes through.

    THE CORE STATES BOTH, NOT THE BOX. `_internal_routes` draws the line out through the shell's
    +Y flank, and the placed body carries the flank the line leaves by. So they come from the
    core's own placement, the same way a cap conduit does: move the core, re-yaw it, or move the
    station the shroud's bore lands on, and the chase follows without a number being retyped.

    Reached THROUGH `foam_assembly` rather than imported. `_internal_routes` puts the cold
    core's own directories on `sys.path` when it loads, and a module that does that at this
    one's import time changes what every later import in this process resolves to — the same
    hazard a walk taken in a cold process runs into. `_foam` already holds it."""
    tip = _foam.routes.routes["prv-vent"][-1]
    at, _axis = foam_carry((tip, (0.0, 1.0, 0.0)))
    return ((box(foam).xmin - _cci.casing_foil_allowance, at[1], at[2]),)


def core_holds(foam) -> tuple:
    """The core's aft crown as `enclosure.Pack.core_holds` — `(x0, x1, aft, crown)` each.

    The two lanes are `CORE_HOLD_LANES`; `aft` is the aft face of the core's foil envelope,
    which is the plane `rear_seam_clear` is measured to, and `crown` is `cap_face` —
    the lid's outer face beneath its equipment mounts."""
    b, crown = box(foam), cap_face(foam)
    return tuple((x0, x1, b.ymax + _cci.casing_foil_allowance, crown) for x0, x1 in CORE_HOLD_LANES)


FRONT_RIDERS = ("valve-v-", "coil-v-", "tee-y-", "stem-elbow-", "turn-", "step-",
                "reservoir-a-fill-turn", "reservoir-a-draw-turn", "reservoir-b-fill-turn")


CORE_RIDERS = ("g-ganen-pump", "valve-v-a", "valve-v-b", "vk-solenoid",
               "coil-v-a", "coil-v-b", "stub-fluid-2", "stub-fluid-4",
               "discharge-chain", "pump-elbow-suction", "pump-elbow-discharge")


CORE_RIDE_LATER = ("foam-assembly", "funnel", "nameplate")


CORE_RIDE_RUNS = ("tube-", "turn-", "step-")


BEDDED_TOL = 0.01


JOINT_STATIONS = {
    "refrig-1": ("compressor.refrig-discharge", "condenser+fan.refrig-inlet"),
    "refrig-2": ("condenser+fan.refrig-outlet", "foam-assembly.evap-inlet"),
    "refrig-3": ("foam-assembly.evap-outlet", "compressor.refrig-suction"),
}


REFRIGERANT_IDS = tuple(cid for cid, _f, _t in _card.REFRIGERANT_SEGMENTS)


MADE_BY_MATE, MADE_BY_TUBE = "mate", "drawn"


JOINT_TOL = 0.05


def refrigerant_mates(joints) -> list:
    """The legs a shared plane CLOSED, as `(id, from, to, mm apart)` — what
    `_scorecard.load_connections` may count as made without a line drawn for it.

    A leg the machine draws is not here and does not belong here: `routed` counts that one off
    the run itself, and counting it twice would let a tube stand in for the mating it is drawn
    instead of. A mating standing open is copper the machine owes, so it belongs with the
    connections still to route and not with the ones already made."""
    return [(j.id, j.frm, j.to, j.mm) for j in joints
            if j.made == MADE_BY_MATE and j.mm is not None and j.mm <= JOINT_TOL]


MOUNT_TOL = 0.001


def pump_mount_rows(foam_carry, water_pump_carry) -> list:
    """The bare pump uses its lid-integrated half pipe and removable snap cap."""
    return []


def cap_anchor(name: str):
    """One of the cold core's chain anchors as a station in the CORE'S OWN frame:
    `((x, y, z), the way the body comes into it)`.

    `foam_assembly` authors the rib in the cap's frame and turns it back through the cap's own
    half-turn install, so its `(x, y)` is already the assembly's; the Z is the seat's own axis,
    which stands `_cold_core_interface.cap_anchor_axis_over_face` over the lid's outer face. The
    seat opens on the cap's +Z, which is the way the body is laid into it."""
    x, y = _foam.cap_anchor_station(name)
    return ((x, y, _foam.cap_face_z + _cci.cap_anchor_axis_over_face(name)),
            _foam.cap_conduit_axis_out())


def cap_side_anchor(name: str):
    """One of the cold core's SIDEWAYS anchors as a station in the CORE'S OWN frame:
    `((x, y, z), the way the run comes into it)`.

    The pipe opens on the core's own −Y, so a run beds into it from the room rather than being
    laid down into it. Its Z stands `_cold_core_interface.cap_side_anchor_height`'s own axis term
    over the lid's outer face, and its Y is the pipe's axis — `axis_off` forward of the post's
    face, which `foam_assembly.cap_side_anchor_station` already carries."""
    x, y = _foam.cap_side_anchor_station(name)
    return ((x, y, _foam.cap_face_z + _cci.cap_side_anchors[name].over_face),
            (0.0, -1.0, 0.0))


def cap_conduit(name: str):
    """One of the cold core's cap conduits as a station in the CORE'S OWN frame:
    `((x, y, z), outward axis)`.

    The core owns the actual lid-guide or fitting mouth, including its height
    and direction. The appliance carries that native station into world space."""
    return _foam.cap_conduit_mouth(name)


def water_pump_west_limit() -> float:
    """Retained pump mounting datum in the rear service bay."""
    return -50.2


def water_pump_port_lane_limit() -> float:
    """The westmost the pump's casting may reach on the FLAVOUR UNIONS' OWN STOREY.

    THE CASTING IS THE EAST FLANK OF THE PORT LANE. The two flavour unions cross the +Y wall of back-top
    between the rear seam's boss chain and this casting, `PORT_WEST_COLUMN` stands the pair off
    that chain by one `PORT_LANE_CLEAR`, and this is the same millimetre owed on the other side.
    Read off the east column and the union's own body — the station the field actually stands
    on."""
    return PANEL_X["bulkhead-flavor-a"] + _jg.BODY_D / 2.0 + PORT_LANE_CLEAR


DISCHARGE_ELBOW_DIP = 25.0


PUMP_ELBOWS = {
    "suction": ("pump-elbow-suction", (0.0, -1.0, 0.0)),
    "discharge": ("pump-elbow-discharge",
                  (0.0, -math.cos(math.radians(DISCHARGE_ELBOW_DIP)),
                   -math.sin(math.radians(DISCHARGE_ELBOW_DIP)))),
}


CHAIN_SEAT_SLIP = fits.slip


PORT_HOLE_SLIP = 2.0 * fits.slip


def bulkhead_seat_y():
    """The plane the union's flange bears on — the +Y wall of back-top's OWN OUTER FACE, and the face of the
    ring lying flush in it.

    The pocket is cut one `bulkhead_ring.THICK` INTO that face and the ring fills it, so wall stock and
    colour come out one plane and a flange landing here lands on both at once."""
    return _enc.rear_plane_y + _enc.wall


def bulkhead_mouth_y():
    """The Y of its INBOARD collet face — the plane the ASSE chain's own inlet collet butts on.
    Read off the fitting's own seating planes, so a longer union moves the chain it feeds rather
    than closing on it."""
    return bulkhead_seat_y() + _jg.far_ring_face_y


def y_wall_ports(bulkhead_carry, panel_carries):
    """Through-holes the +Y wall of back-top carries, as `(kind, x, z, *size)` on its own plane.

    One per union: the bore its threading passes. Each is struck on the fitting's own inboard
    collet, so hole and barrel cannot land on two different columns, and it is bored one
    `PORT_HOLE_SLIP` over the barrel that goes through it."""
    carries = {"bulkhead-water": bulkhead_carry, **panel_carries}
    return [("round", carry(Y_WALL_FITTINGS[name][0].port(-1.0))[0][0],
             carry(Y_WALL_FITTINGS[name][0].port(-1.0))[0][2],
             Y_WALL_FITTINGS[name][0].panel_hole_d(PORT_HOLE_SLIP))
            for name, carry in carries.items()]


Y_WALL_FITTINGS = {
    "bulkhead-water": (_jg, "union", "water", "water"),
    "bulkhead-carb": (_jg, "union", "carb", "carb"),
    "bulkhead-flavor-a": (_drain_bulkhead, "drain", "flavor-a", "flavor"),
    "bulkhead-flavor-b": (_drain_bulkhead, "drain", "flavor-b", "flavor"),
    "co2-inlet": (_neofit, "neofit", "co2", "co2"),
    "bulkhead-drain": (_drain_bulkhead, "drain", "drain", "drain"),
}


def ring_name(which: str) -> str:
    """The body name one chip goes into the assembly under."""
    return f"bulkhead-ring-{which}"


def word_name(which: str) -> str:
    """The body name that chip's lettering goes in under — a second solid in a second colour,
    lying in the recess the chip carries for it."""
    return f"bulkhead-ring-{which}-word"


BULKHEAD_RING_SLIP = fits.slip


BULKHEAD_RING_RIM = 3.0


PORT_BOSS_PROUD = _ring.THICK


def port_clamp_stack(t: float) -> float:
    """The barrel length from the flush ring face to the inboard nut land.

    A full-section station clamps its whole `t`, which already holds the ring, its static
    back gap and the wall under them. A relieved station's land stands one `wall` behind
    the ring and its gap, so it clamps `wall + PORT_BOSS_PROUD + fits.slip`.
    """
    return max(t, _enc.wall + PORT_BOSS_PROUD + fits.slip)


def port_pocket_d(ring: str = "union") -> float:
    """What one station's pocket measures ACROSS — the chip's own width and the slip it takes in
    it. The wall cuts it and `PORT_FIELD_PITCH` spaces the columns by it, off this one call."""
    return _ring.od(ring) + 2.0 * BULKHEAD_RING_SLIP


def port_pocket_rise(which=None) -> float:
    """How far a pocket stands ABOVE the bore's axis — the chip's own rise and its slip. The top
    row runs out past the box's top face and is cut off by it, which is what leaves those three
    chips open at the top."""
    return (_ring.RISE if which is None else _ring.rise(which)) + BULKHEAD_RING_SLIP


def wall_stations(bulkhead_carry, panel_carries, co2_carry, drain_carry) -> dict:
    """Every `Y_WALL_FITTINGS` station on the wall, as
    `name -> (x, z, fitting, ring, ring name, fluid)`.

    Each column is read off the FITTING'S OWN INBOARD COLLET, which is what `y_wall_ports` and
    `co2_wall_port` bore from — so a pad, a ring and the hole through both cannot land on two
    different columns."""
    carries = {"bulkhead-water": bulkhead_carry, **panel_carries, "co2-inlet": co2_carry, "bulkhead-drain": drain_carry}
    out = {}
    for name, (fitting, ring, which, fluid) in Y_WALL_FITTINGS.items():
        x, _y, z = carries[name](fitting.port(-1.0))[0]
        out[name] = (x, z, fitting, ring, which, fluid)
    return out


def y_wall_field(stations):
    """The pocket each chip lies in, as `enclosure.Pack.port_field` — one per station, not one field
    across them. `enclosure._port_field` cuts each into the wall's outer face; a station relieved
    for its nut keeps the land under it as retained wall stock, and `BULKHEAD_RING_RIM` is the
    wall the field keeps round every chip."""
    return _enc.PortField(PORT_BOSS_PROUD, BULKHEAD_RING_RIM,
                          tuple((x, z, port_pocket_d(ring), port_pocket_rise(which),
                                 _ring.bottom(ring) + BULKHEAD_RING_SLIP)
                                for x, z, _fitting, ring, which, _fluid in stations.values()))


CUSTOMER_TUBE_STATIONS = ("bulkhead-water", "co2-inlet")


COLLAR_OFF_COLLET = 8.0


COLLAR_TUBE_TAIL = 10.0


def customer_tube_name(which: str) -> str:
    """The body name one customer-side tube goes into the assembly under.

    IT CARRIES THE TUBE PREFIX BECAUSE IT IS TUBE. `_scorecard._split_placed` reads the placed
    world into its three populations off these names, and what it asks of a body it does not ask
    of a length of tube: a tube is fastened by the collet it seats in, so it owes no row in the
    fastening table, it stands at 0.00 against the fitting it is pushed into by construction, and
    it is not an obstruction in front of the port it leaves. Named outside the prefix it enrols
    as a body and is charged all three."""
    return f"tube-customer-{which}"


def collar_name(which: str) -> str:
    """The body name one collar goes into the assembly under."""
    return f"tube-collar-{which}"


def collar_word_name(which: str) -> str:
    """The body name that collar's lettering goes in under — a second solid in a second colour,
    lying in the flats the collar carries for it."""
    return f"{collar_name(which)}-word"


NAMEPLATE_MARGIN = 5.0


NAMEPLATE = "nameplate"


NAMEPLATE_INK = "nameplate-ink"


NAMEPLATE_PSU_CLEAR = 1.0


NAMEPLATE_CAP_CLEAR = 1.0


def nameplate_cut(station) -> _enc.Nameplate:
    """The production snap-fit pocket at the plate's station."""
    return _np.interface.station(*station)._replace(thick=_np.THICK)


DECK_CLEAR = 6.0


DECK_FALL_LIMIT = 60.0


PORT_NUT_GAP = 7.0


PORT_DECK_EXTRA = 7.5


PORT_HARDWARE_PITCH = _jg.panel_footprint()[0] + PORT_NUT_GAP + PORT_DECK_EXTRA


PORT_FIELD_PITCH = port_pocket_d() + BULKHEAD_RING_RIM


PORT_PITCH = max(PORT_HARDWARE_PITCH, PORT_FIELD_PITCH)


_stated.state(
    "port-pocket-floor", "Every pocket leaves wall under the chip it holds",
    f"a chip under `enclosure.wall` {_enc.wall:g} mm",
    _ring.THICK < _enc.wall - 1e-9,
    f"the pocket is cut {_ring.THICK:g} mm into a wall {_enc.wall:g} mm thick and leaves "
    f"{_enc.wall - _ring.THICK:.2f} mm of floor under the chip.")


_port_stack = _stated.bound(
    "port-clamp-stack", "Every fitting's bare barrel takes the wall and the ring lying in it",
    f"a stack of the wall at its own station, floored on `enclosure.wall` and "
    f"{PORT_BOSS_PROUD:g} mm of boss")


for _n, (_fit, _r, _w, _f) in Y_WALL_FITTINGS.items():
    _bare = getattr(_fit, "PANEL_THREAD", None) or _fit.THREAD_LEN
    _port = next(row for row in _above.specification()['rear_wall']['wet_ports']
                 if row['name'] == _n)
    _t = _enc.back_wall_t_at(_port['center_x_mm'], _port['center_z_mm'])
    _stack = port_clamp_stack(_t)
    _port_stack(_stack <= _bare + 1e-9,
                f"{_n} offers {_bare:.2f} mm of bare barrel and the joint it makes up through "
                f"{_t:g} mm of wall stacks {_stack:g} mm, leaving the nut none of it")


def west_interior_face():
    """The −X wall's own inner face, off the stated width — the same face `enclosure._dims`
    builds the box on."""
    return _enc.interior_x()[0]


def west_exterior_face():
    """And that wall's OUTER face — the machine's own skin on this flank, one `enclosure.wall`
    further west. It is the machine's west exterior face."""
    return west_interior_face() - _enc.wall


def west_seam_crown():
    """What actually fences the west lane at the +Y wall of back-top: the side band the seam's own
    furniture keeps, one `enclosure.side_band_inset` inboard of that face.

    THE WALL IS NOT THE FENCE THERE. `enclosure.side_band_inset` is how far the seam's furniture
    reaches inboard on this flank, and a body on the west lane meets that first. A lane
    measured to the bare face reports fourteen millimetres that are not there."""
    return west_interior_face() + _enc.side_band_inset


PORT_LANE_CLEAR = 1.0


PORT_WEST_COLUMN = west_seam_crown() + PORT_LANE_CLEAR + _jg.BODY_D / 2.0


PANEL_X = {"bulkhead-flavor-b": PORT_WEST_COLUMN,
           "bulkhead-flavor-a": PORT_WEST_COLUMN + PORT_PITCH,
           "bulkhead-carb": PORT_WEST_COLUMN + PORT_PITCH}


PORT_FOOT_CLEAR = 1.0


FLAVOR_STOREY_DROP = 1.55


def flavor_storey(gate: float, pump_carry) -> float:
    """The storey both rear flavor unions cross the wall on: one `FLAVOR_STOREY_DROP` under the
    manifold gate's cruise.

    Foot clearance uses the union's actual stepped profile in the assembled
    native check; its largest diameter does not occupy its whole axial length.
    """
    return gate - FLAVOR_STOREY_DROP


PANEL_ON_GATE_LANE = ("bulkhead-flavor-b", "bulkhead-flavor-a")


def panel_z(name: str, deck: float, gate: float) -> float:
    """The storey one union of the row crosses the wall on — the deck, or its own run's lane."""
    return gate if name in PANEL_ON_GATE_LANE else deck


DIGITEN_STEP = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"


DIGITEN_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 90.0))


CARB_2 = 22.0


DIGITEN_CEILING_CLEAR = 1.0


DIGITEN_WEST_SET = 3.0


DIGITEN_SEAT_SLIP = fits.slip


def digiten_anchors(carry) -> tuple:
    """The station `enclosure._flow_meter_anchors` builds from — `(axis_x, axis_z, seat_r, bands)`.

    `seat_r` is one slip over the widest fixed collar radius. `bands` is that collar's own
    measured axial extent, excluding the narrower neck, housing shoulder and movable collet.
    """
    axis = carry(_digiten.inlet())[0]
    bands, radii = [], []
    for sign in (-1, 1):
        start, end, r0, r1 = _digiten.mounting_profile(sign)[-1]
        ends = [carry(((sign * x, 0.0, 0.0), (sign, 0.0, 0.0)))[0][1]
                for x in (start, end)]
        bands.append(tuple(sorted(ends)))
        radii.extend((r0, r1))
    return (axis[0], axis[2], max(radii) + DIGITEN_SEAT_SLIP, tuple(bands))


TUBE_ANCHOR_SPAN = 200.0


TUBE_ANCHOR_SLIP = fits.slip


TUBE_ANCHOR_SITES = (
    # The carb-water line's crossing, under the top wall it runs 12.6 mm below for 123 mm. The
    # wall there is back-top's ceiling slab, the face that piece prints on, so the rib stands up
    # from the bed.
    ("carb-1", 1, (0.0, 0.0, 1.0), "enclosure-back-top"),
    # The downstream gas line's aft crossing, under the same back-top ceiling slab.
    ("co2-2", 1, (0.0, 0.0, 1.0), "enclosure-back-top"),
    # Flavor B's straight cruise aft. Its rib stands ahead of the rear Wago row's
    # complete tower and worked-lever envelope; the tube retains its authored route.
    ("fluid-28", 2, (-1.0, 0.0, 0.0), "enclosure-back-top"),
)


TUBE_ANCHOR_END_FORMS = {
    "carb-1": ("corbel", "corbel"),
    "co2-2": ("corbel", "corbel"),
    "fluid-28": ("corbel", "corbel"),
}


ANCHOR_END_FORMS = ("column", "corbel")


FLAVOR_B_ANCHOR_WELL_CLEAR = 1.0


TUBE_ANCHOR_CLOSURES = {
    "carb-1": "cap",
    "co2-2": "cap",
    "fluid-28": "tie",
}


ANCHOR_CLOSURES = ("tie", "cap")


def tube_anchor_midpoint(run, leg):
    """The rib centre on its straight leg, with the flavour-B Wago working lane clear and
    `carb-1`'s anchor cap clear of `co2-1`.

    CARB-1'S RIB STANDS AT THE HEAD OF ITS CLIMB. `co2-1`'s U runs beside the middle of the
    crossing, one tied rib's reach off it (`_lines._co2_1`) and inside the anchor cap's wings,
    so the capped rib stands with its near end one `wall` past the tangent point of the bend the
    run climbs into, where the cap stands clear of the U and holds the tube where it turns."""
    p, q = run.pts[leg], run.pts[leg + 1]
    mid = tuple((p[k] + q[k]) / 2.0 for k in range(3))
    if run.id == "carb-1":
        tangents = {i: run.radii[i] * math.tan(math.radians(turn) / 2.0)
                    for i, turn, _incoming, _outgoing in run.bends}
        at = tangents.get(leg, 0.0) + _enc.wall + _anchor_cap.RIB_LEN / 2.0
        length = math.dist(p, q)
        return tuple(p[k] + (q[k] - p[k]) * at / length for k in range(3))
    if run.id != "fluid-28":
        return mid
    if abs(p[0] - q[0]) > 1e-6 or abs(p[2] - q[2]) > 1e-6 or q[1] <= p[1]:
        raise ValueError("fluid-28's wall anchor requires its aft-running straight Y leg")
    wells = [(y, size) for side, y, z, size in CLUSTER_WAGOS.values()
             if side < 0 and _enc.back_top_owns((0.0, y, z))]
    if not wells:
        raise ValueError("fluid-28's anchor has no rear Wago row to locate its working gap")
    # The complete rib, including its two end webs/corbels, occupies tube_anchor_len
    # along Y. The connector's levers also need their declared operating room.
    well_fore = min(y - max(_enc.wago_half(size)[0], _enc.wago_swing(size) / 2.0)
                    for y, size in wells)
    y = well_fore - FLAVOR_B_ANCHOR_WELL_CLEAR - _enc.tube_anchor_len / 2.0
    # Route vertices are square construction corners. The anchor must stand on
    # the actual straight left between their rounded tangent stations.
    tangents = {i: run.radii[i] * math.tan(math.radians(turn) / 2.0)
                for i, turn, _incoming, _outgoing in run.bends}
    straight_lo = p[1] + tangents.get(leg, 0.0)
    straight_hi = q[1] - tangents.get(leg + 1, 0.0)
    half = _enc.tube_anchor_len / 2.0
    if y - half < straight_lo - 1e-6 or y + half > straight_hi + 1e-6:
        raise ValueError(
            f"fluid-28 anchor Y{y-half:.3f}..{y+half:.3f} leaves its actual "
            f"straight Y{straight_lo:.3f}..{straight_hi:.3f}")
    return (mid[0], y, mid[2])


def tube_anchor_sites(runs) -> tuple:
    """`(run id, station)` per anchor. A station is `(mid, along, root, seat_r, end_forms)`,
    the first four read off the run itself and the end-web forms carried from
    `TUBE_ANCHOR_SITES` — and a sixth entry, `"cap"`, on a station an anchor cap closes
    (`TUBE_ANCHOR_CLOSURES`). A station a zip tie closes carries no sixth entry.

    The rib follows the named straight leg. Most use its midpoint; flavour B uses
    the free band ahead of the rear Wago row, including its worked levers, and `carb-1` the
    head of its climb (`tube_anchor_midpoint`). The piece
    supplies the root face, and the tube supplies the rib's X/Z and bore. A capped rib is
    longer than a tied one (`_anchor_cap_interface.RIB_LEN`), and it stands whole on the leg's
    straight, between the tangent points of the bends either end."""
    by_id = {r.id: r for r in runs}
    stations = []
    site_ids = {rid for rid, _leg, _root, _piece in TUBE_ANCHOR_SITES}
    for table, what in ((TUBE_ANCHOR_END_FORMS, "end forms"), (TUBE_ANCHOR_CLOSURES, "closures")):
        if missing := site_ids - set(table):
            raise ValueError(f"tube_anchors: no {what} stated for {sorted(missing)}")
        if unknown := set(table) - site_ids:
            raise ValueError(f"tube_anchors: {what} name no anchor site: {sorted(unknown)}")
    for rid, leg, root, _piece in TUBE_ANCHOR_SITES:
        end_forms = tuple(TUBE_ANCHOR_END_FORMS[rid])
        if len(end_forms) != 2 or any(form not in ANCHOR_END_FORMS for form in end_forms):
            raise ValueError(
                f"tube_anchors: {rid} end forms are {end_forms!r}; each of the two route ends "
                f"must be one of {ANCHOR_END_FORMS}.")
        closure = TUBE_ANCHOR_CLOSURES[rid]
        if closure not in ANCHOR_CLOSURES:
            raise ValueError(
                f"tube_anchors: {rid} is closed by {closure!r}; a closure is one of "
                f"{ANCHOR_CLOSURES}.")
        r = by_id.get(rid)
        if r is None:
            continue                        # a run whose bodies are not both placed yet
        if leg + 1 >= len(r.pts):
            raise ValueError(
                f"tube_anchors: {rid} has {len(r.pts) - 1} legs and this row names leg {leg}. "
                f"`TUBE_ANCHOR_SITES` names a leg of the route as `_lines` draws it.")
        p, q = r.pts[leg], r.pts[leg + 1]
        length = math.dist(p, q)
        u = tuple((q[k] - p[k]) / length for k in range(3))
        # A LEG NEED NOT BE AXIAL, only square to the face. The rib is extruded along the tube and
        # its two ends are cut square to that, so what it asks of the leg is that the face it
        # roots on lies at one distance down the whole of it — which is the test below and not
        # this one. A leg that leans in the plane of its own wall passes both.
        if abs(sum(u[k] * root[k] for k in range(3))) > 1e-9:
            raise ValueError(
                f"tube_anchors: {rid} leg {leg} runs along {u} and this row roots it on {root}. "
                f"An anchor stands ACROSS its tube, never off the face the tube points at.")
        if length < _enc.tube_anchor_len:
            raise ValueError(
                f"tube_anchors: {rid} leg {leg} is {length:.2f} mm and a rib is "
                f"{_enc.tube_anchor_len:.2f}. A seat longer than the straight it stands on would "
                f"close on the corners either side of it.")
        mid = tube_anchor_midpoint(r, leg)
        station = (mid, u, tuple(root), r.diam / 2.0 + TUBE_ANCHOR_SLIP, tuple(end_forms))
        if closure == "cap":
            tangents = {i: r.radii[i] * math.tan(math.radians(turn) / 2.0)
                        for i, turn, _incoming, _outgoing in r.bends}
            at = math.dist(p, mid)
            lo, hi = tangents.get(leg, 0.0), length - tangents.get(leg + 1, 0.0)
            half = _anchor_cap.RIB_LEN / 2.0
            if at - half < lo - 1e-6 or at + half > hi + 1e-6:
                raise ValueError(
                    f"tube_anchors: {rid}'s capped rib runs {at - half:.2f}..{at + half:.2f} mm "
                    f"along leg {leg}, whose straight is {lo:.2f}..{hi:.2f}. A rib off the "
                    f"straight closes on the bend either side of it.")
            station += ("cap",)
        stations.append((rid, station))
    return tuple(stations)


BODY_ANCHOR_SLIP = fits.slip


BODY_ANCHOR_SITES = (
    # The regulator's barrel, between its two wrench hexes — off back-top's ceiling slab.
    ("wr1110", _wr1110.barrel, (0.0, 0.0, 1.0), "enclosure-back-top"),
    # The downstream check's inlet boss; the bowed connecting tubes do not locate its body.
    ("gasher-co2", _gas_chain.check_socket, (0.0, 0.0, 1.0), "enclosure-back-top"),
    # The water split's seat closes on its fixed run section in the west wall.
    ("water-split", lambda: _split.clearance_seat(_enc.tube_anchor_len, _enc.tie_w),
     (-1.0, 0.0, 0.0), "enclosure-back-top"),
)


BODY_ANCHOR_END_FORMS = {
    "wr1110": ("corbel", "corbel"),
    "gasher-co2": ("corbel", "corbel"),
    "water-split": ("corbel", "corbel"),
}


def body_anchors(carries) -> tuple:
    """One station per body anchor — `(mid, along, root, seat_r)`, the shape `_tube_anchors`
    builds a rib from, all of it read off the body's own section.

    THE SECTION IS THE REFERENCE MODULE'S, and that module holds it to the file the pack seats.
    So the seat rides every move of the body, and there is no radius stated here to go stale.

    THE RIB LIES INSIDE ITS SECTION. A run is one radius its whole length and a fitting is not:
    a rib must clear whatever stands beside its bearing. The water split qualifies its complete
    clearance span separately from the narrower measured collar patch the tie bears on; its
    reference checks both the branch and release room before supplying that envelope."""
    stations = []
    site_ids = {name for name, _s, _r, _p in BODY_ANCHOR_SITES}
    if missing := site_ids - set(BODY_ANCHOR_END_FORMS):
        raise ValueError(f"body_anchors: no end forms stated for {sorted(missing)}")
    if unknown := set(BODY_ANCHOR_END_FORMS) - site_ids:
        raise ValueError(f"body_anchors: end forms name no anchor site: {sorted(unknown)}")
    for name, section, root, _piece in BODY_ANCHOR_SITES:
        carry = carries.get(name)
        if carry is None:
            continue                        # a body that is not placed yet
        station, r, length = section()
        mid, u = carry(station)
        if abs(sum(u[k] * root[k] for k in range(3))) > 1e-9:
            raise ValueError(
                f"body_anchors: {name}'s section runs along {u} and this row roots it on {root}. "
                f"An anchor stands ACROSS the body, never off the face the body points at.")
        if length < _enc.tube_anchor_len:
            raise ValueError(
                f"body_anchors: {name}'s section is {length:.2f} mm and a rib is "
                f"{_enc.tube_anchor_len:.2f}. A seat longer than the section it bears on closes "
                f"on whatever is either side of it.")
        stations.append((tuple(mid), tuple(u), tuple(root), r + BODY_ANCHOR_SLIP,
                         tuple(BODY_ANCHOR_END_FORMS[name])))
    return tuple(stations)


def cap_tube_anchors(foam_carry, runs) -> tuple:
    """Every rib the cold core's cap stands for a RUN, as `unsupported_spans` reads a station.

    A row in `_cold_core_interface.cap_anchors` named for a run is one; a row named for a body is
    the chains', and holds nothing this counts. The seat's world axis is the cap's own station
    carried out, and the tube lies along whichever of its legs passes through it."""
    by_id = {r.id: r for r in runs}
    out = []
    for name in _cci.cap_anchors:
        r = by_id.get(name)
        if r is None:
            continue
        mid = foam_carry(cap_anchor(name))[0]
        for i in range(len(r.pts) - 1):
            p, q = r.pts[i], r.pts[i + 1]
            if not _on_leg(mid, p, q, 1e-3):
                continue
            d = math.dist(p, q)
            out.append((mid, tuple((q[k] - p[k]) / d for k in range(3)),
                        (0.0, 0.0, -1.0), _cci.cap_anchors[name].seat_r))
            break
        else:
            raise ValueError(
                f"cap_tube_anchors: the rib for {name} stands at {mid} and no leg of that run "
                f"passes through it. `_cold_core_interface.cap_anchors[{name!r}].centre` is in "
                f"the cap's own frame, and the run is where its two ports put it.")
    # AND THE POSTS THAT GRIP SIDEWAYS. Same reading, one axis over: the seat's root is the core
    # behind it rather than the lid under it, so the station carries −Y where the anchors carry
    # −Z, and the run has to pass through the pipe's own axis just the same.
    for name in _cci.cap_side_anchors:
        r = by_id.get(name)
        if r is None:
            continue
        mid, root = foam_carry(cap_side_anchor(name))
        for i in range(len(r.pts) - 1):
            p, q = r.pts[i], r.pts[i + 1]
            if not _on_leg(mid, p, q, 1e-3):
                continue
            d = math.dist(p, q)
            out.append((mid, tuple((q[k] - p[k]) / d for k in range(3)),
                        tuple(root), _cci.cap_side_anchors[name].seat_r))
            break
        else:
            raise ValueError(
                f"cap_tube_anchors: the side post for {name} stands its pipe at {mid} and no leg "
                f"of that run passes through it. "
                f"`_cold_core_interface.cap_side_anchors[{name!r}]` is in the cap's own frame, "
                f"and the run is where its two ports put it.")
    return tuple(out)


def lid_cap_stations(foam_carry, runs) -> tuple:
    """`(name, mid, along)` for every rib on the cold core's lid an anchor cap closes
    (`_cold_core_interface.cap_anchors`, closure "cap"): the seat's world axis point, carried out
    of the cap's own frame, and the run's leg through it. The cap roots on the lid, so its frame's
    root direction is the world's −Z."""
    by_id = {r.id: r for r in runs}
    out = []
    for name, row in _cci.cap_anchors.items():
        r = by_id.get(name)
        if row.closure != "cap" or r is None:
            continue
        mid = foam_carry(cap_anchor(name))[0]
        for p, q in zip(r.pts, r.pts[1:]):
            if _on_leg(mid, p, q, 1e-3):
                d = math.dist(p, q)
                out.append((name, mid, tuple((q[k] - p[k]) / d for k in range(3))))
                break
        else:
            raise ValueError(
                f"lid_cap_stations: the capped rib for {name} stands at {mid} and no leg of that "
                f"run passes through it.")
    return tuple(out)


def reservoir_a_anchor_sites(runs) -> tuple:
    """Actual paired-lid seat stations, one per held tube at each shared tie.

    These are nominal restraint locations. They do not establish tie gripping
    force, tube side loads or physical retention.
    """
    import _reservoir_a_anchors
    by_id = {run.id: run for run in runs}
    spec = _reservoir_a_anchors.specification()
    return tuple(
        (identifier, (tuple(point), tuple(axis),
                      (0., 0., -1.), row.get('seat_radius_mm', spec['seat_radius_mm'])))
        for row in _reservoir_a_anchors.datums().values()
        for identifier, point, axis in zip(row['routes_west_to_east'],
                                          row['tube_centers_world_mm'],
                                          row['tube_axes_world'])
        if identifier in by_id)


def reservoir_a_developed_stations(run, points):
    """Exact native line/arc lengths at the A seats, for the current route only."""
    if run.id not in ('fluid-14', 'fluid-16'):
        return None
    import above_core_routes
    spec = above_core_routes.reservoir_a_route_specs()[run.id]
    if len(run.pts) != len(spec['points_mm']) or any(
            math.dist(a, b) > 1.e-6 for a, b in zip(run.pts, spec['points_mm'])):
        return None
    cuts = [0.]
    distance = 0.
    for segment in spec['segments']:
        if segment['kind'] == 'line':
            p, q = segment['points_mm']
            cuts.extend(distance + math.dist(p, point) for point in points
                        if _on_leg(point, p, q, 1.e-6))
            distance += math.dist(p, q)
        else:
            center, axis = segment['center_mm'], segment['axis']
            radius, angle = segment['radius_mm'], segment['angle_rad']
            start = tuple(p-c for p, c in zip(segment['points_mm'][0], center))
            for point in points:
                radial = tuple(p-c for p, c in zip(point, center))
                if (abs(math.dist(point, center)-radius)>1.e-6
                        or abs(sum(a*b for a, b in zip(radial, axis)))>1.e-6):
                    continue
                cross = (start[1]*radial[2]-start[2]*radial[1],
                         start[2]*radial[0]-start[0]*radial[2],
                         start[0]*radial[1]-start[1]*radial[0])
                turn = math.atan2(math.copysign(1., angle)*sum(a*b for a, b in zip(axis, cross)),
                                  sum(a*b for a, b in zip(start, radial)))
                if turn < -1.e-6/radius:
                    turn += 2*math.pi
                if turn <= abs(angle)+1.e-6/radius:
                    cuts.append(distance+radius*max(0., turn))
            distance += radius * abs(angle)
    cuts.append(distance)
    return tuple(sorted(set(cuts)))


def unsupported_spans(runs, stations) -> dict:
    """The longest stretch of each run that nothing holds — the reading `tube-anchored` grades.

    A run is held at its two ends and wherever an anchor sits on it. Between those points it is
    one continuous elastic member, free to turn at every corner, so what spans is the DEVELOPED
    length from one held point to the next."""
    out = {}
    for r in runs:
        native = reservoir_a_developed_stations(r, [row[0] for row in stations])
        if native is not None:
            out[r.id] = max(b-a for a, b in zip(native, native[1:]))
            continue
        # Each corner's own shortening, taken at the waypoint it turns about, so the stations walk
        # the DEVELOPED length `Run.length` reports and this goal cannot disagree with the card
        # about how long a run is.
        short = {i: 2.0 * r.radii[i] * math.tan(math.radians(turn) / 2.0)
                    - r.radii[i] * math.radians(turn)
                 for i, turn, _li, _lo in r.bends}
        cuts, s = [0.0], 0.0
        for i in range(len(r.pts) - 1):
            s -= short.get(i, 0.0)
            for station in stations:
                mid, _u, _n, _seat = station[:4]
                if _on_leg(mid, r.pts[i], r.pts[i + 1]):
                    cuts.append(s + math.dist(r.pts[i], mid))
            s += math.dist(r.pts[i], r.pts[i + 1])
        cuts.append(s)
        cuts.sort()
        out[r.id] = max(b - a for a, b in zip(cuts, cuts[1:]))
    return out


def _on_leg(pt, p, q, tol=1e-6) -> bool:
    """Whether `pt` lies on the segment `p..q` — an anchor's own leg and no other."""
    d = math.dist(p, q)
    if d < tol:
        return False
    return abs(math.dist(p, pt) + math.dist(pt, q) - d) < tol


ASSE_TIE_T = 1.0


ASSE_TIE_CLEAR = 0.5


def interior_ceiling() -> float:
    """The plane the top wall's inner face lies on, off the appliance's own stated height.

    The height is struck from the floor slab's underside, so the cavity is what the stated
    number leaves once the slab and the top wall are both out of it — and the slab is the
    thicker of the two (`enclosure.floor_t`)."""
    return _enc.appliance_height - _enc.floor_t - _enc.ceiling_skin


C14_STEP = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"


def c14_mount_half() -> tuple:
    """Half extents of the tunnel block carrying the bore, the two inserts and the flange's
    pocket."""
    _kind, _cx, _cz, wx, wz, _r = c14_cutout()
    return _enc.c14_mount_half(wx, wz,
                               _enc.c14_screw_pitch / 2.0)


C14_STATION = (_above.pose('c14-inlet')['translation_mm'][0],
               _above.pose('c14-inlet')['translation_mm'][2])


def c14_seat_y() -> float:
    """The plane the receptacle's flange bears on — the FORE face of `enclosure._c14_tunnel`,
    and not the +Y wall of back-top's inner face.

    It is struck from the outside in, off the two things that have to stand between that flange
    and the customer: `enclosure.heatset_depth` of insert entering this face from inside the
    machine, and `enclosure.socket_cap` over its blind end. Where the boundary between tunnel and
    wall falls inside that stack does not move the plane — the wall carries the cap and the
    tunnel carries the insert, and the sum is what the receptacle sits behind."""
    x, z = C14_STATION
    return (_enc.rear_plane_y + _enc.wall) - _enc.back_wall_t_at(x, z) - _enc.c14_tunnel_len


def c14_stations():
    """The two heat-set screw stations on the +Y wall of back-top, as `(x, z)` — `enclosure._c14_tunnel`
    bores one into its fore face at each. Both sit ON the mating axis, so the pair follows the
    one station the receptacle is placed at, and the tunnel's own width across X is struck to
    reach them."""
    return tuple((C14_STATION[0] + dx, C14_STATION[1])
                 for dx in (-_enc.c14_screw_pitch / 2.0, _enc.c14_screw_pitch / 2.0))


def c14_cutout():
    """The bore in the wall, in `back_ports` shape — struck on the same station the body is.

    The flange never passes this wall: the inlet's rim bears on the pocket floor around this
    bore and its ears are the pocket's. What the wall's opening shows is the cavity the rim
    frames, and the C13 nose comes down this bore to it."""
    return ("rect", C14_STATION[0], C14_STATION[1],
            _enc.c14_bore_w, _enc.c14_bore_h, _enc.c14_bore_r)


CO2_CHAIN_TURN = (((0.0, 0.0, 1.0), 180.0),)


def keystone_cutout(station: tuple):
    """The opening the jack snaps into, in `back_ports` shape."""
    wx = _keystone.FACE_W + 2.0 * fits.slip
    wz = _keystone.FACE_H + 2.0 * fits.slip
    r = _keystone.panel_cutout()[2]
    x, z = station
    return ("rect", x, z, wx, wz, r)


CO2_REGULATOR_SETBACK = 58.0


CO2_CHECK_SIDE_OFFSET = 36.0


CO2_CHECK_FORWARD_OFFSET = 20.0


def co2_inlet_mouth_y():
    """The Y of the ABU44's INBOARD collet face — the mouth `co2-0` leaves by, and so where the
    whole chain starts. Read off `bulkhead_seat_y` through the fitting's own reach, exactly as
    `bulkhead_mouth_y` reads the unions: the flange bears on the port field's crown and what the
    fitting takes inboard of that is its own business."""
    return bulkhead_seat_y() + _neofit.far_ring_face_y


def co2_wall_port(inlet_carry):
    """The bore the ABU44's M17 barrel passes, as a `back_ports` entry. Struck on the fitting's
    own inboard collet so hole and barrel cannot land on two different columns, and bored one
    `PORT_HOLE_SLIP` over that barrel — the same construction the four unions' bores take."""
    pos = inlet_carry(_neofit.port(-1.0))[0]
    return ("round", pos[0], pos[2], _neofit.panel_hole_d(PORT_HOLE_SLIP))


STANDALONE = ("compressor", "condenser+fan", "foam-assembly", "g-ganen-pump",
              *(f"{name}{part}" for name, _toward in PUMP_ELBOWS.values()
                for part in ("", "-clamp-barb", "-clamp-tube")),
              "funnel", "discharge-chain", "display", "display-cover",
              "display-gasket",
              "psu", "pcba",
              "relay-1", "relay-2", "asse1022-assembly",
              "bulkhead-drain", *_drain.ADAPTER_NAMES,
              "mq6-sensor", "thermal-fuse", "fuse-clamp",
              ) + WAGO_POLES + tuple(CLUSTER_WAGOS) + (
              "water-split", "flow-regulator", "vk-solenoid", "bulkhead-water",
              "c14-inlet", "co2-inlet", "gasher-co2", "wr1110",
              *_gas_chain.ADAPTER_NAMES,
              "nameplate", "nameplate-ink",
              "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb", "digiten-flow",
              *(f"anchor-cap-{rid}" for rid, closure in TUBE_ANCHOR_CLOSURES.items()
                if closure == "cap"),
              *(f"anchor-cap-{name}" for name, row in _cci.cap_anchors.items() if row.closure == "cap"))


def _manifold(name):
    return (name not in STANDALONE and not name.startswith("enclosure-")
            and name not in _ROUTED)


_ROUTED: set = set()


def east_wall_seat():
    """The plane a body hung on the east wall stands its outer face on: one complete mounting
    boss inboard of the box's BASE interior plane.

    Read off the wall and not off whichever body is widest on the floor. The boss is built on
    the wall, so a body that seats on the boss's own tip seats on the wall whatever else is
    packed beside it — and a narrower body arriving on the floor moves neither.

    AND THE PLANE IT IS STRUCK ON IS THE BOX'S, NOT THE PIECE'S. Every east-wall body lands on
    back-top, whose flank stands `back_top_flank_t` where the box carries one `wall`
    (`enclosure.back_top_flank_face`, 98.5 against `interior_x`'s 104.5) — so this seat is one
    boss inboard of a plane six millimetres outboard of the face the body actually meets, and
    what it leaves between body and wall is 0.25 mm rather than a boss. `enclosure._east_bosses`
    reads the piece's own face and builds no stem for a stand that short, so those bodies bolt
    flat to the flank with their inserts in its own section. Struck on the face that is there
    this plane would be 92.25, which is a different packing and not a different comment."""
    return _enc.interior_x()[1] - _enc.mount_boss_out


FLOOR_BOSS_SLIP = 1.0


FLOOR_GROMMET_SQUEEZE = 0.4


def floor_mounts(*mounted):
    """The floor slab's boss stations, as `(x, y, tip, dia)`.

    `wall_mounts`' analogue for a body bolted DOWN onto the slab rather than hung on the
    flank. One `(carry, holes, face_z, bore_d)` per body: the placement, the body's own hole
    pattern, the height in that body's own frame of its grommet's crown, and the bore each post
    rises through. A body standing on the floor has that crown at the TOP of whatever the hole
    passes through, not at its own Z = 0 — the post rises through the hole to it, which is what
    locates the body as well as fastens it.

    THE POST'S SECTION IS THE DONOR'S, struck off that bore less one `FLOOR_BOSS_SLIP` on the
    radius, so a body whose holes are measured again moves its own posts with it and no
    diameter for them is typed anywhere. ITS CROWN IS THE DONOR'S LESS THE SQUEEZE: the post
    stops the washer one `FLOOR_GROMMET_SQUEEZE` under the grommet's own crown, which is the
    preload the flange carries."""
    out = []
    for carry, holes, face_z, bore_d in mounted:
        for hx, hy in holes:
            pos, _axis = carry(((hx, hy, face_z), (0.0, 0.0, 1.0)))
            out.append((pos[0], pos[1], pos[2] - FLOOR_GROMMET_SQUEEZE,
                        bore_d - 2.0 * FLOOR_BOSS_SLIP))
    return tuple(out)


PSU_TURN = (((0.0, 1.0, 0.0), -90.0),)


PSU_AFT_WIRE_ALLOWANCE = 5.0


PSU_RELAY_BODY_GAP = 4.0


RELAY_BOARD_BODY_GAP = 3.0


PCBA_TURN = (((0.0, 1.0, 0.0), -90.0), ((1.0, 0.0, 0.0), -90.0))


WIRED_CLEAR = 6.0


RELAY_TURN = (((0.0, 0.0, 1.0), 270.0), ((0.0, 1.0, 0.0), 270.0))


RELAY1_CORBEL_LIFT = 0.0


WAGO_TURN = (((1.0, 0.0, 0.0), 90.0), ((0.0, 1.0, 0.0), -90.0))


WAGO_TURN_WEST = (((1.0, 0.0, 0.0), 90.0), ((0.0, 1.0, 0.0), 90.0))


WAGO_CORBEL_FLOOR_CLEAR = 1.0


def _wago_skirt(size="413"):
    """What a well reaches PAST its lug on the row's cross axis — the wall it wraps the lug in,
    plus that wall's press clearance.

    The lug is what gets placed and the WELL is what can foul a neighbour, and the well is the
    bigger of the two. Clearing the brick's crown by the lug's own bottom face would bury the
    skirt in it, so every clearance struck against this row is struck against the tower."""
    return _enc.wago_half(size)[1] - _enc.wago_stand(size)[1] / 2.0


def wago_row_reach() -> float:
    """How far aft the last lug of a five-wide 221-413 row reaches from the row's own origin —
    four pitches, the well wall the first lug starts past, and one lug's own height."""
    return 4.0 * _enc.wago_pitch + _enc.wago_well_wall + _enc.wago_stand("413")[0]


def wago_wells(row, cluster, over):
    """Every wall's well stations, `(side, y, z, size, clear_z, supportless_roof)` — one per
    placed lug, read off the lug's own box so a well cannot end up anywhere but under the thing
    it holds.

    Separate wells keep the two-tab, 45°-ramped lid on their print-down face.
    The lower manifold well has a full lid, retaining the 3.2 mm web between
    the stacked connector pockets. `clear_z` is the plane on the tower's print-down side that its
    wedge may not cross. The five power-row wells stand on back-top's +X wall, whose print-up is
    `enclosure.print_up("back", "top")`: printing machine −Z up, the row's wedge stands over the
    tower and that plane is the ceiling slab's interior face
    (`enclosure.back_top_ceiling_face`) — the piece's own stock, which the wedge is cut off flat
    against, and the plane the tower stands on as a column where `stand_wells` reads the air to
    it free; printing machine +Z up, the wedge hangs under the tower and the plane is `over`,
    the crown of the brick the row runs along. A cluster well in back-top's band carries the
    same ceiling face when that piece prints ceiling-down; one on a mouth-down piece carries
    None, since its wall is open under it on that print."""
    up = _enc.print_up("back", "top")
    row_clear = over if up > 0 else _enc.back_top_ceiling_face()
    out = []
    for _name, solid, _carry in row:
        b = box(solid)
        out.append((+1, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0,
                    "413", row_clear, True))
    for name, solid, _carry, size in cluster:
        b = box(solid)
        centre = ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0)
        cluster_clear = (_enc.back_top_ceiling_face()
                         if up < 0 and _enc.back_top_owns(centre) else None)
        out.append((CLUSTER_WAGOS[name][0], centre[1], centre[2], size, cluster_clear,
                    name != "wago-manb"))
    return tuple(out)


ASSE1022_YAW = -90.0


ASSE_SEAT_SLIP = fits.slip


ASSE_STEP_SLIP = 0.5


def asse_sections(asse_carry) -> tuple:
    """The chain's own sections, forward to aft, as `(y0, y1, west_x, seat_r, axis_x)` — the band
    each occupies down the lane, how far west its seat reaches, the bore radius a round one takes,
    and the axis a bore is struck on. `seat_r` is None where the section is seated on a V.

    A HEX GETS A V AND A CIRCLE GETS A BORE. The hex's V is read off the corner it lies on, so its
    apex stands one circumradius under the axis; a round section is held in a bore concentric with
    it, one `ASSE_SEAT_SLIP` over its own circumradius, stopped at the axis plane where its lip is
    still a lip. That is the whole of why the barrel steps out of its neighbours and not a number
    chosen here.

    Read through `asse_carry`, so a fitting whose length changes moves its own step."""
    axis = asse_carry(_asse.flow_axis())[0]
    def band(part_x0, part_x1, across, hexed):
        # +X in the chain's frame is the machine's −Y: the yaw lays the flow forward down the
        # lane, so a section's upstream end is its AFT end.
        ends = sorted(asse_carry(((x, 0.0, _asse.bfp.BODY_CENTER_Z), (1.0, 0.0, 0.0)))[0][1]
                      for x in (part_x0, part_x1))
        if hexed:
            west = axis[0] - across / 2.0 - ASSE_SEAT_SLIP / math.sin(math.radians(60.0))
            return (ends[0], ends[1], west, None, axis[0])
        seat_r = across / 2.0 + ASSE_SEAT_SLIP
        return (ends[0], ends[1], axis[0] - seat_r, seat_r, axis[0])
    rows = (
        # the PI4512F6S's swivel nut, forward of the barrel — round, because it spins
        band(_asse.OUTLET_X, _asse.OUTLET_X + _oad.NUT_LENGTH, _oad.NUT_ACROSS_CORNERS, False),
        # the Multiplex's brass hex barrel, and the one section whose flats are read as flats
        band(_asse.BARREL_UPSTREAM, _asse.BARREL_DOWNSTREAM,
             _asse.bfp.HEX_ACROSS_CORNERS, True),
        # the GAGIRA coupling, aft. NOT the 3/8" NPT inlet stub it threads onto: the coupling's
        # `LARGE_SOCKET_DEPTH` is the whole of that stub, so the stub is never a section this
        # wall sees — what stands in the band is the coupling's own hex, round-seated because
        # its clock is wherever its thread stopped.
        band(_asse.COUPLING_X, _asse.COUPLING_X + _asse.coupling.LENGTH,
             _asse.coupling.HEX_ACROSS_CORNERS, False),
    )
    # THE DEEPER SECTION TAKES THE SLIP AT EVERY BOUNDARY. A step is a face square to the axis,
    # and the millimetre either side of it belongs to the deeper of the two sections it divides —
    # so the deep section is longer than the fitting in it and the step is a stop that fitting
    # travels to.
    # BOTH END SECTIONS RUN THE SHORTER OF THE TWO FITTINGS' LENGTHS. What the anchor puts at each
    # end of the barrel is a face square to the axis, and the fitting past that face is seated on
    # the section it presents rather than followed down its length.
    reach = min(r[1] - r[0] for r in (rows[0], rows[-1]))
    rows = ((rows[0][1] - reach, rows[0][1], *rows[0][2:]), rows[1],
            (rows[-1][0], rows[-1][0] + reach, *rows[-1][2:]))
    out = [list(r) for r in rows]
    for i in range(len(out) - 1):
        deep = i if out[i][2] < out[i + 1][2] else i + 1
        edge = out[i][1] + (ASSE_STEP_SLIP if deep == i else -ASSE_STEP_SLIP)
        out[i][1], out[i + 1][0] = edge, edge
    return tuple(tuple(r) for r in out)


ASSE_TIE_VENT_CLEAR = 1.5


ASSE_TIE_NECK_ALLOWANCE_D = 9.53  # Clear-band allocation around the vent axis.


def asse_ties(asse_carry) -> tuple:
    """The Y of each tie band — the middle of the clear run the vent leaves on either side of it.

    BOTH ARE ON THE BRASS. The barrel is the one section a tie may close on: the JG acetal nut
    and the PP reducer go out of round under one, and the nut is the part whose clock means
    nothing anyway. Its vent stands out of the middle of it, so the barrel's own length
    offers exactly these two bands and no others."""
    _fwd, barrel, _aft = asse_sections(asse_carry)
    vent = asse_carry(_asse.port("vent-tip"))[0]
    edge = ASSE_TIE_NECK_ALLOWANCE_D / 2.0 + ASSE_TIE_VENT_CLEAR
    return ((barrel[0] + (vent[1] - edge)) / 2.0, ((vent[1] + edge) + barrel[1]) / 2.0)


def asse_reach_down(asse_carry) -> float:
    """How far under the axis the anchor's flanks run — the chain's OWN lowest arris, and not a
    millimetre past it.

    Every section's lowest point below the axis is its apothem if the anchor reads its flats and
    its radius if it reads its tangent, so the deepest of the three is what the anchor has to
    reach and anything under that is PETG holding air. It is the barrel's, being both the widest
    section and the one seated on flats.

    The vent stub hangs far below all of this and is not in it: the anchor would have to be
    notched around the fall, and what stands under the barrel is the tray."""
    return max(axis_z_drop for axis_z_drop in _asse_section_drops(asse_carry))


def _asse_section_drops(asse_carry):
    """Each section's own reach under the axis — apothem for the one read off flats, radius for
    the ones read off their tangent."""
    yield _asse.bfp.HEX_ACROSS_CORNERS / 2.0 * math.cos(math.radians(30.0))
    yield _oad.NUT_ACROSS_CORNERS / 2.0
    yield _asse.coupling.HEX_ACROSS_CORNERS / 2.0


def asse_cradle(asse_carry) -> tuple:
    """The whole station `enclosure._asse_cradle` builds from: the axis the ASSE anchor is struck on,
    its sections, the two tie bands, and how far under the axis its flanks reach."""
    axis = asse_carry(_asse.flow_axis())[0]
    return (axis[2], asse_sections(asse_carry), asse_ties(asse_carry),
            asse_reach_down(asse_carry))


def anchor_rows(foam_carry, bodies: dict) -> list:
    """Each chain anchor as `(name, label, has, wants, fouls)` — the rib the cap carries against
    the sections of the placed body it stands under.

    A RIB MAY BE LONGER THAN THE SECTION IT BEARS ON. So the test is not containment but
    clearance — exactly one section under the rib FILLS the bore, and every other one it overhangs
    onto has to pass under it. `fouls` names any that does not.

    `wants` is the filling section's own circumradius plus `CHAIN_SEAT_SLIP`, read off the body's
    own stack. The cap prints a rib it never sees the body of, so the body is what corrects it.

    A RIB BORED FOR A RUN IS NOT ROWED HERE. A tube is one section its whole length, so there is
    no stack to read and nothing for a rib to foul."""
    rows = []
    for name, station in _cci.cap_anchors.items():
        if name not in bodies:
            continue
        carry, mod = bodies[name]
        axis = foam_carry(cap_anchor(name))[0]
        tip = carry(mod.inlet())[0]
        half = _cci.cap_anchor_len / 2.0
        # Sections measure positive flow distance from the inlet mouth.
        outlet = carry(mod.outlet())[0]
        direction = cq.Vector(*outlet)-cq.Vector(*tip)
        distance = (cq.Vector(*axis)-cq.Vector(*tip)).dot(direction.normalized())
        s0, s1 = distance-half, distance+half
        under = [(lab, r) for lab, r, a, b in mod.sections() if a < s1 - 1e-9 and s0 + 1e-9 < b]
        fills = [(lab, r) for lab, r in under if abs(r + CHAIN_SEAT_SLIP - station.seat_r) <= 1e-3]
        fouls = [lab for lab, r in under if r + CHAIN_SEAT_SLIP > station.seat_r + 1e-3]
        label, r = fills[0] if fills else (
            max(under, key=lambda s: s[1]) if under else ("nothing", 0.0))
        rows.append((name, label, station.seat_r, r + CHAIN_SEAT_SLIP, fouls if fouls or fills
                     else ["no section fills the bore"]))
    return rows


SPLIT_TURN = (((0.0, 1.0, 0.0), -90.0),)


FLAVOR_STEP = 42.20


BOWL_CLEAR = 1.0


WATER_2 = 42.0


SPLIT_FLANK_OFFSET = 8.65


def _whole(bodies):
    out = None
    for s in bodies:
        b = box(s)
        out = b if out is None else out.add(b)
    return out


PACK_Y = 14.48


def manifold_carry(lift: float):
    """The same two turns, the same depth and the same lift, as a `carry` for a STATION.

    `manifold_layout.port` and its siblings answer in the pack's OWN world — the frame the fold
    leaves it in — and `build_pack` then poses that whole world and stands it on the base's
    crown. A line reaching a valve's collet has to arrive where the collet ends up, so the
    station rides the same transform the solid does: `(x, y, z) → (−x, z + PACK_Y, y + lift)`,
    which is what the two rotations and the two datums compose to."""
    def carry(station):
        (px, py, pz), (ax, ay, az) = station
        return ((-px, pz + PACK_Y, py + lift), (-ax, az, ay))
    return carry


def manifold_pump_trays(carry) -> tuple:
    """The authored head bracket datums in the installed manifold frame."""
    head_y = -ml.BARB_INSET + ml.PUMP_Y - ml.kp.head_front_z + ml.kp.base_plane_z
    head_z = ml.PUMP_BARB_Z - ml.kp.body_y_face + ml.kp.cy
    stations = []
    for _name, px in sorted(ml.PUMPS.items()):
        centre = list(carry(((px, head_y, head_z), (0., 1., 0.)))[0])
        centre[2] += _enc._interface.pump_seated_drop
        stations.append(tuple(round(value, 6) for value in centre))
    return tuple(stations)


def manifold_references(a):
    """Explicit selections of the already-world-placed manifold fine file."""
    import _assembly_model
    reading = getattr(a, 'manifold_reading', None)
    if reading is None:
        return {}
    indices = {}
    for index, row in enumerate(reading.summaries):
        indices.setdefault(row['name'], []).append(index)
    return {name: _assembly_model.instance(reading.model, indices=selection)
            for name, selection in indices.items()}


def _with_manifold_rows(a, native, rows):
    """Insert explicit named rows at the manifold node's existing assembly position."""
    before = set()
    for child in a.children:
        if child.name == 'manifold-layout':
            break
        before.add(child.name)
    out, inserted = {}, False
    for name, value in native.items():
        if not inserted and name not in before:
            out.update(rows)
            inserted = True
        out[name] = value
    if not inserted:
        out.update(rows)
    return out


THROUGH_WALL = ("bulkhead-water", "c14-inlet", "keystone-jack", "co2-inlet",
                "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb",
                "bulkhead-drain")


CEILING_RELIEF_PLAN_SLIP = 2.0


CEILING_RELIEF_Z_CLEAR = 1.0


CEILING_RELIEF_LEVEL_GROUPS = (
    ("asse1022-assembly",),
    ("digiten-flow",),
    # Made-up gas fittings take one pocket roof per assembly. This preserves each member's
    # own plan while avoiding sub-wall steps over its adjacent adapter hexes.
    ("wr1110", _gas_chain.REG_IN_ADAPTER, _gas_chain.REG_OUT_ADAPTER),
    ("gasher-co2", _gas_chain.CHECK_IN_ADAPTER, _gas_chain.CHECK_OUT_ADAPTER),
)


CEILING_RELIEF_LANE_BODIES = ("asse1022-assembly",)


CEILING_RELIEF_MIN_DEPTH_BODIES = ("gasher-co2",)


CEILING_RELIEF_CONNECTOR_PAIRS = (("asse1022-assembly", "bulkhead-water"),
                                  ("digiten-flow", "wr1110"))


CEILING_RELIEF_CONNECTOR_ENTRY = 0.5


CEILING_RELIEF_ENVELOPE_BODIES = ("digiten-flow",)


def _contained_reliefs(reliefs: tuple) -> tuple:
    """Keep the larger of same-name, same-roof plan boxes when one contains the other."""
    out = []
    tol = _enc.stated_bound_tol
    for row in reliefs:
        contained = False
        remove = []
        for i, other in enumerate(out):
            if row[0] != other[0] or abs(row[5] - other[5]) > tol:
                continue
            other_contains = (other[1] <= row[1] + tol and other[2] >= row[2] - tol
                              and other[3] <= row[3] + tol and other[4] >= row[4] - tol)
            row_contains = (row[1] <= other[1] + tol and row[2] >= other[2] - tol
                            and row[3] <= other[3] + tol and row[4] >= other[4] - tol)
            if other_contains:
                contained = True
                break
            if row_contains:
                remove.append(i)
        if contained:
            continue
        for i in reversed(remove):
            out.pop(i)
        out.append(row)
    return tuple(out)


def _enveloped_reliefs(reliefs: tuple) -> tuple:
    """Keep a connected pocket; envelope overlapping sections as one box, and leave sections
    that stand apart in plan as their own boxes."""
    out = list(reliefs)
    for name in CEILING_RELIEF_ENVELOPE_BODIES:
        indices = [i for i, row in enumerate(out) if row[0] == name]
        if len(indices) < 2:
            # The lifted native section already joins the ring crowns through their neck.
            # Its containing plan needs no additional union or empty-corner enlargement.
            continue
        rows = [out[i] for i in indices]
        tol = _enc.stated_bound_tol
        x_overlap = min(row[2] for row in rows) - max(row[1] for row in rows)
        y_overlap = min(row[4] for row in rows) - max(row[3] for row in rows)
        if x_overlap <= tol or y_overlap <= tol:
            continue
        envelope = (
            name,
            min(row[1] for row in rows), max(row[2] for row in rows),
            min(row[3] for row in rows), max(row[4] for row in rows),
            max(row[5] for row in rows),
        )
        first = indices[0]
        out = [row for row in out if row[0] != name]
        out.insert(first, envelope)
    return tuple(out)


def _level_reliefs(reliefs: tuple) -> tuple:
    """Give each reviewed group one roof plane without changing a member's plan."""
    out = tuple(reliefs)
    for group in CEILING_RELIEF_LEVEL_GROUPS:
        roof = max((row[5] for row in out if row[0] in group), default=None)
        if roof is not None:
            out = tuple(row[:5] + (roof,) if row[0] in group else row for row in out)
    return out


def _full_depth_reliefs(reliefs: tuple) -> tuple:
    """Reject a local ceiling pocket shallower than one printable wall."""
    face = _enc.back_top_ceiling_face()
    tol = _enc.stated_bound_tol
    for row in reliefs:
        depth = row[5] - face
        if tol < depth < _enc.wall - tol:
            raise ValueError(
                f"ceiling relief `{row[0]}` is only {depth:.3f} mm deep; level it with its "
                f"purchased-part pocket, omit it, or make it at least one {_enc.wall:g} mm wall")
    return tuple(reliefs)


def _minimum_depth_reliefs(reliefs: tuple) -> tuple:
    """Deepen only the explicitly reviewed singleton pockets to one printable wall."""
    face = _enc.back_top_ceiling_face()
    roof = face + _enc.wall
    return tuple(
        row[:5] + (max(row[5], roof),)
        if row[0] in CEILING_RELIEF_MIN_DEPTH_BODIES else row
        for row in reliefs
    )


def _asse_end_reliefs(reliefs: tuple, cradle) -> tuple:
    """The ASSE chain's pockets ended on the anchor's own end face where they would run on less
    than one `wall` past it.

    A pocket is one fitting's section box plus `CEILING_RELIEF_PLAN_SLIP`, and the Multiplex
    body's box takes its barrel's plan the body's whole length, over the inlet thread the
    coupling swallows too. Past the anchor's last section the coupling's own pocket carries on
    east of the barrel's plan, so west of it that box ends in a slot narrower than a wall between
    the anchor's end face and the box's own end. The steps hold the barrel to `ASSE_STEP_SLIP`
    along the axis, so an end clips onto the anchor's end face only where the section in that
    pocket stops that travel plus one `ASSE_SEAT_SLIP` short of the face."""
    if not cradle:
        return reliefs
    sections = cradle[1]
    fore, aft = sections[0][0], sections[-1][1]
    keep = ASSE_STEP_SLIP + ASSE_SEAT_SLIP
    out = []
    for name, x0, x1, y0, y1, roof in reliefs:
        if name == "asse1022-assembly":
            if 0.0 < y1 - aft < _enc.wall and y1 - CEILING_RELIEF_PLAN_SLIP + keep <= aft:
                y1 = aft
            if 0.0 < fore - y0 < _enc.wall and y0 + CEILING_RELIEF_PLAN_SLIP - keep >= fore:
                y0 = fore
        out.append((name, x0, x1, y0, y1, roof))
    return tuple(out)


def _connected_reliefs(reliefs: tuple) -> tuple:
    """Append a connector across each sub-wall gap between a named pocket pair.

    Source extents are immutable. A connector exists only when exactly one plan axis has a gap
    narrower than a wall and the other overlaps; it spans the overlap and enters each pocket by
    `CEILING_RELIEF_CONNECTOR_ENTRY`. Unnamed pockets retain their own extents.
    Calling this twice returns the same tuples, so a connector cannot become the source of a
    transitive enlargement."""
    source = tuple(reliefs)
    out = list(source)
    keys = {
        (p[0], *(round(value / _enc.stated_bound_tol) for value in p[1:]))
        for p in source
    }
    for left, right in CEILING_RELIEF_CONNECTOR_PAIRS:
        left_rows = tuple(row for row in source if row[0] == left)
        right_rows = tuple(row for row in source if row[0] == right)
        if not left_rows and not right_rows:
            continue
        candidates = []
        for p in left_rows:
            for q in right_rows:
                x_overlap = min(p[2], q[2]) - max(p[1], q[1])
                y_overlap = min(p[4], q[4]) - max(p[3], q[3])
                x_gap = max(q[1] - p[2], p[1] - q[2])
                y_gap = max(q[3] - p[4], p[3] - q[4])
                separated_x = x_gap > _enc.stated_bound_tol
                separated_y = y_gap > _enc.stated_bound_tol
                if separated_x == separated_y:
                    continue
                if separated_x:
                    if x_gap >= _enc.wall or y_overlap <= _enc.stated_bound_tol:
                        continue
                    x0 = min(p[2], q[2]) - CEILING_RELIEF_CONNECTOR_ENTRY
                    x1 = max(p[1], q[1]) + CEILING_RELIEF_CONNECTOR_ENTRY
                    y0, y1 = max(p[3], q[3]), min(p[4], q[4])
                else:
                    if y_gap >= _enc.wall or x_overlap <= _enc.stated_bound_tol:
                        continue
                    x0, x1 = max(p[1], q[1]), min(p[2], q[2])
                    y0 = min(p[4], q[4]) - CEILING_RELIEF_CONNECTOR_ENTRY
                    y1 = max(p[3], q[3]) + CEILING_RELIEF_CONNECTOR_ENTRY
                candidates.append((f"{left}/{right} connector", x0, x1, y0, y1,
                                   min(p[5], q[5])))
        unique = []
        pair_keys = set()
        for connector in candidates:
            key = (connector[0], *(round(value / _enc.stated_bound_tol)
                                   for value in connector[1:]))
            if key not in pair_keys:
                pair_keys.add(key)
                unique.append(connector)
        for connector in unique:
            key = (connector[0], *(round(value / _enc.stated_bound_tol)
                                   for value in connector[1:]))
            if key not in keys:
                keys.add(key)
                out.append(connector)
    return tuple(out)


WEDGE_CLEAR = 1.0


WELL_COLUMNS = (
    (+1, 322.25),        # the five-Wago power row on the +X wall
    (-1, 270.0),         # the reeds/sensors cluster on the −X wall
)


KEPT_WEDGES = ()


def stand_anchors(stations) -> tuple:
    """Each anchor station with its `stand` entry (`enclosure._tube_anchors`): per end web,
    `(plane, None)` where the site states a `column` — back-top's ceiling face, which that end
    continues to over the flank's whole section — and None where it states a `corbel`. The
    statement is the site's (`TUBE_ANCHOR_END_FORMS`, `BODY_ANCHOR_END_FORMS`); nothing here
    reads the pack, so a column stands because someone decided it should and not because the
    air above the web happened to be free. A station outside back-top's band is passed through
    as its four geometric entries.

    A stated `column` on an end whose rib has no column to give — flanks level, tube along the
    build axis, print-down flank facing away from the bed — raises. A statement the geometry
    cannot honour is a statement to correct, never one to quietly downgrade to a corbel."""
    up = _enc.print_up("back", "top")
    roots, lane = _enc.back_top_frames()
    face_z = _enc.back_top_ceiling_face()
    out = []
    for station in stations:
        end_forms = tuple(station[4]) if len(station) > 4 else ("corbel", "corbel")
        if len(end_forms) != 2 or any(form not in ANCHOR_END_FORMS for form in end_forms):
            raise ValueError(
                f"stand_anchors: end forms are {end_forms!r}; each end must be one of "
                f"{ANCHOR_END_FORMS}.")
        st = tuple(station[:4])
        # A capped station keeps its closure behind its `stand` (`enclosure.anchor_capped`).
        capped = tuple(station[5:6]) == ("cap",)
        if not _enc.back_top_owns(st[0]):
            if capped:
                raise ValueError(
                    f"stand_anchors: the anchor at ({st[0][0]:.2f}, {st[0][1]:.2f}, "
                    f"{st[0][2]:.2f}) is capped and stands outside back-top's band; the box's "
                    f"anchor caps close ribs back-top builds.")
            out.append(st)
            continue
        columns = _enc.tube_anchor_end_columns(st, roots, lane, up, face_z)
        stand = []
        for end, (form, column) in enumerate(zip(end_forms, columns), 1):
            if form == "corbel":
                stand.append(None)
                continue
            if column is None:
                raise ValueError(
                    f"stand_anchors: the anchor at ({st[0][0]:.2f}, {st[0][1]:.2f}, "
                    f"{st[0][2]:.2f}) states `column` on end {end}, and that rib has no column "
                    f"to the print-bed face — its site should say `corbel`.")
            stand.append((face_z, None))
        out.append(st + (tuple(stand),) + (("cap",) if capped else ()))
    return tuple(out)


def stand_wells(stations) -> tuple:
    """Each well station with its `column` entry (`enclosure._side_wells`): whether its row's
    tower continues to `clear_z` as a column, stated at `WELL_COLUMNS` and not searched for. A
    station with no `clear_z` has no plane to stand on and is passed through; a stated row that
    has no `clear_z` is an error, as is a stated row no well matches."""
    rows = {}
    for st in stations:
        side, _sy, sz, _size, clear_z, _roof = st[:6]
        rows.setdefault((side, round(sz, 4)), []).append(clear_z)
    for key in WELL_COLUMNS:
        if key not in rows:
            raise ValueError(
                f"WELL_COLUMNS names the row {key}, and no well stands there; the row it was "
                f"written for has moved or gone.")
        if any(c is None for c in rows[key]):
            raise ValueError(
                f"WELL_COLUMNS names the row {key}, and its wells have no plane to stand a "
                f"column on. A row off the ceiling-down piece cannot carry one.")
    return tuple(
        tuple(st[:6]) + ((True,) if (st[0], round(st[2], 4)) in WELL_COLUMNS else
                         ((False,) if st[4] is not None else ()))
        for st in stations)


_PLAN_INSET = 0.02


def authored_anchor_corbels(stations) -> tuple:
    """Named rooms enclosing tube-anchor end webs whose site specifies an ordinary corbel."""
    roots, lane = _enc.back_top_frames()
    up = _enc.print_up("back", "top")
    rooms = []
    for station in stations:
        if len(station) < 5:
            continue
        forms = tuple(station[4])
        bounds = _enc.tube_anchor_end_corbel_bounds(station, roots, lane, up)
        for end, (form, bound) in enumerate(zip(forms, bounds), 1):
            if form != "corbel" or bound is None:
                continue
            mid = station[0]
            rooms.append((
                f"tube anchor at ({mid[0]:.2f}, {mid[1]:.2f}, {mid[2]:.2f}), end {end}",
                bound,
                "the anchor site specifies its ordinary full-width 45-degree corbel",
            ))
    return tuple(rooms)


def front_flank_reliefs_fine(reference, *, transform=None):
    """F/I flank pockets from explicit fine entries and their raw placed bounds.

    `reference` carries the fine model, ordered summary rows and `raw_bounds`;
    it supplies no shape API. The same source boxes clip the actual bodies.
    """
    import _assembly_model

    entries = {}
    for index, row in enumerate(reference.summaries):
        name = row['name']
        stem, _, tail = name.rpartition('/')
        name = stem if tail.isdigit() else name
        entries.setdefault(name, []).append(index)
    air = _card.CLEARANCE_FLOOR
    plans = []
    def tool(lower, upper, lo, hi):
        origin = (lo, lower[1] - 1.0, lower[2] - 1.0)
        span = (hi - lo, upper[1] - lower[1] + 2.0, upper[2] - lower[2] + 2.0)
        return [list(origin), [p + d for p, d in zip(origin, span)]]
    for name, valve in (("coil-v-f", "valve-v-f"), ("coil-v-i", "valve-v-i")):
        lower, upper = reference.raw_bounds[name]
        side = 1.0 if (lower[0] + upper[0]) / 2.0 > 0.0 else -1.0
        face = _enc.front_top_flank_face()[1 if side > 0 else 0]
        lo, hi = ((face - air, upper[0] + 1.0) if side > 0
                  else (lower[0] - 1.0, face + air))
        if hi <= lo:
            continue
        plans.append({'name':name, 'valve':valve, 'side':side, 'face':face,
                      'request':{'indices':entries[name], 'box':tool(lower, upper, lo, hi)}})
    readings = _assembly_model.box_commons(reference.model, [p['request'] for p in plans],
                                           transform=transform)
    active = []
    valves = []
    for plan, reading in zip(plans, readings):
        if reading['raw']['min'] is None:
            continue
        plan = {**plan, 'coil':reading['raw']}
        lower, upper = reference.raw_bounds[plan['valve']]
        face, side = plan['face'], plan['side']
        lo, hi = ((face, upper[0] + 1.0) if side > 0 else (lower[0] - 1.0, face))
        if hi > lo:
            valves.append((len(active), {'indices':entries[plan['valve']],
                                         'box':tool(lower, upper, lo, hi)}))
        active.append(plan)
    readings = _assembly_model.box_commons(reference.model, [request for _owner, request in valves],
                                           transform=transform)
    for (owner, _request), reading in zip(valves, readings):
        if reading['raw']['min'] is not None:
            active[owner]['crossing'] = reading['raw']
    pockets = []
    for plan in active:
        bounds = [plan['coil']]
        if 'crossing' in plan:
            bounds.append(plan['crossing'])
        xs = [row[key][0] for row in bounds for key in ('min', 'max')]
        ys = [row[key][1] for row in bounds for key in ('min', 'max')]
        zs = [row[key][2] for row in bounds for key in ('min', 'max')]
        floor = max(xs) + air if plan['side'] > 0 else min(xs) - air
        if abs(floor) > min(abs(x) for x in _enc.interior_x()):
            raise ValueError(f"{plan['name']} clearance would enter the nominal enclosure wall")
        face = plan['face']
        pockets.append((plan['name'], min(face, floor), max(face, floor),
                        min(ys) - air, max(ys) + air, min(zs) - air, max(zs) + air))
    return tuple(pockets)


def above_core_ceiling_reliefs():
    """Plain roof pockets retain the selected three-millimetre outer skin."""
    pockets = _above.specification()['ceiling_pockets']['pockets']
    return tuple((p['name'], p['xmin'], p['xmax'], p['ymin'], p['ymax'], p['zmax'])
                 for p in pockets)


def funnel_centre(box):
    """The collar and drain centre, on the drop-in frame's datum (`funnel_frame.center_y`)
    and not the centre of its plan."""
    return ((box.inner[0] + box.inner[1]) / 2, _funnel_frame.center_y)


COVER_ORIGIN = ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))


RIDGE_REACH = 60.0


SEAT_TOL = 1e-6


NOT_A_BODY = ("tube-", "turn-", "step-", "stub-", "enclosure-")


def seat_off(seat) -> float:
    """The worst a seat's own rule missed by, in mm — 0 when every face and every mouth landed
    where the rule named."""
    if "station" in seat.rule:
        return max(abs(g - w) for g, w in zip(seat.got["station"], seat.rule["station"]))
    return max((abs(seat.got[k] - v) for k, v in seat.rule.items() if k in seat.got),
               default=0.0)
