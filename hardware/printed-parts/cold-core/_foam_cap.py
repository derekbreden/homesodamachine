"""Foam cap stack: a cup at each end of the shell (the foam pour tray) and its pour lid.
Rigid seats have their printed-face allowances; exterior foil tape seals the dry seams.
The two ends are the same cup and the same plate divided differently — the
top lid is solid to its full height and its cup one head pad shorter for it."""

import math
import cadquery as cq
from world_workplane import WorldWorkplane, xy_plane_z_up
import fits
from _cold_core_interface import (
    wall_and_floor_thickness,
    wall_thickness,
    outer_shell_wall,
    outer_shell_x_length,
    outer_shell_y_length,
    corner_round_radius,
    screw_boss_size,
    cap_conduits,
    cap_conduit_floor_xy,
    cap_passive_guides,
    cap_cable_guides,
    cap_conduit_bore_radius,
    cap_conduit_boss_radius,
    cap_conduit_links,
    cap_conduit_link_width,
    cap_conduit_entry_relief_radius,
    foam_cap_height,
    foam_shell_outer_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_cap_lid_pour_xy,
    foam_cap_lid_vent_xy,
    attachment_xy_positions,
    attachment_stations,
    cap_shell_clearance,
    cap_lid_clearance,
    screw_clearance_radius,
    head_cbore_radius,
    head_cbore_depth,
    head_pad_height,
    head_pad_slip,
    foam_cap_lid_height,
)
from _outer_shell import build_attachment_bosses, trim_cup_floor
import _above_core_mounts as _above_mounts

# A lid stands one wall of plate over a head pad's own height, and the two ends of the stack
# reach it differently. The BOTTOM lid is that plate with a pad at each attachment station. The
# TOP lid is SOLID to the same height over its whole footprint: it is the plate the service bay
# stands on, and a plate with pads under it has no face to print on.
lid_total_height = foam_cap_lid_height
lid_cut_through_depth = lid_total_height + wall_and_floor_thickness
# The lower lid's open head pockets retain the casing's full 2.38 mm inward stock.
head_pad_growth = max(0.0, head_cbore_radius + wall_thickness - screw_boss_size / 2)

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
# not be read as one: V-B's upright wall and the water-check saddle stand off
# that face, so the assembly's box top is an equipment mount.
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
    """Cap guide columns and the floor-rooted curved soda sleeve.

    ONE EXTRUDE PER CONDUIT, unioned. A bore's wall is thicker than half the `LINE_PITCH`
    its neighbour stands at, so a pair of conduits carries bosses that OVERLAP — and two
    overlapping wires pushed through a single extrude close one self-intersecting face,
    not a fused pair. Unioning the columns one at a time is what makes them the single
    peanut-section post the pour and the lid actually meet."""
    columns = None
    for name, centre in cap_conduits.items():
        if name in ('reservoir-b-fill', 'water-in', 'carb-water-out'):
            continue
        if (name in cap_passive_guides or name in cap_cable_guides) and math.dist(centre, cap_conduit_floor_xy[name]) > 1.e-8:
            if name in cap_cable_guides:
                points = _above_mounts.cable_guide_points(name)['points_mm'][1:-1]
                plan = [ _above_mounts.above_core.world_to_cap(p)[:2] for p in points]
            else:
                plan = (cap_conduit_floor_xy[name], centre)
            column = None
            for lower, upper in zip(plan, plan[1:]):
                dx, dy = upper[0]-lower[0], upper[1]-lower[1]
                segment = (cq.Workplane('XY')
                    .center((upper[0]+lower[0])/2., (upper[1]+lower[1])/2.)
                    .slot2D(math.hypot(dx, dy)+2.*cap_conduit_boss_radius,
                            2.*cap_conduit_boss_radius, math.degrees(math.atan2(dy, dx)))
                    .extrude(height))
                column = segment if column is None else column.union(segment)
        else:
            column = (
                WorldWorkplane(xy_plane_z_up)
                .workplane(offset=0)
                .moveTo(centre)
                .circle(cap_conduit_boss_radius)
                .extrude(height)
            )
        columns = column if columns is None else columns.union(column)
    # Simple full-height webs connect the two close pairs. The subsequent bore
    # cut keeps the passages open through the entire joined stock.
    for first, second in cap_conduit_links:
        a, b = cap_conduits[first], cap_conduits[second]
        dx, dy = b[0] - a[0], b[1] - a[1]
        link = (cq.Workplane("XY")
                .box(math.hypot(dx, dy), cap_conduit_link_width, height,
                     centered=(True, True, False))
                .rotate((0, 0, 0), (0, 0, 1), math.degrees(math.atan2(dy, dx)))
                .translate(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0)))
        columns = columns.union(link)
    carrier = _above_mounts.reservoir_b_fill_features(height)['cup_add']
    carrier = _above_mounts.world_shape_in_cap(carrier).translate((0., 0., height))
    soda = _above_mounts.soda_out_features()['cup_add']
    soda = _above_mounts.world_shape_in_cap(soda).translate((0., 0., height))
    return columns.union(carrier).union(soda)


def build_conduit_bores(height, radius=cap_conduit_bore_radius, overshoot=0.0,
                        frame='cup'):
    """Every cap conduit's bore, extruded +Z by height from z=0.

    `overshoot` starts the cut that far BELOW the floor and lengthens it to match. A bore
    whose start face is coincident with the floor's own outer face leaves the cut sharing a
    plane with the solid it is cutting, and where the column it runs up is FUSED INTO THE
    PERIMETER WALL — three faces meeting on that plane instead of two — the cut lands in
    the cavity and leaves the floor under it standing. Starting off the plane is what makes
    it a through-cut."""
    ordinary = [xy for name, xy in cap_conduits.items()
                if name not in ('reservoir-b-fill','water-in','carb-water-out') and
                (frame == 'lid' or name not in (*cap_passive_guides, *cap_cable_guides))]
    bores = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-overshoot)
        .pushPoints(ordinary)
        .circle(radius)
        .extrude(height + overshoot)
    )
    band = cq.Solid.makeBox(outer_shell_x_length+40., outer_shell_y_length+40.,
        height+overshoot+1., cq.Vector(-outer_shell_x_length/2.-20.,
                                    -outer_shell_y_length/2.-20.,-overshoot))
    if frame == 'cup':
        # Lower entries keep the existing reservoir bores. The shallow turns
        # finish above the cup and meet straight upper bores in the lid.
        from _internal_routes import routes, build_route, route_bend_radius
        for name in cap_passive_guides:
            passage = build_route(routes[name], route_bend_radius, radius)
            passage = (passage.rotate((0., 0., 0.), (0., 0., 1.), 180.)
                       .translate((0., 0., -foam_shell_outer_height)))
            bores = bores.union(passage.intersect(band))
        for name in cap_cable_guides:
            route = _above_mounts.cable_guide_points(name)
            passage = build_route(route['points_mm'], route['bend_radius_mm'], radius)
            passage = _above_mounts.world_shape_in_cap(passage).translate((0., 0., top_cap_height))
            bores = bores.union(passage.intersect(band))
    water_air = _above_mounts.world_shape_in_cap(_above_mounts.water_in_features()['cut'])
    if frame == 'cup':
        water_air = water_air.translate((0.,0.,top_cap_height))
    bores = bores.union(water_air.intersect(band))
    soda_air = _above_mounts.world_shape_in_cap(_above_mounts.soda_out_features()['cut'])
    if frame == 'cup':
        soda_air = soda_air.translate((0.,0.,top_cap_height))
    bores = bores.union(soda_air.intersect(band))
    fitting_air = _above_mounts.reservoir_b_fill_features(top_cap_height)['cut']
    fitting_air = _above_mounts.world_shape_in_cap(fitting_air)
    if frame == 'cup':
        fitting_air = fitting_air.translate((0., 0., top_cap_height))
    return bores.union(fitting_air.intersect(band))


def build_conduit_entry_reliefs(z_inner):
    """Leaning-line countersinks in the LID, lofted from the bore's own radius at `z_inner`
    — one wall under the outer face — out to `cap_conduit_entry_relief_radius` at that face,
    which is where a line leaves.

    ONE LOFT PER CONDUIT, unioned. `build_conduit_bores` pushes its points through a single
    extrude; a loft runs between two wires and takes one station at a time."""
    cones = None
    for name, centre in cap_conduits.items():
        # The shared sensor loom stays vertical until above the lid. Its
        # straight mouth needs no leaning-tube relief beside the earth boss.
        if name in ('reservoir-b-fill','water-in','sensor-cable'):
            continue
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
    layer. Same footprint and same screw-clearance pattern either way, so
    the mouth-down bottom cap lands its screws on the shell's existing bosses.

    EACH CUP IS AS TALL AS ITS OWN LID LEAVES IT. The bottom cup stands the whole
    `foam_cap_height` and its boss columns stop `head_pad_height` short of the mouth: that
    relief is where the bottom lid's head pads go, and the slip it carries is what lets them in.
    The TOP cup stands `top_cap_height` and takes no relief — its lid is solid to the plane the
    pads would have stood on, so every column runs to the rim and the lid's flat underside lands
    on all of them at once.

    A CONDUIT column runs the full height to the mouth rim, where the lid's plate lands on
    it, and carries a ⌀[7.5 mm](FCAP_BORE_D) bore through itself and the floor under it. Only
    the mouth-up top cap has them: `cap_conduits` is everything that leaves by the top —
    `cap_fluid_conduits`, the two reservoir reed cables and the internal sensor
    loom — and the service bay is on the top cap's outer face."""
    height = foam_cap_height if open_down else top_cap_height
    casing_stock = outer_shell_wall
    cap = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(height)
        .edges("|Z")
        .fillet(corner_round_radius)
        .faces("<Z" if open_down else ">Z")
        # The plain casing keeps the nominal standing-wall section.
        .shell(-casing_stock)
    )
    # The cap's floor takes none of the skin's stock either, and it is at whichever end the
    # cup is not open on — the mouth-down cap carries its floor on top.
    cap = trim_cup_floor(
        cap,
        *((height - casing_stock,
           height - wall_and_floor_thickness - cap_shell_clearance)
          if open_down else
          (wall_and_floor_thickness + cap_shell_clearance, casing_stock)),
        wall=casing_stock)
    # Same ⌀ boss + teardrop webs as the outer shell.
    cap = cap.union(build_attachment_bosses(height))
    if open_down:
        # The mouth-end relief: the bottom lid's pad section, one slip larger all round,
        # standing on the mouth at z=0 because that is the material side of a mouth-down cup.
        cap = cap.cut(build_attachment_bosses(
            head_pad_height + cap_lid_clearance,
            oversize=head_pad_growth + head_pad_slip))
    else:
        cap = cap.union(build_conduit_columns(height))
    # Screw clearance passes the full cap height, floor through to mating edge.
    cap = cap.cut(attachment_clearances_extrude(height))
    if not open_down:
        cap = cap.cut(build_conduit_bores(height, overshoot=wall_and_floor_thickness))
    # Keep the shell, lid and all mounted hardware on their construction datums.
    # Both dry seats retreat into this cup. The floor's inward face grows by
    # the same shell allowance, retaining its complete 2 mm section.
    z0 = cap_lid_clearance if open_down else cap_shell_clearance
    z1 = height - (cap_shell_clearance if open_down else cap_lid_clearance)
    envelope = (WorldWorkplane(xy_plane_z_up).workplane(offset=z0)
                .rect(outer_shell_x_length + 2.0, outer_shell_y_length + 2.0)
                .extrude(z1 - z0))
    cap = cap.intersect(envelope)
    cap = cap.unwrap()
    if not open_down:
        water = _above_mounts.water_in_features()
        stock = _above_mounts.world_shape_in_cap(water['cup_add']).translate((0.,0.,height))
        air = _above_mounts.world_shape_in_cap(water['cut']).translate((0.,0.,height))
        cap = cap.union(stock).cut(air)
    return cap


def head_access_pockets(z0, depth):
    """Head pockets open to the outside, retaining complete head-bearing floors.

    The outward slots remove the thin counterbore rims at the casing edge.
    The exterior foil band covers these dry side openings, with driver access
    through the lid's flat outer face.
    """
    pockets = (WorldWorkplane(xy_plane_z_up).workplane(offset=z0)
               .pushPoints(attachment_xy_positions).circle(head_cbore_radius)
               .extrude(depth))
    r = head_cbore_radius
    for (x, y), wall in attachment_stations:
        if wall == "corner":
            # A radial opening meets the rounded outside normally, leaving no
            # narrow wedge between a straight slot flank and the corner arc.
            ox=x-(1 if x>0 else -1)*(outer_shell_x_length/2-corner_round_radius)
            oy=y-(1 if y>0 else -1)*(outer_shell_y_length/2-corner_round_radius)
            angle=math.degrees(math.atan2(oy,ox))-90.0
            slot=(cq.Workplane("XY").box(2*r,2*corner_round_radius+2,depth,
                  centered=(True,False,False))
                  .rotate((0,0,0),(0,0,1),angle).translate((x,y,z0)))
        elif wall == "x":
            end = (1 if x > 0 else -1) * (outer_shell_x_length/2 + 1)
            slot = (cq.Workplane("XY").box(abs(end-x), 2*r, depth,
                    centered=(True, True, False))
                    .translate(((x+end)/2, y, z0)))
        else:
            end = (1 if y > 0 else -1) * (outer_shell_y_length/2 + 1)
            slot = (cq.Workplane("XY").box(2*r, abs(end-y), depth,
                    centered=(True, True, False))
                    .translate((x, (y+end)/2, z0)))
        pockets = pockets.union(slot)
    return pockets


def build_foam_cap_lid(open_down=False):
    """The pour lid for the cap built with the same `open_down` — the plate that closes
    its mouth. Authored mouth-facing-side-down either way, so z=0 is the face that lands on the
    cup and `lid_total_height` is the outer face a counterbore is sunk from; the head lands
    head_seat_recess under a face that is otherwise a plane.

    ONE HEIGHT, TWO PLATES. The bottom lid is one wall of plate with a head pad standing off its
    mouth-facing side at each attachment station, into the relief its cup leaves. The TOP lid is
    that height SOLID over the whole footprint — the pads are the plate, its underside is one
    plane, and the band they stood in is wall its cup does not carry."""
    plate_height = wall_and_floor_thickness if open_down else lid_total_height
    cbore_z0 = 0.0 if open_down else lid_total_height - head_cbore_depth
    cbore_depth = head_cbore_depth + (fits.supported_surface if open_down else 0.0)

    lid = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(plate_height)
        .edges("|Z")
        .fillet(corner_round_radius)
    )
    if open_down:
        # Each pad retains 2.38 mm inward stock around its head pocket.
        lid = lid.union(build_attachment_bosses(
            head_pad_height, oversize=head_pad_growth).translate(
            (0, 0, wall_and_floor_thickness)))
    head_cbores = head_access_pockets(cbore_z0, cbore_depth)

    # Pour hole on the +X half: the top lid's at its fore-west station over open cavity, the
    # bottom lid's off the centreline by whatever the deck-mount stations leave it
    # (`foam_cap_lid_pour_xy`); vent holes mirrored across y at the −X corners, where nothing
    # stands.
    pour_xy = foam_cap_lid_pour_xy(top=not open_down)
    vent_plus_y_xy, vent_minus_y_xy = foam_cap_lid_vent_xy(top=not open_down)

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
        roof = _above_mounts.reservoir_b_fill_features(top_cap_height)['lid_add']
        lid = lid.union(_above_mounts.world_shape_in_cap(roof))
        lid = lid.cut(build_conduit_bores(lid_cut_through_depth, frame='lid'))
        lid = lid.cut(build_conduit_entry_reliefs(lid_total_height - wall_and_floor_thickness))
    lid = lid.unwrap()
    if not open_down:
        water = _above_mounts.water_in_features()
        lid = lid.union(_above_mounts.world_shape_in_cap(water['lid_add']))
        lid = lid.cut(_above_mounts.world_shape_in_cap(water['cut']))
        soda = _above_mounts.soda_out_features()
        lid = lid.union(_above_mounts.world_shape_in_cap(soda['lid_add']))
        lid = lid.cut(_above_mounts.world_shape_in_cap(soda['cut']))
    return lid
