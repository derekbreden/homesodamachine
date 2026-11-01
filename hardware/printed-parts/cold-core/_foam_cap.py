"""Uniform equipment lid and open-topped bottom closure for the cold core.

The lid's underside is its bed face. The bottom closure prints on its outside
floor and carries its M5 head pads inside. Exterior foil closes the dry seams.
"""

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
    lid_attachment_stations,
    lid_attachment_xy_positions,
    cap_shell_clearance,
    cap_lid_clearance,
    screw_clearance_radius,
    head_cbore_radius,
    head_cbore_depth,
    head_pad_height,
    head_pad_slip,
    foam_cap_lid_height,
    bottom_cap_height,
    bottom_pour_positions,
    bottom_pour_radius,
)
from _outer_shell import build_attachment_bosses, trim_cup_floor
import _above_core_mounts as _above_mounts

lid_total_height = foam_cap_lid_height
lid_cut_through_depth = lid_total_height + wall_and_floor_thickness
# The lower lid's open head pockets retain the casing's full 2.38 mm inward stock.
head_pad_growth = max(0.0, head_cbore_radius + wall_thickness - screw_boss_size / 2)

# Distance from the internal body datum to the equipment lid's underside.
top_cap_height = foam_cap_height - head_pad_height

# --- the two planes outside the stack answers to ---------------------------
#
# THE STACK'S FLOOR is the bottom cap's outer face, the most-negative-Z layer, which is what the
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


def attachment_clearances_extrude(height, top=False):
    """Screw-clearance cylinders at every attachment position, extruded +Z by height."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(lid_attachment_xy_positions if top else attachment_xy_positions)
        .circle(screw_clearance_radius)
        .extrude(height)
    )



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
    import _reservoir_b_fill
    fitting_air = _reservoir_b_fill.channel_air()
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



def head_access_pockets(z0, depth, top=False):
    """Head pockets open to the outside, retaining complete head-bearing floors.

    The outward slots remove the thin counterbore rims at the casing edge.
    The exterior foil band covers these dry side openings, with driver access
    through the lid's flat outer face.
    """
    stations = lid_attachment_stations if top else attachment_stations
    pockets = (WorldWorkplane(xy_plane_z_up).workplane(offset=z0)
               .pushPoints([xy for xy, wall in stations]).circle(head_cbore_radius)
               .extrude(depth))
    r = head_cbore_radius
    for (x, y), wall in stations:
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


def build_foam_cap_lid():
    """Uniform top equipment plate, with recessed M5 heads and fluid passages."""
    lid = (WorldWorkplane(xy_plane_z_up).rect(outer_shell_x_length,outer_shell_y_length)
           .extrude(lid_total_height).edges('|Z').fillet(corner_round_radius))
    lid = lid.cut(head_access_pockets(lid_total_height-head_cbore_depth,head_cbore_depth,top=True))
    lid = lid.cut(attachment_clearances_extrude(lid_cut_through_depth,top=True))
    lid = lid.cut(build_conduit_bores(lid_cut_through_depth,frame='lid'))
    lid = lid.cut(build_conduit_entry_reliefs(lid_total_height-wall_and_floor_thickness)).unwrap()
    for name in ('water_in_features','soda_out_features'):
        features = getattr(_above_mounts,name)()
        lid = lid.union(_above_mounts.world_shape_in_cap(features['lid_add']))
        lid = lid.cut(_above_mounts.world_shape_in_cap(features['cut']))
    # A plain clearance window lets the independent R14 holder stay with its tube.
    import _reservoir_b_fill
    guide = _above_mounts.world_shape_in_cap(_reservoir_b_fill.guide_world())
    b = guide.BoundingBox()
    window = cq.Solid.makeBox(b.xlen+.3,b.ylen+.3,lid_total_height+.2,
        cq.Vector(b.xmin-.15,b.ymin-.15,-.1))
    lid = lid.cut(window)
    return lid


def build_bottom_cap():
    """One open-topped closure; four underside pour points and two air vents."""
    height = bottom_cap_height
    cap = (WorldWorkplane(xy_plane_z_up).rect(outer_shell_x_length,outer_shell_y_length)
           .extrude(height).edges('|Z').fillet(corner_round_radius)
           .faces('>Z').shell(-outer_shell_wall))
    cap = trim_cup_floor(cap,wall_and_floor_thickness,outer_shell_wall)
    cap = cap.union(build_attachment_bosses(height))
    cap = cap.union(build_attachment_bosses(lid_total_height,oversize=head_pad_growth))
    cap = cap.cut(head_access_pockets(0.,head_cbore_depth+fits.supported_surface))
    cap = cap.cut(attachment_clearances_extrude(height+.1))
    holes = [(xy,bottom_pour_radius) for xy in bottom_pour_positions]
    holes += [(xy,foam_cap_lid_vent_radius) for xy in foam_cap_lid_vent_xy(top=False)]
    for xy,radius in holes:
        cap = cap.cut(cq.Solid.makeCylinder(radius,height+.2,cq.Vector(*xy,-.1)))
    return cap.clean().unwrap()
