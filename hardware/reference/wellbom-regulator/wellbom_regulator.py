"""Wellbom CGA-320 CO2 regulator — the primary regulator that ships with the appliance.

It stands on the customer's own CO2 cylinder and is the only thing on this machine the customer
threads onto anything. Its CGA-320 nut pulls down on the cylinder valve; its 7/16"-20 male flare
outlet takes the MI4508F4SLF's brass swivel nut, and the red 1/4" tether runs from there to the
CO2 bulkhead on the +Y wall of back-top (`ledger/bom.md` §4).

Two dials, one adjustment, one shutoff, one relief valve. THE TWO DIALS DO NOT READ THE SAME
THING and the picture has to say which is which: the +X dial reads what is left in the cylinder,
0–3000 psi, and the +Z dial reads what is going out to the appliance, 0–230 psi with a green
band across the range the vendor carbonates soda in. Both are drawn here with their scales,
their needles at rest on zero, and nothing behind the dial face.

Where the figures come from
---------------------------
There is no dimensioned drawing for this part. What is standardised is taken at its standard —
the CGA-320 nut's 1-1/8" hex and 0.825"-14 thread, the 7/16"-20 UNF outlet, the 2" dial every
CO2 beer regulator's gauges are sold in. Everything else is proportion read off the listing's
own front-view photography (Amazon B0G13P5PMY, image `71bzwkO3RaL`), scaled so the outlet's
7/16"-20 thread in that image is 11.11 mm across. `README.md` says which figure is which.

Coordinate frame
----------------
The frame the regulator hangs in once it is on the cylinder:

- **+Y** out of the body's face toward the customer — the adjustment knob.
- **+Z** up — the outlet-pressure dial. **−Z** down — the shutoff and the outlet flare.
- **−X** the inlet axis, out toward the cylinder — the CGA-320 nut.
- **+X** the cylinder-contents dial, with the relief valve on the arm below it.

Origin where the bonnet's axis crosses the inlet and outlet axes. The regulator is handed, and
this is the hand it has: standing in front of it, the customer sees the cylinder on their right,
the contents dial on their left, the outlet dial above and the flare below.

Run:
    tools/cad-venv/bin/python hardware/reference/wellbom-regulator/wellbom_regulator.py
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
                        M_GAUGE_WHITE, M_MOULDED_BLACK)

STEP = _here.parent / "wellbom-regulator.step"

# --- the standards ----------------------------------------------------------
# CGA-320 is the connection every USA CO2 beverage cylinder presents: a 0.825"-14 NGO-RH male
# thread on the valve, and a female nut on the regulator that pulls a nipple down onto the
# valve's own face with a nylon washer between them. The nut takes a 1-1/8" wrench.
CGA320_NUT_FLATS = 25.4 * 1.125
CGA320_THREAD_D = 25.4 * 0.825
CGA320_NUT_LENGTH = 25.4
CGA320_NIPPLE_D = 15.9          # the nose that seats on the cylinder valve, inside the nut

# The outlet: a 1/4" SAE 45° male flare. The MI4508F4SLF's swivel nut runs onto the thread and
# pulls its own flared tube over this cone — metal on metal, hand tight, no tape and no tool.
FLARE_THREAD_D = 25.4 * 0.4375  # 7/16"-20 UNF major diameter
FLARE_ROOT_D = 25.4 * 0.3834    # and its minor, the stem the crests stand on
FLARE_PITCH = 25.4 / 20.0
FLARE_CONE_HALF_ANGLE = 45.0
FLARE_TIP_D = 6.4
FLARE_BORE_D = 4.8
OUTLET_HEX_FLATS = 25.4 * 0.5625   # 9/16", the hex every 1/4" flare fitting carries

# The gauges are the 2" dial size this whole class of regulator is built from.
DIAL_D = 47.0                    # the printed disc, its rim under the bezel
WINDOW_D = 44.0                  # what the bezel leaves of it
CASE_D = 55.0
CASE_DEPTH = 21.0
GAUGE_REACH = 63.0               # body centre to a dial's own centre
GAUGE_STEM_D = 17.0              # the brass boss between the body and the case
GAUGE_FACE_Y = 14.0              # where the dial's own front plane stands
BEZEL_PROUD = 5.0                # how far the case wall stands over the dial

# --- the body ---------------------------------------------------------------
HUB_D = 34.0                     # the manifold the four arms leave
HUB_BACK_Y = -20.0
HUB_FRONT_Y = 2.0
BONNET_D = 53.0                  # the diaphragm chamber standing on the front of it
BONNET_BACK_Y = -6.0
BONNET_FRONT_Y = 16.0
BONNET_EDGE_R = 5.0
LOCK_RING_D = 30.0               # the brass ring that pins the knob where it was set
LOCK_RING_FRONT_Y = 27.0
KNOB_D = 44.0                    # over the lobes; the flutes cut in to `KNOB_VALLEY_D`
KNOB_VALLEY_D = 38.0
KNOB_LOBES = 6
KNOB_FRONT_Y = 45.0
KNOB_MARK_PROUD = 0.8            # the turn direction moulded onto the knob's face

INLET_AXIS = (-1.0, 0.0, 0.0)    # out toward the cylinder, on the customer's right
TANK_AXIS = (1.0, 0.0, 0.0)      # the contents dial, on the customer's left
INLET_BOSS_D = 20.0
INLET_BOSS_REACH = 26.0          # where the boss ends and the nipple runs on
INLET_NIPPLE_D = 14.0
INLET_NUT_NEAR = 53.0            # the nut's inboard face
INLET_NUT_FACE = INLET_NUT_NEAR + CGA320_NUT_LENGTH

OUTLET_BOSS_D = 18.0
OUTLET_BOSS_Z = -35.0            # where the boss ends and the shutoff body begins
SHUTOFF_BODY_D = 22.0
SHUTOFF_BODY_Z = -59.0
SHUTOFF_KNOB_Z = -47.0           # the shutoff knob's own axis, running out +Y
SHUTOFF_KNOB_D = 24.0
SHUTOFF_VALLEY_D = 21.0
SHUTOFF_COLLAR_D = 27.0
SHUTOFF_KNOB_NEAR_Y = 11.0
SHUTOFF_KNOB_FAR_Y = 27.0
OUTLET_HEX_Z = -69.0             # where the hex ends and the flare thread runs on
FLARE_THREAD_Z = -80.0           # where the thread ends and the 45° cone begins
_flare_cone_drop = (FLARE_THREAD_D - FLARE_TIP_D) / 2.0 * math.tan(
    math.radians(FLARE_CONE_HALF_ANGLE))
FLARE_CONE_Z = FLARE_THREAD_Z - _flare_cone_drop
OUTLET_TIP_Z = FLARE_CONE_Z - 1.5

# The relief valve, on the one arm that is neither a gauge nor a port. It lifts on its own near
# 150 psi and the ring pulls it by hand; the vendor's own labelled figure states both.
PRV_RELIEF_PSI = 150.0
PRV_BEARING_DEG = -37.0          # in the XZ plane, from the contents dial's arm toward the outlet
PRV_STEM_D = 10.0
PRV_ROOT_R = 16.0
PRV_STEM_R = 44.0
PRV_COLLAR_D = 14.0
PRV_COLLAR_NEAR_R = 24.0
PRV_COLLAR_FAR_R = 32.0
PRV_RING_R = 52.0
PRV_RING_D = 16.0
PRV_WIRE_D = 2.5

# --- what each dial says ----------------------------------------------------
# A dial's scale runs 270° clockwise from its zero at the lower left. The two rings are the same
# pressure in two units: the outer ring is printed red and the inner ring black, on both gauges,
# and which unit is which differs between them because the two dials are different parts.
DIAL_ZERO_DEG = 225.0
DIAL_SWEEP_DEG = 270.0
# The band on the outlet dial, in psi, off the listing's own front view — the vendor's
# recommended 80 psi for soda sits in the middle of it.
SODA_BAND_PSI = (70.0, 95.0)

TANK_FULL_PSI = 3000.0
OUTLET_FULL_PSI = 230.0


def _ring_spec(full, major, minor, labels):
    """One printed scale: its full-scale value, its tick steps and the values it letters."""
    return {"full": full, "major": major, "minor": minor, "labels": labels}


# The cylinder-contents dial: psi in red outside, bar in black inside, and the gauge standard
# it is built to lettered under the top of the scale.
TANK_DIAL = {
    "red": _ring_spec(TANK_FULL_PSI, 500.0, 100.0, (0, 500, 1000, 1500, 2000, 2500, 3000)),
    "black": _ring_spec(TANK_FULL_PSI / 14.5038, 50.0, 10.0, (0, 50, 100, 150, 200)),
    "units": ("bar", "psi"),
    "stamp": "EN562",
    "band": None,
}
# The outlet dial: psi in black inside, bar in red outside, and the soda band across the middle.
OUTLET_DIAL = {
    "red": _ring_spec(OUTLET_FULL_PSI / 14.5038, 4.0, 1.0, (4, 8, 12, 16)),
    "black": _ring_spec(OUTLET_FULL_PSI, 50.0, 10.0, (0, 50, 100, 150, 200, 230)),
    "units": ("psi", "bar"),
    "stamp": None,
    "band": SODA_BAND_PSI,
}

# Where each ring sits on the face, off the listing's own dial photography.
RED_NUMERAL_R = 19.0
RED_TICK_OUT_R = 17.4
RED_TICK_MAJOR_R = 14.0
RED_TICK_MINOR_R = 15.6
BLACK_ARC_R = 13.4
BLACK_TICK_MAJOR_R = 11.2
BLACK_TICK_MINOR_R = 12.2
BLACK_NUMERAL_R = 9.4
UNIT_UPPER_R = 6.4
UNIT_LOWER_R = 9.4
STAMP_R = 4.8
NUMERAL_SIZE = 2.8
STAMP_SIZE = 2.2
UNIT_SIZE = 2.6
MAJOR_TICK_W = 0.8
MINOR_TICK_W = 0.45
PRINT_T = 0.6
BAND_T = 0.25                    # the band goes down first and the scale is printed over it
NEEDLE_R = 14.6
NEEDLE_TAIL_R = 4.2
NEEDLE_W = 1.2
HUB_DIAL_D = 4.3
BAND_NEAR_R = 3.2
BAND_FAR_R = 11.2

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
    """The male flare's tip: `(position, outward axis)`. The MI4508F4SLF's swivel nut comes up
    this axis and pulls its flared tube over the cone behind the tip."""
    return (0.0, 0.0, OUTLET_TIP_Z), (0.0, 0.0, -1.0)


def adjustment() -> tuple:
    """The pressure-adjustment knob's own face and the axis a hand turns it about — what the
    customer is pointed at when the guide says to set the pressure."""
    return (0.0, KNOB_FRONT_Y, 0.0), (0.0, 1.0, 0.0)


def shutoff() -> tuple:
    """The knob that opens and closes the outlet, on its own axis out the body's face."""
    return (0.0, SHUTOFF_KNOB_FAR_Y, SHUTOFF_KNOB_Z), (0.0, 1.0, 0.0)


def relief() -> tuple:
    """The relief valve's pull ring, at the far end of its arm."""
    x, z = _bearing(PRV_RING_R)
    return (x, 0.0, z), _bearing(1.0, as_axis=True)


def tank_dial() -> tuple:
    """The cylinder-contents dial's centre and the direction it is read from."""
    return (GAUGE_REACH, GAUGE_FACE_Y, 0.0), (0.0, 1.0, 0.0)


def outlet_dial() -> tuple:
    """The outlet-pressure dial's centre and the direction it is read from."""
    return (0.0, GAUGE_FACE_Y, GAUGE_REACH), (0.0, 1.0, 0.0)


def stations() -> dict:
    """Everything a picture or a neighbour points at, under the name it is pointed at by."""
    return {"inlet": inlet(), "outlet": outlet(), "adjustment": adjustment(),
            "shutoff": shutoff(), "relief": relief(),
            "tank-dial": tank_dial(), "outlet-dial": outlet_dial()}


# --- the solid ---------------------------------------------------------------

def _bearing(r: float, as_axis: bool = False):
    """A point on the relief valve's arm at radius `r`, in the XZ plane."""
    a = math.radians(PRV_BEARING_DEG)
    x, z = r * math.cos(a), r * math.sin(a)
    return (x, 0.0, z) if as_axis else (x, z)


def _perpendicular(direction: cq.Vector) -> tuple:
    """Two unit vectors across `direction`, so a feature can be swung about an arm on any axis."""
    seed = cq.Vector(0, 0, 1) if abs(direction.z) < 0.9 else cq.Vector(1, 0, 0)
    across = direction.cross(seed).normalized()
    return across, direction.cross(across).normalized()


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


def _threaded(root_d: float, crest_d: float, pitch: float, axis, near: float,
              far: float) -> cq.Solid:
    """A male thread as the stem it is cut on and the crests standing off it, one per turn —
    what says "a nut runs onto this" without a helix nobody measures off."""
    stem = _cyl(root_d, axis, near, far)
    turns = int((far - near) / pitch)
    for i in range(turns):
        at = near + (i + 0.5) * pitch
        stem = stem.fuse(_cyl(crest_d, axis, at - pitch * 0.28, at + pitch * 0.28))
    return stem


def _fluted_knob(outer_d: float, valley_d: float, lobes: int, axis, near: float,
                 far: float) -> cq.Solid:
    """A moulded control knob: a cylinder with `lobes` scallops swept out of its flank, so a
    thumb and finger find it without looking."""
    direction = cq.Vector(*axis)
    body = _cyl(outer_d, axis, near, far)
    scallop_r = (outer_d - valley_d) / 2.0 + 3.0
    centre_r = valley_d / 2.0 + scallop_r
    across, up = _perpendicular(direction)
    for i in range(lobes):
        a = 2.0 * math.pi * i / lobes
        here = across.multiply(math.cos(a)).add(up.multiply(math.sin(a)))
        body = body.cut(cq.Solid.makeCylinder(
            scallop_r, far - near + 2.0,
            direction.multiply(near - 1.0).add(here.multiply(centre_r)), direction))
    return body


def build_body() -> cq.Solid:
    """The chromed brass: the manifold, the diaphragm chamber over it, and the four arms —
    inlet, outlet with its shutoff body, the two gauge bosses and the relief valve."""
    bonnet = (cq.Workplane("XY").workplane(offset=BONNET_BACK_Y).circle(BONNET_D / 2.0)
              .extrude(BONNET_FRONT_Y - BONNET_BACK_Y).edges("%Circle").fillet(BONNET_EDGE_R)
              .val().rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90.0))
    solid = _cyl(HUB_D, (0.0, 1.0, 0.0), HUB_BACK_Y, HUB_FRONT_Y).fuse(bonnet)

    solid = solid.fuse(_cyl(INLET_BOSS_D, INLET_AXIS, 0.0, INLET_BOSS_REACH))
    solid = solid.fuse(_cyl(INLET_NIPPLE_D, INLET_AXIS, INLET_BOSS_REACH, INLET_NUT_NEAR + 17.0))
    solid = solid.fuse(_cyl(OUTLET_BOSS_D, (0.0, 0.0, -1.0), 0.0, -OUTLET_BOSS_Z))
    solid = solid.fuse(_cyl(SHUTOFF_BODY_D, (0.0, 0.0, -1.0), -OUTLET_BOSS_Z, -SHUTOFF_BODY_Z))
    solid = solid.fuse(_hex(OUTLET_HEX_FLATS, (0.0, 0.0, -1.0), -SHUTOFF_BODY_Z, -OUTLET_HEX_Z))
    solid = solid.fuse(_threaded(FLARE_ROOT_D, FLARE_THREAD_D, FLARE_PITCH, (0.0, 0.0, -1.0),
                                 -OUTLET_HEX_Z, -FLARE_THREAD_Z))
    solid = solid.fuse(cq.Solid.makeCone(
        FLARE_THREAD_D / 2.0, FLARE_TIP_D / 2.0, FLARE_THREAD_Z - FLARE_CONE_Z,
        cq.Vector(0, 0, FLARE_THREAD_Z), cq.Vector(0, 0, -1)))
    solid = solid.fuse(_cyl(FLARE_TIP_D, (0.0, 0.0, -1.0), -FLARE_CONE_Z, -OUTLET_TIP_Z))
    solid = solid.cut(_cyl(FLARE_BORE_D, (0.0, 0.0, -1.0), -SHUTOFF_BODY_Z, -OUTLET_TIP_Z - 0.1))

    solid = solid.fuse(_cyl(SHUTOFF_COLLAR_D, (0.0, 1.0, 0.0), 0.0, SHUTOFF_KNOB_NEAR_Y)
                       .translate((0.0, 0.0, SHUTOFF_KNOB_Z)))

    bearing = _bearing(1.0, as_axis=True)
    solid = solid.fuse(_cyl(PRV_STEM_D, bearing, PRV_ROOT_R, PRV_STEM_R))
    solid = solid.fuse(_cyl(PRV_COLLAR_D, bearing, PRV_COLLAR_NEAR_R, PRV_COLLAR_FAR_R))
    ring_x, ring_z = _bearing(PRV_RING_R)
    solid = solid.fuse(cq.Solid.makeTorus(
        PRV_RING_D / 2.0, PRV_WIRE_D / 2.0, cq.Vector(ring_x, 0.0, ring_z), cq.Vector(0, 1, 0)))

    for axis in (TANK_AXIS, (0.0, 0.0, 1.0)):
        solid = solid.fuse(_cyl(GAUGE_STEM_D, axis, 0.0, GAUGE_REACH - CASE_D / 2.0 + 2.0))
    return solid.clean()


def build_inlet_nut() -> cq.Solid:
    """The CGA-320 nut: a 1-1/8" hex, bored the cylinder valve's 0.825" thread, that turns
    freely on the nipple standing inside it."""
    nut = _hex(CGA320_NUT_FLATS, INLET_AXIS, INLET_NUT_NEAR, INLET_NUT_FACE)
    nut = nut.cut(_cyl(CGA320_THREAD_D, INLET_AXIS, INLET_NUT_NEAR + 16.0, INLET_NUT_FACE + 0.1))
    return nut.cut(_cyl(CGA320_NIPPLE_D, INLET_AXIS,
                        INLET_NUT_NEAR - 0.1, INLET_NUT_NEAR + 16.0)).clean()


def build_lock_ring() -> cq.Solid:
    """The brass ring under the knob. Backed off, the knob turns; run up, the setting stays
    where an elbow leaves it."""
    return _cyl(LOCK_RING_D, (0.0, 1.0, 0.0), BONNET_FRONT_Y - 2.0, LOCK_RING_FRONT_Y)


def build_adjust_knob() -> cq.Solid:
    """The pressure-adjustment knob, and the turn direction moulded into its face."""
    knob = _fluted_knob(KNOB_D, KNOB_VALLEY_D, KNOB_LOBES, (0.0, 1.0, 0.0),
                        LOCK_RING_FRONT_Y, KNOB_FRONT_Y)
    face = cq.Workplane(_dial_plane).workplane(offset=KNOB_FRONT_Y)
    sweep = (face.circle(13.0).circle(11.4).extrude(KNOB_MARK_PROUD).val()
             .intersect(cq.Solid.makeBox(40.0, 4.0, 40.0,
                                         cq.Vector(-20.0, KNOB_FRONT_Y - 1.0, -14.0))))
    marks = (face.center(11.0, -6.5).text("+", 5.5, KNOB_MARK_PROUD, combine=False).val()
             .fuse(face.center(-11.0, -6.5).text("-", 5.5, KNOB_MARK_PROUD,
                                                combine=False).val()))
    return knob.fuse(sweep).fuse(marks).clean()


def build_shutoff_knob() -> cq.Solid:
    """The knob that opens and closes the outlet, out the front of its own valve body."""
    return _fluted_knob(SHUTOFF_KNOB_D, SHUTOFF_VALLEY_D, KNOB_LOBES, (0.0, 1.0, 0.0),
                        SHUTOFF_KNOB_NEAR_Y, SHUTOFF_KNOB_FAR_Y).translate(
        (0.0, 0.0, SHUTOFF_KNOB_Z))


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
    n = int(round(full / step))
    return [i * step * full / (n * step) for i in range(n + 1)]


def _numeral(value: float, plane, r: float, deg: float, size: float) -> cq.Shape:
    """One lettered reading, standing upright the way the dial prints it."""
    u, v = _at(r, deg)
    text = f"{value:g}"
    return plane.center(u, v).text(text, size, PRINT_T, combine=False).val()


def _ring_marks(spec: dict, plane, numeral_r, major_r, minor_r, out_r) -> tuple:
    """One printed scale as `(the marks, the numerals)`, each a compound of its own bodies."""
    full = spec["full"]
    marks = []
    for value in _steps(spec["minor"], full):
        marks.append(_tick(minor_r, out_r, _scale_deg(value, full), MINOR_TICK_W, plane))
    for value in _steps(spec["major"], full):
        marks.append(_tick(major_r, out_r, _scale_deg(value, full), MAJOR_TICK_W, plane))
    numerals = [_numeral(v, plane, numeral_r, _scale_deg(v, full), NUMERAL_SIZE)
                for v in spec["labels"]]
    return cq.Compound.makeCompound(marks), cq.Compound.makeCompound(numerals)


def _needle(deg: float, plane) -> cq.Shape:
    """The pointer, at rest on its own zero: a tapered blade out to the scale and a stub
    counterweight behind the hub."""
    a = math.radians(deg)
    along = (math.cos(a), math.sin(a))
    across = (-math.sin(a), math.cos(a))

    def at(radius, half):
        return (radius * along[0] + half * across[0], radius * along[1] + half * across[1])

    corners = [at(NEEDLE_R, 0.35), at(1.5, NEEDLE_W / 2.0), at(-NEEDLE_TAIL_R, 1.1),
               at(-NEEDLE_TAIL_R, -1.1), at(1.5, -NEEDLE_W / 2.0), at(NEEDLE_R, -0.35)]
    return plane.polyline(corners + corners[:1]).wire().extrude(0.8).val()


def build_dial(spec: dict, centre) -> list:
    """One gauge, standing at `centre` and read from +Y — `[(shape, name, material)]`.

    The case is a black cup and the bezel round its mouth leaves `WINDOW_D` of the dial showing;
    everything the customer reads stands on that disc. The lens over it and the works behind it
    are not modelled."""
    cx, _cy, cz = centre
    face_y = GAUGE_FACE_Y
    front_y = face_y + BEZEL_PROUD

    def plane(offset):
        return cq.Workplane(_dial_plane).workplane(offset=offset).center(-cx, cz)

    case = (_cyl(CASE_D, (0.0, 1.0, 0.0), front_y - CASE_DEPTH, front_y)
            .cut(_cyl(DIAL_D + 0.2, (0.0, 1.0, 0.0), front_y - CASE_DEPTH - 0.1, face_y + 0.4))
            .cut(_cyl(WINDOW_D, (0.0, 1.0, 0.0), face_y + 0.4, front_y + 0.1))
            .translate((cx, 0.0, cz)))
    dial = _cyl(DIAL_D, (0.0, 1.0, 0.0), face_y - 1.0, face_y).translate((cx, 0.0, cz))

    marks = plane(face_y)
    red_ticks, red_numerals = _ring_marks(spec["red"], marks, RED_NUMERAL_R, RED_TICK_MAJOR_R,
                                          RED_TICK_MINOR_R, RED_TICK_OUT_R)
    black_ticks, black_numerals = _ring_marks(spec["black"], marks, BLACK_NUMERAL_R,
                                              BLACK_TICK_MAJOR_R, BLACK_TICK_MINOR_R,
                                              BLACK_ARC_R)
    black = [black_ticks, black_numerals,
             plane(face_y).circle(BLACK_ARC_R).circle(BLACK_ARC_R - 0.3).extrude(PRINT_T).val(),
             _needle(DIAL_ZERO_DEG, plane(face_y + PRINT_T))]
    upper, lower = spec["units"]
    black.append(plane(face_y).center(0.0, -UNIT_UPPER_R).text(upper, UNIT_SIZE, PRINT_T,
                                                      combine=False).val())
    if spec["stamp"]:
        black.append(plane(face_y).center(0.0, STAMP_R).text(spec["stamp"], STAMP_SIZE, PRINT_T,
                                                         combine=False).val())
    red = [red_ticks, red_numerals,
           plane(face_y).center(0.0, -UNIT_LOWER_R).text(lower, UNIT_SIZE, PRINT_T,
                                                 combine=False).val()]

    bodies = [(case, "case", M_GAUGE_BLACK),
              (dial, "dial", M_GAUGE_WHITE),
              (cq.Compound.makeCompound(black), "black-print", M_GAUGE_BLACK),
              (cq.Compound.makeCompound(red), "red-print", M_GAUGE_RED),
              (_cyl(HUB_DIAL_D, (0.0, 1.0, 0.0), face_y, face_y + 1.6).translate((cx, 0.0, cz)),
               "hub", M_CHROME_PLATE)]
    if spec["band"]:
        near, far = spec["band"]
        full = spec["black"]["full"]
        wedge = (plane(face_y)
                 .polyline([(0.0, 0.0),
                            _at(BAND_NEAR_R, _scale_deg(near, full)),
                            _at(BAND_FAR_R, _scale_deg(near, full)),
                            _at(BAND_FAR_R, _scale_deg(far, full)),
                            _at(BAND_NEAR_R, _scale_deg(far, full)),
                            (0.0, 0.0)]).wire().extrude(BAND_T).val())
        bodies.insert(2, (wedge, "band", M_GAUGE_GREEN))
    return bodies


def build_assembly() -> cq.Assembly:
    """Every body the customer sees, each in what it is made of."""
    a = cq.Assembly(name="wellbom-regulator")
    a.add(build_body(), name="body", color=M_CHROME_PLATE)
    a.add(build_inlet_nut(), name="cga320-nut", color=M_CHROME_PLATE)
    a.add(build_lock_ring(), name="lock-ring", color=M_BRASS)
    a.add(build_adjust_knob(), name="adjust-knob", color=M_MOULDED_BLACK)
    a.add(build_shutoff_knob(), name="shutoff-knob", color=M_MOULDED_BLACK)
    for label, spec, station in (("tank", TANK_DIAL, tank_dial()),
                                 ("outlet", OUTLET_DIAL, outlet_dial())):
        for shape, name, material in build_dial(spec, station[0]):
            a.add(shape, name=f"{label}-{name}", color=material)
    return a


def stations_hold():
    """Hold the six extremes to `wellbom-regulator.step` — every one of them a station this
    module states, so a picture posed on one is posed on the file it draws."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    dial_far = GAUGE_REACH + CASE_D / 2.0
    for what, claimed, actual in (
            ("CGA-320 nut face", -INLET_NUT_FACE, bb.xmin),
            ("cylinder-contents dial", dial_far, bb.xmax),
            ("outlet-pressure dial", dial_far, bb.zmax),
            ("flare tip", OUTLET_TIP_Z, bb.zmin),
            ("turn marks on the knob", KNOB_FRONT_Y + KNOB_MARK_PROUD, bb.ymax),
            ("manifold back", HUB_BACK_Y, bb.ymin)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"wellbom-regulator {what} stands at {claimed:g} and {STEP.name} ends at "
                f"{actual:.4f} — the station a picture is aimed at is not where the file is.")


def main():
    assembly = build_assembly()
    bb = assembly.toCompound().BoundingBox()
    print("Wellbom CGA-320 CO2 regulator — 0–120 psi out, 150 psi relief")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  CGA-320 nut {CGA320_NUT_FLATS:.3f} across flats on {CGA320_THREAD_D:.2f} thread; "
          f"outlet {FLARE_THREAD_D:.2f} male flare")
    print(f"  Dials Ø{CASE_D:g} at {GAUGE_REACH:g} off centre: "
          f"contents 0–{TANK_FULL_PSI:g} psi, outlet 0–{OUTLET_FULL_PSI:g} psi "
          f"banded {SODA_BAND_PSI[0]:g}–{SODA_BAND_PSI[1]:g}; relief at {PRV_RELIEF_PSI:g}")
    for name, (pos, axis) in stations().items():
        print(f"  {name:>12}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out "
              f"({axis[0]:.2f}, {axis[1]:.2f}, {axis[2]:.2f})")
    export_assembly(assembly, str(STEP))
    print(f"-> {STEP.name}")
    stations_hold()


if __name__ == "__main__":
    main()
