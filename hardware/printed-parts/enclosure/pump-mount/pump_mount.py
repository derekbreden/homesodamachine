"""Pump mount — the printed saddle that holds one Kamoer KPHM400 in Zone C.

A static part in its own frame: origin ON THE PUMP'S MOTOR AXIS, in the plane of
the pump's stamped mounting-bracket face; +X toward the head, +Y world back, +Z
up. The pump row lies depth-along-X in one pose (`_contents` PUMP_A_POS /
PUMP_B_POS), so the world placement of a mount is a pure translation and every
dimension below reads directly against the pump surface it faces.

The pump enters and leaves STRAIGHT UP. Nothing is threaded, nothing is captive,
and nothing but a hand is needed:

  * The HEAD SOCKET — floor, two side walls, an end wall at the head's front
    face and a stop rib at its rear face — is the whole of the locating. The head
    is a square prism, so a square socket takes the rotor's torque reaction in
    wall shear across the head's own width; no friction, no preload, and nothing
    for the pump to walk against.
  * The SPREAD LATCH is the only spring in the part: each side wall carries on up
    past the shelf as a tongue whose ledge returns FLAT over the head's top face,
    with the finger tab hung inboard of it on a short arm. The flat ledge is a
    positive stop — the pump cannot rise while the tongues are relaxed — so the
    retention is a ledge in shear, not a detent holding on friction. Two
    fingertips down the lane between the tabs, pushed apart, free both ledges at
    once.
  * The MOTOR SADDLE is an open half-round under the barrel, no snap. It is the
    pump's second support point, taking the motor's cantilever off the socket;
    being open, it never has to be released.

The mount itself fastens to the enclosure's front wall with four M3 heat-set
inserts on two feet — a factory joint, not a service one. Tool-free is a
property of the PUMP↔MOUNT interface only.

Print orientation: build direction along +X, head end down, standing on the
socket's end wall. The layer planes are then the YZ planes, so the latch tongues
— whose beam axis runs +Z and whose deflection runs ±Y — bend entirely within a
layer, never across the layer bond. Every wall, web and foot flange stands
vertical in that orientation; the only overhangs are the stop rib, the latch
ledges and the saddle's lead-in chamfer, each under 5 mm.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
for _p in (_hw / "scripts", _repo / "tools", _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "flavor" / "pump-case", _hw / "reference" / "kamoer-kphm400"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
from docgen import substitute_md
import kamoer_kphm400 as _kp
import pump_case as _pc


# --- the pump this holds ----------------------------------------------------
# Read live off the reference model, so no pump dimension is re-typed here.
head_half = _kp.head_w / 2.0             # the head's square half-section — the socket's bore
head_reach = _kp.head_depth              # bracket face to head front face
barrel_r = _kp.motor_dia / 2.0
# The boss behind the bracket face — bracket plate, motor adapter plate, rotor
# boss. Its outline is not pinned by any drawing, so nothing the mount grows may
# enter its half-extent: the rear stop rib lives in the seat's corner, outside it.
boss_half = _pc.bore_half_span
# The two outlet elbows stand on the head's TOP face, one either side of the axis,
# and their collets overhang the head's side faces. Their station is the one band
# of that face the latch may not use.
elbow_x = -_kp.arch_plane_z
elbow_r = cq.importers.importStep(
    str(_hw / "reference" / "elbow-connector" / "elbow-connector.step")).val().BoundingBox().xmax
# The band of motor barrel that is bare cylinder on BOTH the reference mock and
# the datasheet part: the mock's `motor_body` starts one boss aft of the bracket
# face, and the real motor's end cap is 111.43 mm from the head's front face.
_pump_total_len = 111.43
barrel_west = max(-_kp.tower_top_z, head_reach - _pump_total_len)
barrel_east = min(-_kp.octagon_top_z, -(_pc.base_thickness + _pc.lower_cap_thickness))

# --- fits and sections ------------------------------------------------------
fit = 0.35              # printed pocket to pump body, per side
fit_x = 0.60            # ditto along the axis, where the socket's two stops face each other
bed = 0.10              # saddle relief — the socket floor is the seat, the saddle beds in behind it
wall = 3.0              # socket wall, latch tongue, foot flange
floor = 4.0             # socket floor / spine plate

# --- the head socket --------------------------------------------------------
seat_z = -head_half                          # the head's bottom face — a declared contact
plate_bottom_z = seat_z - floor
socket_inner_y = head_half + fit             # side-wall inner faces
socket_outer_y = socket_inner_y + wall
# The side walls top out on the pump's axis plane — half the head's height of wall
# to shear the rotor's torque against, and no more, because this height is exactly
# the LIFT a swap costs: the pump is free of the mount the moment its bottom face
# passes the wall tops, and every millimetre of wall is a millimetre it must first
# travel up a column that ends at the enclosure ceiling. Well under the head's top
# face, so the walls also stay clear of the elbow collets that overhang it.
shelf_z = 0.0
clear_lift = shelf_z - seat_z
stop_face_x = -fit_x                         # rear stop rib's front face, at the head's rear face
end_face_x = head_reach + fit_x              # end wall's rear face, at the head's front face
end_wall_x = end_face_x + wall
# The rear stop is a low rib across the seat: tall enough to be a real axial datum
# on the head's rear face, short and narrow enough to stay clear of the boss.
stop_h = 4.0
stop_t = 3.8
stop_half_y = 20.0

# --- the spread latch -------------------------------------------------------
# One tongue per side wall, the pair at one X station. The head's top face is bare
# in two bands, either side of the outlet-elbow station, and the station a mount
# uses is the band that lies under the top-wall hopper opening at ITS pump's X —
# the front band for P-A (whose motor end runs far west of the opening), the rear
# band for P-B (whose head front face runs east of it). LATCH_STATION carries the
# choice; the assertion below holds either against the elbows.
tongue_w = 10.0
LATCH_STATION = {"front": end_face_x - tongue_w, "rear": 5.0}
# The tongue is the wall's own top carried on up past the shelf, so the shelf IS
# its root — no slot, and the 53.9 mm of wall below it is the fixed end a cantilever
# calculation assumes.
tongue_root_z = shelf_z
ledge_z = head_half + fit                    # the ledge's underside, over the head's top face
ledge_reach = 1.5                            # inward reach past the head's side face
ledge_t = 3.0                                # ledge thickness, and the lead-in ramp's 45° rise
ledge_tip_y = socket_inner_y - ledge_reach
tongue_top_z = ledge_z + ledge_t
latch_spread = head_half - ledge_tip_y       # tongue deflection while the head passes the ledge
# The release is two fingertips reaching down between the tabs and pushing them
# apart, so each tab hangs INBOARD of its tongue on a short arm, over the head's
# top face: that is the one place a finger can reach BOTH of them, because P-B's
# whole −Y flank stands south of the top-wall opening and nothing on the outside of
# a wall is reachable there. Nothing on a tab reaches outboard for the same reason
# the walls do not — the inverted bag tray hangs three millimetres off the +Y one.
# The whole latch stack is CEILINGED by the pump's own outlet elbows: each elbow's
# free leg turns horizontally 44.25 mm above the axis plane and sweeps the air over
# the head's top face, so nothing on the mount may stand into it.
elbow_leg_underside_z = 44.25
tab_arm = 7.0                                # how far inboard of the wall the tab stands
tab_arm_t = 2.5
tab_h = 4.8
tab_grip = 1.0                               # inward flare at the tab's top, so a fingertip holds
tab_y = socket_inner_y - tab_arm
tab_top_z = tongue_top_z + tab_arm_t + tab_h

# --- the motor saddle -------------------------------------------------------
saddle_w = 22.0
saddle_x1 = barrel_east - 8.0                # well inside the bare barrel, clear of the boss
saddle_x0 = saddle_x1 - saddle_w
saddle_bore_r = barrel_r + bed
saddle_half_y = saddle_bore_r + wall
saddle_lead = 2.0                            # 45° lead-in on the bore's top rim

# --- the feet ---------------------------------------------------------------
# Each foot is a horizontal web off the spine plate to the enclosure's front wall
# and a flange up its inner face, two M3 screws per foot. The two feet straddle the
# pump's mass — one under the head, one under the saddle — so the motor's cantilever
# lands in a foot instead of in the spine. The flange carries CLEARANCE holes and
# the wall carries the heat-set inserts, so the screw drives from inside the cabinet
# and no fastener breaks the front face the display and the spout share.
foot_w = 16.0
foot_head_x = 18.0
flange_h = 30.0
gusset_t = 6.0
screw_clear_dia = 3.4                        # M3 shank clearance through the flange
screw_pitch = 18.0                           # the two screws' vertical spacing
screw_lower_z = plate_bottom_z + 7.0
foot_saddle_x = saddle_x0 + (saddle_w - foot_w) / 2.0

# --- what the geometry must satisfy -----------------------------------------
if shelf_z >= head_half:
    raise ValueError(
        f"shelf_z {shelf_z:g} reaches the head's top face ({head_half:.2f} mm), where the outlet "
        f"elbows stand and overhang the head's sides — the side walls must top out below it")
_bare_front = (elbow_x + elbow_r + fit, end_face_x)
_bare_rear = (0.0, elbow_x - elbow_r - fit)
for _station, _x0 in LATCH_STATION.items():
    _band = _bare_front if _station == "front" else _bare_rear
    if not (_band[0] <= _x0 and _x0 + tongue_w <= _band[1]):
        raise ValueError(
            f"the {_station} latch station spans x[{_x0:.2f}, {_x0 + tongue_w:.2f}], outside the "
            f"bare band x[{_band[0]:.2f}, {_band[1]:.2f}] the head's top face leaves beside the "
            f"outlet-elbow station (x {elbow_x:g} ± {elbow_r:.2f}) — its ledge and tab would land "
            f"under a collet")
if tab_y - tab_grip <= 0.0:
    raise ValueError(
        f"the tab's inboard face reaches y {tab_y - tab_grip:.2f}, past the pump's centre plane — "
        f"the two tabs would meet over the head instead of leaving a finger between them")
if tab_top_z >= elbow_leg_underside_z - 1.0:
    raise ValueError(
        f"the tab tops reach z {tab_top_z:.2f}, into the outlet elbows' free legs sweeping the air "
        f"over the head at z {elbow_leg_underside_z:g} — keep the whole latch stack a clearance "
        f"below them")
if stop_half_y >= boss_half or seat_z + stop_h >= -boss_half:
    raise ValueError(
        f"the rear stop rib ({stop_half_y:g} mm half-width, {stop_h:g} mm off the seat) reaches "
        f"inside the {boss_half:g} mm boss behind the bracket face, whose outline no drawing "
        f"pins — keep it in the seat's corner")
if not (barrel_west <= saddle_x0 and saddle_x1 <= barrel_east):
    raise ValueError(
        f"the saddle spans x[{saddle_x0:.2f}, {saddle_x1:.2f}], outside the bare-barrel band "
        f"x[{barrel_west:.2f}, {barrel_east:.2f}] the mock and the datasheet agree on")


# --- primitives -------------------------------------------------------------

def _box(x, y, z):
    """Axis-aligned box from three (lo, hi) ranges in the mount's own frame."""
    return (cq.Workplane("XY")
            .box(x[1] - x[0], y[1] - y[0], z[1] - z[0], centered=False)
            .translate((x[0], y[0], z[0])).val())


def _section(profile, x0, length):
    """A (y, z) polygon in the mount's YZ section, extruded `length` along +X."""
    return (cq.Workplane("YZ", origin=(x0, 0, 0))
            .polyline(profile).close().extrude(length).val())


def _xcyl(r, x0, x1):
    """Cylinder on the pump's own axis."""
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def _both_sides(solid):
    """The solid and its mirror across the pump's centre plane."""
    return solid.fuse(solid.mirror("XZ"))


# --- the socket -------------------------------------------------------------

def build_spine():
    """The plate the whole mount stands on: the head's seat, run aft under the
    saddle. The one member both feet and both socket walls share. Aft of the socket
    it carries only the saddle and the aft foot — both on the front half — and the
    source-select tray's front columns come down into the band its +Y edge would
    otherwise cross, so there it stops at the saddle's own width."""
    seat = _box((stop_face_x - stop_t, end_wall_x), (-socket_outer_y, socket_outer_y),
                (plate_bottom_z, seat_z))
    aft = _box((saddle_x0, stop_face_x - stop_t), (-socket_outer_y, saddle_half_y),
               (plate_bottom_z, seat_z))
    return seat.fuse(aft)


def build_socket_walls(tongue_x0):
    """The two side walls, each carrying its latch tongue on up off the shelf. Their
    inner faces are the head's side-face slip fit, and their shear across the head's
    width is the rotor's torque reaction."""
    slab = _box((stop_face_x - stop_t, end_face_x), (socket_inner_y, socket_outer_y),
                (seat_z, shelf_z))
    tongue = _box((tongue_x0, tongue_x0 + tongue_w), (socket_inner_y, socket_outer_y),
                  (shelf_z, tongue_top_z))
    return _both_sides(slab.fuse(tongue))


def build_end_wall():
    """The head's front-face stop. It spans only the head's own width, so the two
    latch tongues either side of it stay free of it."""
    return _box((end_face_x, end_wall_x), (-head_half, head_half), (seat_z, shelf_z))


def build_stop_rib():
    """The head's rear-face stop — a low rib in the seat's corner, outside the boss
    behind the bracket face."""
    return _box((stop_face_x - stop_t, stop_face_x), (-stop_half_y, stop_half_y),
                (seat_z, seat_z + stop_h))


# --- the latch --------------------------------------------------------------

def build_latch(tongue_x0):
    """Per tongue: the FLAT ledge that returns over the head's top face with the
    lead-in ramp above it that the descending head rides out on, and the finger tab
    the release is pushed on — carried inboard on a short arm, over the head, with a
    flare at its top so a fingertip does not slide off. The tongue body itself is
    grown in `build_socket_walls`."""
    ledge = _section([(ledge_tip_y, ledge_z),
                      (socket_outer_y, ledge_z),
                      (socket_outer_y, ledge_z + ledge_t),
                      (ledge_tip_y + ledge_t, ledge_z + ledge_t)], tongue_x0, tongue_w)
    arm = _box((tongue_x0, tongue_x0 + tongue_w), (tab_y, socket_outer_y),
               (tongue_top_z, tongue_top_z + tab_arm_t))
    tab = _section([(tab_y, tongue_top_z + tab_arm_t),
                    (tab_y + wall, tongue_top_z + tab_arm_t),
                    (tab_y + wall, tab_top_z),
                    (tab_y - tab_grip, tab_top_z),
                    (tab_y, tab_top_z - 2.0 * tab_grip)], tongue_x0, tongue_w)
    return _both_sides(ledge.fuse(arm).fuse(tab))


# --- the saddle -------------------------------------------------------------

def build_saddle():
    """The open half-round under the motor barrel: the pump's second support, and
    the reason the socket does not carry the motor's cantilever alone."""
    block = _box((saddle_x0, saddle_x1), (-saddle_half_y, saddle_half_y), (seat_z, 0.0))
    mouth = _box((saddle_x0 - 1.0, saddle_x1 + 1.0), (-saddle_bore_r, saddle_bore_r), (0.0, 1.0))
    lead = _section([(saddle_bore_r, 0.0),
                     (saddle_bore_r + saddle_lead, 0.0),
                     (saddle_bore_r, -saddle_lead)], saddle_x0 - 1.0, saddle_w + 2.0)
    return (block
            .cut(_xcyl(saddle_bore_r, saddle_x0 - 1.0, saddle_x1 + 1.0))
            .cut(mouth)
            .cut(_both_sides(lead)))


# --- the feet ---------------------------------------------------------------

def build_feet(standoff):
    """The two front-wall feet. `standoff` is the pump axis's distance from the
    enclosure interior's front face — the one number that differs between the two
    mounts, because the row's two poses sit at different Y."""
    wall_face_y = -standoff
    feet = None
    for foot_x in (foot_head_x, foot_saddle_x):
        span = (foot_x, foot_x + foot_w)
        web = _box(span, (wall_face_y, -socket_outer_y), (plate_bottom_z, seat_z))
        flange = _box(span, (wall_face_y, wall_face_y + wall),
                      (plate_bottom_z, plate_bottom_z + flange_h))
        gusset = _section([(wall_face_y + wall, seat_z),
                           (wall_face_y + wall, plate_bottom_z + flange_h),
                           (-socket_outer_y, seat_z)],
                          foot_x + (foot_w - gusset_t) / 2.0, gusset_t)
        foot = web.fuse(flange).fuse(gusset)
        for i in range(2):
            foot = foot.cut(cq.Solid.makeCylinder(
                screw_clear_dia / 2.0, wall + 1.0,
                cq.Vector(foot_x + foot_w / 2.0, wall_face_y - 0.5,
                          screw_lower_z + i * screw_pitch),
                cq.Vector(0, 1, 0)))
        feet = foot if feet is None else feet.fuse(foot)
    return feet


# --- the mount --------------------------------------------------------------

def build(standoff, station):
    tongue_x0 = LATCH_STATION[station]
    return cq.Workplane(obj=build_spine()
                        .fuse(build_socket_walls(tongue_x0))
                        .fuse(build_end_wall())
                        .fuse(build_stop_rib())
                        .fuse(build_latch(tongue_x0))
                        .fuse(build_saddle())
                        .fuse(build_feet(standoff)))


# The two mounts differ in exactly two numbers, both of them consequences of where
# the row's two poses sit under the Zone-C top-wall opening (x 119.5…268, y 19…166,
# `enclosure._hopper_hole`):
#
#   standoff — the pump axis's distance from the interior's front face
#              (`enclosure._dims()` inner y0 = −3.0), which the feet reach across:
#                a: (PUMP_A_POS y − the pump's own axis offset) + 3.0 = 96.00 − 35.0 + 3.0
#                b: (PUMP_B_POS y − the pump's own axis offset) + 3.0 = 85.51 − 35.0 + 3.0
#   station  — which bare band of the head's top face carries the latch. P-A's motor
#              end runs 107.9 mm west of the opening, so only its FRONT band lies
#              under it; P-B's head front face runs 3.4 mm east of the opening, so
#              only its REAR band does. The station is where a finger can reach.
MOUNTS = {"a": (64.00, "front"), "b": (53.51, "rear")}

PETG_FLEX_MODULUS = 2000.0      # MPa, short-term
PLASTIC_FRICTION = 0.30         # PETG on the head's ABS


def latch_numbers(modulus=PETG_FLEX_MODULUS):
    """First-order snap numbers for the pair of tongues, each read as a straight
    cantilever of its free length and section: `(insert_N, spread_N, strain_pct)`
    — the peak push to drive the head past both lead-in ramps, the fingertip
    force at one tab that spreads it clear, and the peak bending strain at the
    tongue root while the head passes. Retention itself is not a force in this
    list: the ledge is FLAT, so a lift puts it in shear rather than camming the
    tongue open, and the pump cannot leave until the tabs are spread."""
    free_len = tongue_top_z - tongue_root_z
    inertia = tongue_w * wall ** 3 / 12.0
    at_ledge = 3.0 * modulus * inertia * latch_spread / free_len ** 3
    # The tab is pushed at mid-height, on an arm off the tongue's top — so the lever
    # a finger works is the tongue plus half the tab.
    push_len = tongue_top_z + tab_arm_t + tab_h / 2.0 - tongue_root_z
    at_tab = 3.0 * modulus * inertia * latch_spread / push_len ** 3
    ramp = 1.0                                               # tan of the 45° lead-in off the insertion axis
    insert = 2.0 * at_ledge * (ramp + PLASTIC_FRICTION) / (1.0 - PLASTIC_FRICTION * ramp)
    strain = 3.0 * wall * latch_spread / (2.0 * free_len ** 2) * 100.0
    return insert, at_tab, strain


def main():
    insert, spread, strain = latch_numbers()
    for side, (standoff, station) in MOUNTS.items():
        mount = build(standoff, station)
        out = _here.parent / f"pump-mount-{side}.step"
        export_step(mount, str(out))
        b = mount.val().BoundingBox()
        print(f"-> {out.name}")
        print(f"   envelope  x[{b.xmin:7.2f},{b.xmax:7.2f}] y[{b.ymin:7.2f},{b.ymax:7.2f}] "
              f"z[{b.zmin:7.2f},{b.zmax:7.2f}]   (local; origin on the pump axis at the bracket face)")
        print(f"   print     {b.xlen:.1f} mm tall on a {b.ylen:.1f} × {b.zlen:.1f} mm bed face, "
              f"build direction +X, volume {mount.val().Volume() / 1000.0:.1f} cm³")
        print(f"   latch     {station} station, tongues at x"
              f"[{LATCH_STATION[station]:.2f}, {LATCH_STATION[station] + tongue_w:.2f}], "
              f"tabs at |y| {tab_y - tab_grip:.2f}…{tab_y + wall:.2f}")
    print(f"   socket    {2 * head_half:.2f} mm square seat, walls to z {shelf_z:g}, "
          f"stops at x {stop_face_x:g} and {end_face_x:.2f} ({fit_x * 2:g} mm axial float); "
          f"the pump is free of it {clear_lift:.2f} mm up")
    print(f"   latch     {latch_spread:.2f} mm spread, {insert:.1f} N to press the head in, "
          f"{spread:.1f} N at a tab to release, {strain:.2f}% peak strain, flat ledge in shear")
    print(f"   saddle    Ø{2 * saddle_bore_r:.2f} bore on the Ø{2 * barrel_r:.2f} barrel, "
          f"x[{saddle_x0:.2f}, {saddle_x1:.2f}] inside the bare band "
          f"x[{barrel_west:.2f}, {barrel_east:.2f}]")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "MOUNT_SEAT": f"{2 * head_half:.2f} mm",
            "MOUNT_LIFT": f"{clear_lift:.2f} mm",
            "MOUNT_FIT": f"{fit:g} mm",
            "MOUNT_FLOAT": f"{fit_x * 2:g} mm",
            "MOUNT_SPREAD": f"{latch_spread:.2f} mm",
            "MOUNT_INSERT": f"{insert:.0f} N",
            "MOUNT_RELEASE": f"{spread:.1f} N",
            "MOUNT_STRAIN": f"{strain:.2f}%",
            "MOUNT_LANE": f"{2 * (tab_y - tab_grip):.0f} mm",
            "MOUNT_SADDLE": f"{2 * barrel_r:.2f} mm",
            "MOUNT_SCREWS": "4",
        },
        expected_counts={"MOUNT_SEAT": 1, "MOUNT_LIFT": 2, "MOUNT_FIT": 1, "MOUNT_FLOAT": 1,
                         "MOUNT_SPREAD": 1, "MOUNT_INSERT": 1, "MOUNT_RELEASE": 1,
                         "MOUNT_STRAIN": 1, "MOUNT_LANE": 1, "MOUNT_SADDLE": 1,
                         "MOUNT_SCREWS": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
