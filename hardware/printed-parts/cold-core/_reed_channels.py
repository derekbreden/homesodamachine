"""Reed-and-cable channel system for level sensing — built into the
foam shell on the outer face of each bag-pocket far ±X wall."""

from _cold_core_interface import (
    wall_and_floor_thickness,
    foam_shell_outer_height,
    bag_pocket_outermost_x,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    bulkhead_elbow_exit_z,
    cap_conduits,
    cap_conduit_shell_xy,
    lldpe_tube_od,
    port_hole_radius,
    reed_x_depth,
    reed_y_half_w,
    level_rod_y,
    make_box,
    pour_band_pocket_punch,
    cut_pour_band_pass_through,
    bound,
)

w = wall_and_floor_thickness

# Reed switches per reservoir, level-sensing fuel gauge — see
# `reservoir/level-sensing.md`.
reeds_per_reservoir = 4

# Reed channel cavity is open through the top of the foam shell; reeds
# drop in from above before the lid goes on. Cavity depth (reed_x_depth) is
# shared via the interface — the outer_shell X width is sized to butt it.

# The reservoir's own ROD_POSITION_Y: reeds sit opposite the float-on-rod
# across the bag-pocket wall, so this is not a second station that has to be
# kept level with that one — it IS that one (`_cold_core_interface.level_rod_y`).
reed_y_center = level_rod_y

# Cavity rests on the foam-shell floor at z=w; envelope bottom at z=0.
# Open through the cap to full outer height: the pre-soldered reed
# column drops in before the cap is installed.
reed_cavity_z_range = (w, foam_shell_outer_height)
reed_envelope_z_range = (0, foam_shell_outer_height)

reed_cavity_y_range = (reed_y_center - reed_y_half_w, reed_y_center + reed_y_half_w)
reed_envelope_y_range = (reed_cavity_y_range[0] - w, reed_cavity_y_range[1] + w)

# THE CAVITY IS A VOID AND SO IS A LINE'S BAND, and where the two overlap nothing collides
# — which is why this fence is arithmetic and not a probe. The reed channel stands in the
# FORWARD BAND (`_cold_core_interface.forward_band_width`), the same strip three cap conduits
# drop their lines into, and it runs the shell's full height. A line falling into the cavity
# instead of the band lands on the reed column, reads clear in every solid check in the tree,
# and is only wrong on the bench.
#   So every conduit is priced against both channels here, in plan: the tube's own SECTION
# stands clear of the envelope, which is the channel's cavity and the printed wall around it
# together. Clear of the envelope is clear of the cavity, because that wall is what separates
# them. A FILL is priced by the same rule — it stands over a pocket and the channel stands on
# that pocket's own far wall.
reed_line_clearance = lldpe_tube_od / 2.0

# THE TWO CONDUITS THAT ARE OVER A CHANNEL ON PURPOSE, as `conduit -> the side whose channel it
# stands on`. What comes down every other bore is a line, and a line over a cavity is the failure
# the fence above catches; what comes UP these two is that channel's own reed cable, so standing
# off its channel is the one thing either of them must not do. The pairing is data so the machine
# can refuse it: `reed_cable_conduits_stand_over_their_own` holds each to the side it names.
REED_CABLE_CONDUITS = {"reed-cable-a": +1, "reed-cable-b": -1}


def reed_channel_plan_room(x, y):
    """How far a line at plan `(x, y)` stands off the nearer reed channel envelope, and
    which side's it is: `(mm, side)`. Negative means it is inside one."""
    room = []
    for s in (+1, -1):
        env_x = sorted((s * bag_pocket_outermost_x, s * (bag_pocket_outermost_x + reed_x_depth + w)))
        dx = max(env_x[0] - x, x - env_x[1])
        dy = max(reed_envelope_y_range[0] - y, y - reed_envelope_y_range[1])
        room.append((max(dx, dy), f"reservoir {'AB'[s < 0]}'s reed channel"))
    return min(room)


_reed_clear = bound(
    "reed-channel-clear", "Every conduit's line falls clear of both reed channels",
    f"{reed_line_clearance:g} mm off the nearer channel")
for _name in cap_conduits:
    if _name in REED_CABLE_CONDUITS:
        continue
    _room, _what = reed_channel_plan_room(*cap_conduit_shell_xy(_name))
    _reed_clear(
        _room >= reed_line_clearance - 1e-9,
        f"cap conduit {_name}: the line coming down it stands {_room:.3f} mm off "
        f"{_what}, inside the {reed_line_clearance:g} mm a ⌀{lldpe_tube_od:g} tube's own "
        f"section takes — a line over a reed cavity is a void meeting a void and collides "
        f"with nothing")


# WHAT THE BORE OWES THE CAVITY IS AN OPENING, not containment: the bore is wider than the
# channel is deep, so it stands proud of it in X however it is placed, and the mouth the cable
# comes up is what the two SHARE. Half the bore's own width on each axis is the fence — at that
# the bore lands squarely on the cavity, and under it the two are clipping corners and the mouth
# closes on a crescent no cable is threaded through.
reed_cable_mouth_min = port_hole_radius

_reed_cable_over = bound(
    "reed-cable-conduit-stands-over-its-channel",
    "Every reed-cable conduit opens on the channel its own cable climbs",
    f"{reed_cable_mouth_min:g} mm of shared mouth on each axis")
for _name, _side in sorted(REED_CABLE_CONDUITS.items()):
    if _name not in cap_conduits:
        raise ValueError(
            f"`REED_CABLE_CONDUITS` names {_name!r} as the bore reservoir "
            f"{'AB'[_side < 0]}'s cable leaves by, and the cap carries no conduit by that name "
            f"— the exemption above is what is still holding it out of `reed-channel-clear`.")
    _x, _y = cap_conduit_shell_xy(_name)
    _cav_x = sorted((_side * bag_pocket_outermost_x,
                     _side * (bag_pocket_outermost_x + reed_x_depth)))
    _cav_y = reed_cavity_y_range
    _mouth_x = min(_cav_x[1], _x + port_hole_radius) - max(_cav_x[0], _x - port_hole_radius)
    _mouth_y = min(_cav_y[1], _y + port_hole_radius) - max(_cav_y[0], _y - port_hole_radius)
    _reed_cable_over(
        min(_mouth_x, _mouth_y) >= reed_cable_mouth_min - 1e-9,
        f"reed-cable conduit {_name}: its bore at ({_x:.3f}, {_y:.3f}) and reservoir "
        f"{'AB'[_side < 0]}'s cavity share a mouth {_mouth_x:.3f} {chr(215)} {_mouth_y:.3f} mm "
        f"— the cable comes up the cavity and leaves by this bore, and what the two do not "
        f"share is solid shell over the channel")


def build_reed_channels(side):
    """Reed channel for one ±X reservoir: a Z-slot envelope on the outer
    face of the bag-pocket far ±X wall with the reed cavity carved out,
    new wall material to union with the foam shell.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall

    reed_envelope_x_range = (bag_x, bag_x + s * (reed_x_depth + w))
    reed_cavity_x_range = (bag_x, bag_x + s * reed_x_depth)

    reed_envelope = make_box(reed_envelope_x_range, reed_envelope_y_range, reed_envelope_z_range)
    reed_cavity = make_box(reed_cavity_x_range, reed_cavity_y_range, reed_cavity_z_range)
    return reed_envelope.cut(reed_cavity)


def cut_reed_channel_openings(foam_shell):
    """Cut the bag-pocket far ±X wall in the reed channel footprint: the
    channel opens to the bag-pocket interior on its back face, shortening
    the magnet-to-reed magnetic path across the wall."""
    for s in (+1, -1):
        wall_x_outer = s * bag_pocket_outermost_x
        wall_x_inner = wall_x_outer - s * w
        reed_opening = make_box((wall_x_inner, wall_x_outer), reed_cavity_y_range, reed_cavity_z_range)
        foam_shell = foam_shell.cut(reed_opening)
    return foam_shell


# A CABLE LEAVES BY THE TOP OF THE SLOT IT IS ALREADY IN. The channel is open from the shell's
# floor to its top face, so the column's own cavity is the whole of the run: the cable rises the
# way it was laced and meets the bore the cap stands over that mouth
# (`_cold_core_interface.reed_cable_conduit_xy`). Nothing crosses a pocket wall, nothing runs the
# port lane, and no bore is struck in the face the refrigeration base is mated to.
