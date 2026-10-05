"""Taprite 3741 CGA-320 CO2 regulator — the primary regulator that ships with the appliance,
set at the factory to 75 psi.

It stands on the customer's own CO2 cylinder and is the only thing on this machine the customer
threads onto anything. Its CGA-320 nut pulls down on the cylinder valve. Its outlet is the gray
acetal PI010822S the factory threads into the body's 1/4" NPT port in place of Taprite's flare
fitting, and the red 1/4" tether to the CO2 bulkhead on the +Y wall of back-top is pushed into
that at the factory too (`ledger/bom.md` §4). Regulator and tether ship as one piece.

THE CUSTOMER SETS NOTHING ON IT. The pressure adjustment is a slotted screw out the front of the
black bonnet, under a jam nut: acceptance step 1 turns it to `FACTORY_SET_PSI` on the regulator's
own upper gauge, locks the nut and paint-marks the pair, and it ships at that setting. There is
no knob and no outlet shutoff; the cylinder valve opens and closes the gas.

Two dials, which do not read the same thing: the +X dial reads the cylinder, 0–2000 psi, with a
green band where a cylinder with liquid CO2 in it reads and a red band at the empty end; the +Z
dial reads what goes out to the appliance, 0–160 psi. Both are drawn with their scales and their
needles at rest on zero, which is the state the part ships in.

Where the figures come from
---------------------------
Taprite's own sales drawing (3741_SALES rev C, drawn 1:2: 7" wide, 6" tall, 4.3" deep) and its
parts breakdown (3741 REGULATOR ASSEMBLY rev C, 10-2010), read at 150 px to the real inch. What is
standardised is taken at its standard — the CGA-320 nut's 1-1/8" hex and 0.825"-14 thread, the
PI010822S's nominal 1/4" push-fit envelope. `README.md` says which figure is which.

Coordinate frame
----------------
The frame the regulator hangs in once it is on the cylinder:

- **+Y** out of the body's face toward the customer — the bonnet and its adjusting screw.
- **+Z** up — the outlet-pressure dial. **−Z** down — the outlet and its gray push-fit.
- **−X** the inlet axis, out toward the cylinder — the CGA-320 nut.
- **+X** the cylinder-contents dial.

Origin where the bonnet's axis crosses the inlet and outlet axes. Standing in front of it, the
customer sees the cylinder on their right, the contents dial on their left, the outlet dial above,
the outlet below and the safety blow-off on the upper right of the body.

Run:
    tools/cad-venv/bin/python hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly, import_step
from _materials import (M_BRASS, M_CHROME_PLATE, M_GAUGE_BLACK, M_GAUGE_GREEN, M_GAUGE_RED,
                        M_GAUGE_WHITE, M_JG_GREY_ACETAL, M_MOULDED_BLACK, M_NICKEL_PLATE)

STEP = _here.parent / "taprite-3741-regulator.step"

# --- the setting it ships at ---------------------------------------------------
FACTORY_SET_PSI = 75.0           # acceptance step 1; the in-machine WR1105 holds 3 bar below it
RELIEF_PSI = 130.0               # the safety blow-off, 130 ± 4 psi on Taprite's drawing

# --- the standards ----------------------------------------------------------
# CGA-320 is the connection every USA CO2 beverage cylinder presents: a 0.825"-14 NGO-RH male
# thread on the valve, and a female nut on the regulator that pulls a nipple down onto the
# valve's own face with a nylon washer between them. The nut takes a 1-1/8" wrench.
CGA320_NUT_FLATS = 25.4 * 1.125
CGA320_THREAD_D = 25.4 * 0.825
CGA320_NUT_LENGTH = 25.4
CGA320_NIPPLE_D = 15.9          # the nose that seats on the cylinder valve, inside the nut

# The outlet push-fit: John Guest PI010822S, gray acetal, at the repository's nominal 1/4"
# male-connector envelope (`reference/jg-pp010822e`). Its NPT shank is inside the body's port.
PTC_COLLET_D = 14.0
PTC_COLLET_LENGTH = 13.5
PTC_HEX_ACROSS_CORNERS = 16.5
PTC_HEX_LENGTH = 5.0
NPT_D = 13.7                     # 1/4" NPT major, for the turn of thread left showing
TUBE_D = 6.35                    # the red 1/4" tether it takes

# --- the gauges ----------------------------------------------------------------
# Both are 2" dials in a knurled 2-1/4" bezel, face toward the customer.
DIAL_D = 51.0                    # the printed disc, its rim under the bezel
WINDOW_D = 48.5                  # what the bezel leaves of it
CASE_D = 58.5
CASE_DEPTH = 28.0
GAUGE_FACE_Y = 14.0              # where the dial's own front plane stands
BEZEL_PROUD = 3.0                # how far the bezel stands over the dial
OUTLET_REACH = 67.0              # body centre to the outlet dial's centre, up
TANK_REACH = 65.0                # body centre to the contents dial's centre, out +X
GAUGE_STEM_D = 13.7              # each gauge's 1/4" NPT stem where it leaves the body
GAUGE_BLOCK_W = 14.0             # the wrench block under each case
GAUGE_BLOCK_LENGTH = 9.0

# --- the body ---------------------------------------------------------------
BODY_D = 44.0                    # the brass body behind the bonnet
BODY_BACK_Y = -11.0
BODY_FRONT_Y = 13.5
PORT_BOSS_D = 18.0               # each port's boss, standing to `PORT_FACE_R`
PORT_FACE_R = 23.0

# The black zinc bonnet: the diaphragm flange, a hex neck, and the round nose the adjusting
# screw runs out of.
FLANGE_D = 50.0
FLANGE_FRONT_Y = 25.4
FLANGE_EDGE_R = 2.0
NECK_FLATS = 31.0
NECK_FRONT_Y = 39.0
NOSE_D = 29.0
NOSE_FRONT_Y = 62.3
NOSE_CHAMFER = 2.0
# The adjustment: a 3/8" slotted screw under a jam nut, locked at the factory.
JAM_NUT_FLATS = 25.4 * 0.5
JAM_NUT_FRONT_Y = 70.0
SCREW_D = 25.4 * 0.375
SCREW_TIP_Y = 92.3
SLOT_W = 1.6
SLOT_DEPTH = 3.0

INLET_AXIS = (-1.0, 0.0, 0.0)    # out toward the cylinder, on the customer's right
TANK_AXIS = (1.0, 0.0, 0.0)      # the contents dial, on the customer's left
INLET_NIPPLE_D = 14.0
INLET_NUT_NEAR = 60.0            # the nut's inboard face, run up onto the valve
INLET_NUT_FACE = INLET_NUT_NEAR + CGA320_NUT_LENGTH
INLET_NIPPLE_END = INLET_NUT_FACE - 9.0   # the nose, inside the nut, on the valve's face

OUTLET_THREAD_Z = -PORT_FACE_R - 1.0      # the turn of NPT left showing below the port face
OUTLET_HEX_Z = OUTLET_THREAD_Z - PTC_HEX_LENGTH
OUTLET_MOUTH_Z = OUTLET_HEX_Z - PTC_COLLET_LENGTH

# The safety blow-off, on the body's upper right: Taprite's own fitting, its vent holes in its
# end face. It is not a pull-ring valve and nothing in the guides asks the customer to touch it.
BLOWOFF_BEARING_DEG = 135.0      # in the XZ plane, CCW from +X: up and out toward the inlet
BLOWOFF_ROOT_R = 18.0
BLOWOFF_BODY_D = 11.0
BLOWOFF_BODY_R = 30.0
BLOWOFF_CAP_D = 13.0
BLOWOFF_CAP_R = 37.0
BLOWOFF_VENT_D = 1.6

# --- what each dial says ----------------------------------------------------
# A dial's scale runs 270° clockwise from its zero at the lower left. Each dial carries psi on its
# outer ring in black and bar on its inner ring in red.
DIAL_ZERO_DEG = 225.0
DIAL_SWEEP_DEG = 270.0
TANK_FULL_PSI = 2000.0
OUTLET_FULL_PSI = 160.0
# The contents dial's bands, in psi: red at the empty end, green where a cylinder still holding
# liquid CO2 reads (its vapour pressure, about 850 psi at room temperature). Placed off
# Taprite's drawing and the product photograph; the received part fixes them.
TANK_BANDS = (((0.0, 300.0), M_GAUGE_RED), ((600.0, 1000.0), M_GAUGE_GREEN))


def _ring_spec(full, major, minor, labels):
    """One printed scale: its full-scale value, its tick steps and the values it letters."""
    return {"full": full, "major": major, "minor": minor, "labels": labels}


TANK_DIAL = {
    "outer": _ring_spec(TANK_FULL_PSI, 500.0, 100.0, (500, 1000, 1500, 2000)),
    "inner": _ring_spec(TANK_FULL_PSI / 14.5038, 20.0, 10.0, (40, 60, 80, 100, 120)),
    "units": ("psi", "bar"),
    "stamp": "TAPRITE",
    "bands": TANK_BANDS,
}
OUTLET_DIAL = {
    "outer": _ring_spec(OUTLET_FULL_PSI, 20.0, 5.0, (20, 40, 60, 80, 100, 120, 140, 160)),
    "inner": _ring_spec(OUTLET_FULL_PSI / 14.5038, 2.0, 1.0, (2, 4, 6, 8, 10)),
    "units": ("psi", "bar"),
    "stamp": "TAPRITE",
    "bands": (),
}

# Where each ring sits on the face of a 2" dial.
OUTER_NUMERAL_R = 20.6
OUTER_TICK_OUT_R = 23.6
OUTER_TICK_MAJOR_R = 20.0 + 2.2
OUTER_TICK_MINOR_R = 22.4
INNER_ARC_R = 14.6
INNER_TICK_MAJOR_R = 12.2
INNER_TICK_MINOR_R = 13.3
INNER_NUMERAL_R = 10.3
UNIT_UPPER_R = 6.9
UNIT_LOWER_R = 10.2
STAMP_R = 5.2
NUMERAL_SIZE = 3.0
STAMP_SIZE = 2.4
UNIT_SIZE = 2.8
MAJOR_TICK_W = 0.8
MINOR_TICK_W = 0.45
PRINT_T = 0.6
BAND_T = 0.25                    # the bands go down first and the scale is printed over them
NEEDLE_R = 19.0
NEEDLE_TAIL_R = 4.6
NEEDLE_W = 1.3
HUB_DIAL_D = 4.6
BAND_NEAR_R = 16.0
BAND_FAR_R = 23.6

# A dial faces +Y and is read from +Y, so its own right hand is world −X. This is the plane every
# mark on it is drawn on: the mark's `(u, v)` are its right and its up as the customer sees them.
_dial_plane = cq.Plane(origin=(0.0, 0.0, 0.0), xDir=(-1.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0))


# --- the stations the rest of the world reaches ------------------------------

def inlet() -> tuple:
    """The CGA-320 nut's outer face, and the axis it runs onto the cylinder valve along:
    `(position, outward axis)`. The nipple inside it seats on the valve's own face with the
    supplied nylon washer between."""
    return (-INLET_NUT_FACE, 0.0, 0.0), INLET_AXIS


def outlet() -> tuple:
    """The PI010822S's push-fit mouth, where the red tether goes in: `(position, outward
    axis)`."""
    return (0.0, 0.0, OUTLET_MOUTH_Z), (0.0, 0.0, -1.0)


def adjustment() -> tuple:
    """The slotted adjusting screw's tip and the axis it turns about — set and locked at the
    factory, and what a picture points at to say "leave this alone"."""
    return (0.0, SCREW_TIP_Y, 0.0), (0.0, 1.0, 0.0)


def relief() -> tuple:
    """The safety blow-off's vented end face."""
    x, z = _bearing(BLOWOFF_CAP_R)
    return (x, 0.0, z), _bearing(1.0, as_axis=True)


def tank_dial() -> tuple:
    """The cylinder-contents dial's centre and the direction it is read from."""
    return (TANK_REACH, GAUGE_FACE_Y, 0.0), (0.0, 1.0, 0.0)


def outlet_dial() -> tuple:
    """The outlet-pressure dial's centre and the direction it is read from."""
    return (0.0, GAUGE_FACE_Y, OUTLET_REACH), (0.0, 1.0, 0.0)


def stations() -> dict:
    """Everything a picture or a neighbour points at, under the name it is pointed at by."""
    return {"inlet": inlet(), "outlet": outlet(), "adjustment": adjustment(),
            "relief": relief(), "tank-dial": tank_dial(), "outlet-dial": outlet_dial()}


# --- the solid ---------------------------------------------------------------

def _bearing(r: float, as_axis: bool = False):
    """A point on the blow-off's axis at radius `r`, in the XZ plane."""
    a = math.radians(BLOWOFF_BEARING_DEG)
    x, z = r * math.cos(a), r * math.sin(a)
    return (x, 0.0, z) if as_axis else (x, z)


def _cyl(d: float, axis, near: float, far: float) -> cq.Solid:
    """A cylinder of `d` on `axis`, between two stations measured from the origin."""
    direction = cq.Vector(*axis)
    return cq.Solid.makeCylinder(d / 2.0, far - near, direction.multiply(near), direction)


def _hex(flats: float, axis, near: float, far: float) -> cq.Solid:
    """A wrench hex of `flats` across, on `axis`, between two stations."""
    corners = flats / math.cos(math.radians(30.0))
    prism = cq.Workplane("XY").polygon(6, corners).extrude(far - near).val()
    up = cq.Vector(0, 0, 1)
    direction = cq.Vector(*axis).normalized()
    turn = up.cross(direction)
    # AN ARM POINTING STRAIGHT DOWN HAS NO CROSS PRODUCT WITH UP, and a prism left unturned on
    # that arm runs back through the body it hangs off. Any perpendicular carries the half turn.
    if turn.Length < 1e-9:
        turn = cq.Vector(1, 0, 0) if up.dot(direction) < 0 else None
    if turn is not None:
        prism = prism.rotate(cq.Vector(0, 0, 0), turn,
                             math.degrees(math.acos(max(-1.0, min(1.0, up.dot(direction))))))
    return prism.translate(direction.multiply(near))


def _block(width: float, axis, near: float, far: float) -> cq.Solid:
    """A square wrench block of `width` on `axis`, between two stations."""
    direction = cq.Vector(*axis).normalized()
    across = direction.cross(cq.Vector(0, 1, 0)).normalized()
    plane = cq.Plane(origin=direction.multiply(near).toTuple(), xDir=across.toTuple(),
                     normal=direction.toTuple())
    return cq.Workplane(plane).rect(width, width).extrude(far - near).val()


def build_body() -> cq.Solid:
    """The brass: the body behind the bonnet, its four port bosses, the inlet nipple, each
    gauge's stem and block, and the blow-off's root."""
    solid = _cyl(BODY_D, (0.0, 1.0, 0.0), BODY_BACK_Y, BODY_FRONT_Y)
    for axis in ((0.0, 0.0, 1.0), TANK_AXIS, INLET_AXIS, (0.0, 0.0, -1.0)):
        boss = _cyl(PORT_BOSS_D, axis, 0.0, PORT_FACE_R)
        solid = solid.fuse(boss)
    solid = solid.fuse(_cyl(INLET_NIPPLE_D, INLET_AXIS, PORT_FACE_R, INLET_NIPPLE_END))
    for axis, reach in (((0.0, 0.0, 1.0), OUTLET_REACH), (TANK_AXIS, TANK_REACH)):
        block_far = reach - CASE_D / 2.0 + 1.0
        solid = solid.fuse(_cyl(GAUGE_STEM_D, axis, PORT_FACE_R, block_far - GAUGE_BLOCK_LENGTH))
        solid = solid.fuse(_block(GAUGE_BLOCK_W, axis, block_far - GAUGE_BLOCK_LENGTH, block_far))
    bearing = _bearing(1.0, as_axis=True)
    solid = solid.fuse(_cyl(BLOWOFF_BODY_D + 2.0, bearing, 0.0, BLOWOFF_ROOT_R + 4.0))
    return solid.clean()


def build_blowoff() -> cq.Solid:
    """Taprite's safety blow-off: a brass body and a cap with its vents in the end face."""
    bearing = _bearing(1.0, as_axis=True)
    body = _cyl(BLOWOFF_BODY_D, bearing, BLOWOFF_ROOT_R, BLOWOFF_BODY_R)
    cap = _cyl(BLOWOFF_CAP_D, bearing, BLOWOFF_BODY_R, BLOWOFF_CAP_R)
    solid = body.fuse(cap)
    direction = cq.Vector(*bearing)
    seed = cq.Vector(0, 1, 0)
    across = direction.cross(seed).normalized()
    for i in range(4):
        a = math.pi / 4.0 + i * math.pi / 2.0
        offset = across.multiply(3.6 * math.cos(a)).add(seed.multiply(3.6 * math.sin(a)))
        start = direction.multiply(BLOWOFF_CAP_R - 1.2).add(offset)
        solid = solid.cut(cq.Solid.makeCylinder(BLOWOFF_VENT_D / 2.0, 2.0, start, direction))
    centre = direction.multiply(BLOWOFF_CAP_R - 1.2)
    return solid.cut(cq.Solid.makeCylinder(BLOWOFF_VENT_D / 2.0, 2.0, centre, direction)).clean()


def build_bonnet() -> cq.Solid:
    """The black zinc bonnet: diaphragm flange, hex neck and the round nose."""
    flange = (cq.Workplane("XZ", origin=(0.0, BODY_FRONT_Y, 0.0)).circle(FLANGE_D / 2.0)
              .extrude(-(FLANGE_FRONT_Y - BODY_FRONT_Y)).edges("%Circle")
              .fillet(FLANGE_EDGE_R).val())
    neck = _hex(NECK_FLATS, (0.0, 1.0, 0.0), FLANGE_FRONT_Y, NECK_FRONT_Y)
    nose = (cq.Workplane("XZ", origin=(0.0, NECK_FRONT_Y, 0.0)).circle(NOSE_D / 2.0)
            .extrude(-(NOSE_FRONT_Y - NECK_FRONT_Y)).faces(">Y").edges()
            .chamfer(NOSE_CHAMFER).val())
    bonnet = flange.fuse(neck).fuse(nose)
    return bonnet.cut(_cyl(SCREW_D + 0.4, (0.0, 1.0, 0.0), NOSE_FRONT_Y - 12.0,
                           NOSE_FRONT_Y + 0.1)).clean()


def build_adjustment() -> cq.Solid:
    """The 3/8" slotted adjusting screw and the jam nut that locks it where the factory set it."""
    nut = _hex(JAM_NUT_FLATS, (0.0, 1.0, 0.0), NOSE_FRONT_Y, JAM_NUT_FRONT_Y)
    screw = _cyl(SCREW_D, (0.0, 1.0, 0.0), NOSE_FRONT_Y - 12.0, SCREW_TIP_Y)
    slot = cq.Solid.makeBox(SLOT_W, SLOT_DEPTH + 0.1, SCREW_D + 2.0,
                            cq.Vector(-SLOT_W / 2.0, SCREW_TIP_Y - SLOT_DEPTH,
                                      -SCREW_D / 2.0 - 1.0))
    return nut.fuse(screw.cut(slot)).clean()


def build_inlet_nut() -> cq.Solid:
    """The CGA-320 nut: a 1-1/8" hex, bored the cylinder valve's 0.825" thread, that turns
    freely on the nipple standing inside it."""
    nut = _hex(CGA320_NUT_FLATS, INLET_AXIS, INLET_NUT_NEAR, INLET_NUT_FACE)
    nut = nut.cut(_cyl(CGA320_THREAD_D, INLET_AXIS, INLET_NIPPLE_END, INLET_NUT_FACE + 0.1))
    return nut.cut(_cyl(CGA320_NIPPLE_D, INLET_AXIS,
                        INLET_NUT_NEAR - 0.1, INLET_NIPPLE_END)).clean()


def build_outlet_connector() -> cq.Solid:
    """The PI010822S in the outlet port: the turn of NPT left showing, the wrench hex and the
    push-fit collet the tether goes into."""
    down = (0.0, 0.0, -1.0)
    thread = _cyl(NPT_D, down, PORT_FACE_R, -OUTLET_THREAD_Z)
    hex_flats = PTC_HEX_ACROSS_CORNERS * math.cos(math.radians(30.0))
    hexagon = _hex(hex_flats, down, -OUTLET_THREAD_Z, -OUTLET_HEX_Z)
    collet = _cyl(PTC_COLLET_D, down, -OUTLET_HEX_Z, -OUTLET_MOUTH_Z)
    mouth = _cyl(TUBE_D, down, -OUTLET_MOUTH_Z - 4.0, -OUTLET_MOUTH_Z + 0.1)
    return thread.fuse(hexagon).fuse(collet).cut(mouth).clean()


# --- a dial ------------------------------------------------------------------

def _scale_deg(value: float, full: float) -> float:
    """Where a reading stands on the face, in degrees CCW from the customer's own right."""
    return DIAL_ZERO_DEG - DIAL_SWEEP_DEG * value / full


def _at(r: float, deg: float) -> tuple:
    """A point on the face at `(radius, angle)`, in the dial plane's own `(u, v)`."""
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def _tick(near_r: float, far_r: float, deg: float, width: float, plane) -> cq.Shape:
    """One radial mark on the face."""
    a = math.radians(deg)
    along = (math.cos(a), math.sin(a))
    across = (-math.sin(a) * width / 2.0, math.cos(a) * width / 2.0)
    corners = [(near_r * along[0] + across[0], near_r * along[1] + across[1]),
               (far_r * along[0] + across[0], far_r * along[1] + across[1]),
               (far_r * along[0] - across[0], far_r * along[1] - across[1]),
               (near_r * along[0] - across[0], near_r * along[1] - across[1])]
    return plane.polyline(corners + corners[:1]).wire().extrude(PRINT_T).val()


def _steps(step: float, full: float):
    """Every reading a tick stands at, zero and full scale included."""
    n = int(math.floor(full / step + 1e-9))
    return [i * step for i in range(n + 1)]


def _numeral(value: float, plane, r: float, deg: float, size: float) -> cq.Shape:
    """One lettered reading, standing upright the way the dial prints it."""
    u, v = _at(r, deg)
    return plane.center(u, v).text(f"{value:g}", size, PRINT_T, combine=False).val()


def _ring_marks(spec: dict, plane, numeral_r, major_r, minor_r, out_r) -> tuple:
    """One printed scale as `(the marks, the numerals)`, each a compound of its own bodies."""
    full = spec["full"]
    marks = [_tick(minor_r, out_r, _scale_deg(v, full), MINOR_TICK_W, plane)
             for v in _steps(spec["minor"], full)]
    marks += [_tick(major_r, out_r, _scale_deg(v, full), MAJOR_TICK_W, plane)
              for v in _steps(spec["major"], full)]
    numerals = [_numeral(v, plane, numeral_r, _scale_deg(v, full), NUMERAL_SIZE)
                for v in spec["labels"]]
    return cq.Compound.makeCompound(marks), cq.Compound.makeCompound(numerals)


def _needle(deg: float, plane) -> cq.Shape:
    """The pointer: a tapered blade out to the scale and a stub counterweight behind the hub."""
    a = math.radians(deg)
    along = (math.cos(a), math.sin(a))
    across = (-math.sin(a), math.cos(a))

    def at(radius, half):
        return (radius * along[0] + half * across[0], radius * along[1] + half * across[1])

    corners = [at(NEEDLE_R, 0.35), at(1.5, NEEDLE_W / 2.0), at(-NEEDLE_TAIL_R, 1.2),
               at(-NEEDLE_TAIL_R, -1.2), at(1.5, -NEEDLE_W / 2.0), at(NEEDLE_R, -0.35)]
    return plane.polyline(corners + corners[:1]).wire().extrude(0.8).val()


def build_dial(spec: dict, centre) -> list:
    """One gauge, standing at `centre` and read from +Y — `[(shape, name, material)]`.

    The case is a closed chromed cup and the bezel round its mouth leaves `WINDOW_D` of the dial
    showing; everything the customer reads stands on that disc. The lens over it and the works
    behind it are not modelled."""
    cx, _cy, cz = centre
    face_y = GAUGE_FACE_Y
    front_y = face_y + BEZEL_PROUD

    def plane(offset):
        return cq.Workplane(_dial_plane).workplane(offset=offset).center(-cx, cz)

    case = (_cyl(CASE_D, (0.0, 1.0, 0.0), front_y - CASE_DEPTH, front_y)
            .cut(_cyl(DIAL_D + 0.2, (0.0, 1.0, 0.0), face_y - 1.5, face_y + 0.4))
            .cut(_cyl(WINDOW_D, (0.0, 1.0, 0.0), face_y + 0.4, front_y + 0.1))
            .translate((cx, 0.0, cz)))
    dial = _cyl(DIAL_D, (0.0, 1.0, 0.0), face_y - 1.0, face_y).translate((cx, 0.0, cz))

    marks = plane(face_y)
    outer_ticks, outer_numerals = _ring_marks(spec["outer"], marks, OUTER_NUMERAL_R,
                                              OUTER_TICK_MAJOR_R, OUTER_TICK_MINOR_R,
                                              OUTER_TICK_OUT_R)
    inner_ticks, inner_numerals = _ring_marks(spec["inner"], marks, INNER_NUMERAL_R,
                                              INNER_TICK_MAJOR_R, INNER_TICK_MINOR_R,
                                              INNER_ARC_R)
    upper, lower = spec["units"]
    black = [outer_ticks, outer_numerals,
             _needle(DIAL_ZERO_DEG, plane(face_y + PRINT_T)),
             plane(face_y).center(0.0, -UNIT_UPPER_R).text(upper, UNIT_SIZE, PRINT_T,
                                                          combine=False).val()]
    if spec["stamp"]:
        black.append(plane(face_y).center(0.0, STAMP_R).text(spec["stamp"], STAMP_SIZE, PRINT_T,
                                                             combine=False).val())
    red = [inner_ticks, inner_numerals,
           plane(face_y).circle(INNER_ARC_R).circle(INNER_ARC_R - 0.3).extrude(PRINT_T).val(),
           plane(face_y).center(0.0, -UNIT_LOWER_R).text(lower, UNIT_SIZE, PRINT_T,
                                                         combine=False).val()]

    bodies = [(case, "case", M_CHROME_PLATE),
              (dial, "dial", M_GAUGE_WHITE),
              (cq.Compound.makeCompound(black), "black-print", M_GAUGE_BLACK),
              (cq.Compound.makeCompound(red), "red-print", M_GAUGE_RED),
              (_cyl(HUB_DIAL_D, (0.0, 1.0, 0.0), face_y, face_y + 1.6).translate((cx, 0.0, cz)),
               "hub", M_CHROME_PLATE)]
    full = spec["outer"]["full"]
    for i, ((near, far), material) in enumerate(spec["bands"]):
        wedge = (plane(face_y)
                 .polyline([_at(BAND_NEAR_R, _scale_deg(near, full)),
                            _at(BAND_FAR_R, _scale_deg(near, full)),
                            _at(BAND_FAR_R, _scale_deg(far, full)),
                            _at(BAND_NEAR_R, _scale_deg(far, full)),
                            _at(BAND_NEAR_R, _scale_deg(near, full))]).wire()
                 .extrude(BAND_T).val())
        bodies.insert(2 + i, (wedge, f"band-{i + 1}", material))
    return bodies


def build_assembly() -> cq.Assembly:
    """Every body the customer sees, each in what it is made of."""
    a = cq.Assembly(name="taprite-3741-regulator")
    a.add(build_body(), name="body", color=M_BRASS)
    a.add(build_inlet_nut(), name="cga320-nut", color=M_BRASS)
    a.add(build_blowoff(), name="blow-off", color=M_BRASS)
    a.add(build_bonnet(), name="bonnet", color=M_MOULDED_BLACK)
    a.add(build_adjustment(), name="adjusting-screw", color=M_NICKEL_PLATE)
    a.add(build_outlet_connector(), name="outlet-connector", color=M_JG_GREY_ACETAL)
    for label, spec, station in (("tank", TANK_DIAL, tank_dial()),
                                 ("outlet", OUTLET_DIAL, outlet_dial())):
        for shape, name, material in build_dial(spec, station[0]):
            a.add(shape, name=f"{label}-{name}", color=material)
    return a


def stations_hold():
    """Hold the six extremes to `taprite-3741-regulator.step` — every one of them a station this
    module states, so a picture posed on one is posed on the file it draws."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (
            ("CGA-320 nut face", -INLET_NUT_FACE, bb.xmin),
            ("cylinder-contents dial", TANK_REACH + CASE_D / 2.0, bb.xmax),
            ("outlet-pressure dial", OUTLET_REACH + CASE_D / 2.0, bb.zmax),
            ("outlet push-fit mouth", OUTLET_MOUTH_Z, bb.zmin),
            ("adjusting screw tip", SCREW_TIP_Y, bb.ymax),
            ("CGA-320 nut's back flat", -CGA320_NUT_FLATS / 2.0, bb.ymin)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"taprite-3741-regulator {what} stands at {claimed:g} and {STEP.name} ends at "
                f"{actual:.4f} — the station a picture is aimed at is not where the file is.")


def main():
    assembly = build_assembly()
    bb = assembly.toCompound().BoundingBox()
    print(f"Taprite 3741 CGA-320 CO2 regulator — set at the factory to {FACTORY_SET_PSI:g} psi, "
          f"0–120 psi working, {RELIEF_PSI:g} psi blow-off")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  CGA-320 nut {CGA320_NUT_FLATS:.3f} across flats on {CGA320_THREAD_D:.2f} thread; "
          f"outlet PI010822S push-fit for {TUBE_D:g} tube")
    print(f"  Dials Ø{CASE_D:g}: contents 0–{TANK_FULL_PSI:g} psi at {TANK_REACH:g}, "
          f"outlet 0–{OUTLET_FULL_PSI:g} psi at {OUTLET_REACH:g}")
    for name, (pos, axis) in stations().items():
        print(f"  {name:>12}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out "
              f"({axis[0]:.2f}, {axis[1]:.2f}, {axis[2]:.2f})")
    export_assembly(assembly, str(STEP))
    print(f"-> {STEP.name}")
    stations_hold()


if __name__ == "__main__":
    main()
