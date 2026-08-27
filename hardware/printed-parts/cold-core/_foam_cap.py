"""Foam cap stack: a cup at each end of the shell (the foam pour tray), the lid that closes its
mouth during the pour, and the TPU 90A gasket that rings the cup's mating edge against the
outer shell's face. The two ends are the same cup and the same plate divided differently — the
top lid is solid to its full height and its cup one head pad shorter for it."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    outer_shell_wall,
    outer_shell_x_length,
    outer_shell_y_length,
    corner_round_radius,
    cap_conduits,
    cap_conduit_bore_radius,
    cap_conduit_boss_radius,
    cap_conduit_entry_relief_radius,
    foam_cap_height,
    foam_shell_outer_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_cap_lid_pour_xy,
    foam_cap_lid_vent_xy,
    attachment_xy_positions,
    screw_clearance_radius,
    head_cbore_radius,
    head_cbore_depth,
    head_pad_height,
    head_pad_slip,
    foam_cap_lid_height,
    gasket_thickness,
    gasket_strip_width,
)
from _outer_shell import build_attachment_bosses, take_skin_off_the_floor

# A lid stands one wall of plate over a head pad's own height, and the two ends of the stack
# reach it differently. The BOTTOM lid is that plate with a pad at each of the six stations. The
# TOP lid is SOLID to the same height over its whole footprint: it is the plate the service bay
# stands on, and a plate with pads under it has no face to print on.
lid_total_height = foam_cap_lid_height
lid_cut_through_depth = lid_total_height + wall_and_floor_thickness

# THE TWO CUPS ARE NOT THE SAME HEIGHT. The bottom cup stands the whole `foam_cap_height` and
# its lid's pads sink into the relief its boss columns leave at the mouth. The top cup stops one
# pad short of that, because the band is its lid's: what would have been the cup's last
# `head_pad_height` of wall is plate, and the foam behind it gives it up. The stack is the same
# height either way, and so is the section a clamp screw crosses.
top_cap_height = foam_cap_height - head_pad_height

# --- the two planes outside the stack answers to ---------------------------
#
# THE STACK'S FLOOR is the bottom lid's outer face, the most-negative-Z layer, which is what the
# appliance stands the whole core on.
#   THE CAP FACE is the top lid's outer face — the plane every body on the core's crown is placed
# off, and the plane a cap conduit's bore opens on. It is NOT the stack's highest point and must
# not be read as one: the valve cradles (`_cold_core_interface.cap_cradles`) stand off that face,
# so the assembly's box top is a cradle pad, and a body seated on it would stand on a valve seat.
#
# Both are arithmetic over the lid this module makes and the two heights the interface states, so
# they live beside the lid. `foam_assembly` re-exports them for the appliance and
# `_internal_routes` ends every riser on the cap face, which is where the machine's own run to
# that conduit begins.
stack_floor_z = -(foam_cap_height + wall_and_floor_thickness)
cap_face_z = foam_shell_outer_height + top_cap_height + lid_total_height


def attachment_clearances_extrude(height):
    """Screw-clearance cylinders at every attachment position, extruded +Z by height."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(attachment_xy_positions)
        .circle(screw_clearance_radius)
        .extrude(height)
    )


def build_conduit_columns(height):
    """Every cap conduit's column, extruded +Z by height from z=0.

    ONE EXTRUDE PER CONDUIT, unioned. A bore's wall is thicker than half the `LINE_PITCH`
    its neighbour stands at, so a pair of conduits carries bosses that OVERLAP — and two
    overlapping wires pushed through a single extrude close one self-intersecting face,
    not a fused pair. Unioning the columns one at a time is what makes them the single
    peanut-section post the pour and the lid actually meet."""
    columns = None
    for centre in cap_conduits.values():
        column = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=0)
            .moveTo(centre)
            .circle(cap_conduit_boss_radius)
            .extrude(height)
        )
        columns = column if columns is None else columns.union(column)
    return columns


def build_conduit_bores(height, radius=cap_conduit_bore_radius, overshoot=0.0):
    """Every cap conduit's bore, extruded +Z by height from z=0.

    `overshoot` starts the cut that far BELOW the floor and lengthens it to match. A bore
    whose start face is coincident with the floor's own outer face leaves the cut sharing a
    plane with the solid it is cutting, and where the column it runs up is FUSED INTO THE
    PERIMETER WALL — three faces meeting on that plane instead of two — the cut lands in
    the cavity and leaves the floor under it standing. Starting off the plane is what makes
    it a through-cut."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-overshoot)
        .pushPoints(list(cap_conduits.values()))
        .circle(radius)
        .extrude(height + overshoot)
    )


def build_conduit_entry_reliefs(z_inner):
    """Every conduit's countersink in the LID, lofted from the bore's own radius at `z_inner`
    — one wall under the outer face — out to `cap_conduit_entry_relief_radius` at that face,
    which is where a line leaves.

    ONE LOFT PER CONDUIT, unioned. `build_conduit_bores` pushes its points through a single
    extrude; a loft runs between two wires and takes one station at a time."""
    cones = None
    for centre in cap_conduits.values():
        cone = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=z_inner)
            .moveTo(centre)
            .circle(cap_conduit_bore_radius)
            .workplane(offset=wall_and_floor_thickness)
            .moveTo(centre)
            .circle(cap_conduit_entry_relief_radius)
            .loft(ruled=True)
        )
        cones = cone if cones is None else cones.union(cone)
    return cones


def build_foam_cap(open_down=False):
    """The foam-pour cup. Default opens +Z (floor on the bottom, mouth up) —
    the top cap. open_down=True shells the other face so the cup opens −Z
    (floor on top, mouth down): the bottom cap, seated floor-up against the
    shell's bottom face with its open mouth + lid as the most-negative-Z
    layer. Same footprint and same six-screw clearance pattern either way, so
    the mouth-down bottom cap lands its screws on the shell's existing bosses.

    EACH CUP IS AS TALL AS ITS OWN LID LEAVES IT. The bottom cup stands the whole
    `foam_cap_height` and its six boss columns stop `head_pad_height` short of the mouth: that
    relief is where the bottom lid's head pads go, and the slip it carries is what lets them in.
    The TOP cup stands `top_cap_height` and takes no relief — its lid is solid to the plane the
    pads would have stood on, so every column runs to the rim and the lid's flat underside lands
    on all of them at once.

    A CONDUIT column runs the full height to the mouth rim, where the lid's plate lands on
    it, and carries a ⌀[6.5 mm](FCAP_BORE_D) bore through itself and the floor under it. Only
    the mouth-up top cap has them: `cap_conduits` is everything that leaves by the top —
    `cap_fluid_conduits` and a reed cable apiece in the other two — and the service bay is on
    the top cap's outer face."""
    height = foam_cap_height if open_down else top_cap_height
    cap = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(height)
        .edges("|Z")
        .fillet(corner_round_radius)
        .faces("<Z" if open_down else ">Z")
        # The cap's wall carries the same show skin as the shell it stacks on, so it stands on
        # the same section (`outer_shell_wall`) and its pour tray gives up the difference.
        .shell(-outer_shell_wall)
    )
    # The cap's floor takes none of the skin's stock either, and it is at whichever end the
    # cup is not open on — the mouth-down cap carries its floor on top.
    cap = take_skin_off_the_floor(
        cap,
        *((height - outer_shell_wall, height - wall_and_floor_thickness)
          if open_down else (wall_and_floor_thickness, outer_shell_wall)))
    # Same ⌀ boss + teardrop webs as the outer shell.
    cap = cap.union(build_attachment_bosses(height))
    if open_down:
        # The mouth-end relief: the bottom lid's pad section, one slip larger all round,
        # standing on the mouth at z=0 because that is the material side of a mouth-down cup.
        cap = cap.cut(build_attachment_bosses(head_pad_height, oversize=head_pad_slip))
    else:
        cap = cap.union(build_conduit_columns(height))
    # Screw clearance passes the full cap height, floor through to mating edge.
    cap = cap.cut(attachment_clearances_extrude(height))
    if not open_down:
        cap = cap.cut(build_conduit_bores(height, overshoot=wall_and_floor_thickness))
    return cap.unwrap()


def build_foam_cap_lid(open_down=False):
    """The pour lid for the cap built with the same `open_down` — the plate that closes
    its mouth. Authored mouth-facing-side-down either way, so z=0 is the face that lands on the
    cup and `lid_total_height` is the outer face a counterbore is sunk from; the head lands
    head_seat_recess under a face that is otherwise a plane.

    ONE HEIGHT, TWO PLATES. The bottom lid is one wall of plate with a head pad standing off its
    mouth-facing side at each of the six stations, into the relief its cup leaves. The TOP lid is
    that height SOLID over the whole footprint — the pads are the plate, its underside is one
    plane, and the band they stood in is wall its cup does not carry."""
    plate_height = wall_and_floor_thickness if open_down else lid_total_height
    cbore_z0 = 0.0 if open_down else lid_total_height - head_cbore_depth

    lid = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(plate_height)
        .edges("|Z")
        .fillet(corner_round_radius)
    )
    if open_down:
        # The pads are the cap boss's own section — what its columns gave up.
        lid = lid.union(build_attachment_bosses(head_pad_height).translate(
            (0, 0, wall_and_floor_thickness)))
    head_cbores = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=cbore_z0)
        .pushPoints(attachment_xy_positions)
        .circle(head_cbore_radius)
        .extrude(head_cbore_depth)
    )

    # Pour hole on the +X half, off the centreline by whatever the deck-mount stations and
    # the valve cradles there leave it (`foam_cap_lid_pour_xy`); vent holes mirrored across y
    # at the −X corners, where nothing stands.
    pour_xy = foam_cap_lid_pour_xy()
    vent_plus_y_xy, vent_minus_y_xy = foam_cap_lid_vent_xy()

    def cut_hole(anchor_xy, radius):
        return (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=0)
            .moveTo(anchor_xy)
            .circle(radius)
            .extrude(lid_cut_through_depth)
        )

    pour_hole = cut_hole(pour_xy, foam_cap_lid_pour_radius)
    vent_hole_plus_y = cut_hole(vent_plus_y_xy, foam_cap_lid_vent_radius)
    vent_hole_minus_y = cut_hole(vent_minus_y_xy, foam_cap_lid_vent_radius)
    clearances = attachment_clearances_extrude(lid_cut_through_depth)
    lid = (
        lid.cut(pour_hole)
        .cut(vent_hole_plus_y)
        .cut(vent_hole_minus_y)
        .cut(head_cbores)
        .cut(clearances)
    )
    # The conduit's bore continues through the plate the column's top lands on — the whole of
    # it, the column's own axis carried straight up through the lid — and opens on the outer
    # face into the `cap_conduit_entry_skew` countersink the line leaves by, one wall deep. The
    # mouth-down bottom lid closes the stack's other end and takes neither.
    if not open_down:
        lid = lid.cut(build_conduit_bores(lid_cut_through_depth))
        lid = lid.cut(build_conduit_entry_reliefs(lid_total_height - wall_and_floor_thickness))
    return lid.unwrap()


def build_foam_cap_gasket():
    """TPU 90A gasket between foam_cap mating edge and outer_shell mating
    face. Rounded-corner perimeter ring matching the shell's rounded outer
    wall, ring width uniform through the corner, + a boss-shaped pad
    (same boss + teardrop-web shape as the shell/cap) at each of the 6 screw
    positions. Printed twice."""
    outer = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(gasket_thickness)
        .edges("|Z")
        .fillet(corner_round_radius)
    )
    inner = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(
            outer_shell_x_length - 2 * gasket_strip_width,
            outer_shell_y_length - 2 * gasket_strip_width,
        )
        .extrude(gasket_thickness)
        .edges("|Z")
        .fillet(corner_round_radius - gasket_strip_width)
    )
    gasket = outer.cut(inner)
    pads = build_attachment_bosses(gasket_thickness)
    holes = attachment_clearances_extrude(gasket_thickness)
    return gasket.union(pads).cut(holes).unwrap()
