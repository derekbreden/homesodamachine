import math
from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
xy_plane_z_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
# All structural walls and floors are 2 mm thick. The 1 mm originals
# warped/shifted in PETG; 2 mm holds its shape on every wall it's been
# tested on so far. The outer dimensions of every component are
# refactored below so that wall-thickness growth is *added* to the
# outer envelope rather than absorbed from inner buffers, foam gaps,
# bag pocket cavities, etc.
wall_and_floor_thickness = 2.0
# Reference wall thickness used in the original 1 mm design. Outer-
# dimension formulas use (wall_and_floor_thickness - reference_wall_thickness)
# as a compensation term, so 1 mm walls reproduce the original geometry
# exactly and 2 mm walls grow each affected outer dimension by 1 mm.
reference_wall_thickness = 1.0
wall_thickness_compensation = wall_and_floor_thickness - reference_wall_thickness
hole_shift_from_edge = 15.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank copper shell
# -------------------------------------------------------
#
# Tank copper shell radius. The +compensation term keeps the inner face
# of the shell wall (where the copper coil sits) at radius 69.5 regardless
# of wall thickness, preserving the 6 mm coil buffer.
tank_outer_radius = 63.5
# Bumped from 7 to 8 mm so the actual radial clearance between the tank
# (R=63.5) and the inner shell face is 7 mm (with 2 mm walls), enough
# for 1/4" ACR copper coil + thermal tape + assembly slack.
copper_coil_buffer_radius = 8.0
tank_copper_shell_radius = tank_outer_radius + copper_coil_buffer_radius + wall_thickness_compensation
#
# Tank copper shell height. The +compensation term keeps the interior
# Y cavity at the original 211.4 mm regardless of floor thickness.
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_copper_shell_height = (
    tank_height + below_tank_elbows_height + above_tank_elbows_height
    + wall_thickness_compensation
)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank support wedge
# -------------------------------------------------------
#
tank_support_wedge_height = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Bag pocket
# -------------------------------------------------------
#
# bag_pocket_width tracks tank_copper_shell_radius automatically, so the
# bag-pocket Z interior cavity (= width − 2 × wall) stays at 139 mm. The
# bag_pocket_depth gets +2*compensation so the X interior cavity stays
# at 33 mm regardless of wall thickness.
bag_pocket_width = tank_copper_shell_radius * 2
bag_pocket_depth = 35 + 2 * wall_thickness_compensation
#
# -------------------------------------------------------


# -------------------------------------------------------
# Outer shell
# -------------------------------------------------------
#
outer_shell_foam_gap = 16.0
# Outer wall is the same 2 mm as the rest of the assembly now. Kept as
# its own constant in case the inner/outer split is ever needed again.
outer_shell_wall_thickness = wall_and_floor_thickness
#
# Outer footprint shared by the outer shell, the foam cap, and the foam
# cap lid. Defined at module level so changing outer_shell_wall_thickness
# updates all three together (they must remain coplanar at the corners
# so the pin bosses line up).
bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
outer_shell_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + outer_shell_wall_thickness)
outer_shell_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + outer_shell_wall_thickness)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap (top/bottom 16 mm foam pour tray, printed twice)
# -------------------------------------------------------
#
# Foam cap outer height. The +compensation term keeps the cap's interior
# Y cavity (= foam thickness in the cap) at 15 mm regardless of floor
# thickness.
foam_cap_height = 16.0 + wall_thickness_compensation
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap lid (sits atop a cap during foam pour, printed twice)
# -------------------------------------------------------
#
foam_cap_lid_pour_radius = 5.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cap-to-outer-shell pin joinery
# -------------------------------------------------------
# Pins on cap top (one face); holes drilled into outer-shell corners (top + bottom faces).
# Same cap printed twice — used as bottom (pins up into outer shell) and top (flipped, pins down into outer shell).
# Lid has corner clearance holes so the cap pin can pass freely through into the outer shell.
#
pin_radius = 2.0
pin_height = 5.0
pin_hole_depth = pin_height + 1.0
pin_boss_size = 8.0
lid_pin_clearance_radius = pin_radius
#
# -------------------------------------------------------


def build_tank_copper_shell():
    
    return (
        cq.Workplane(xz_plane_y_up)
        .circle(tank_copper_shell_radius)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def build_bag_pocket_support_shell():
    bag_pocket_support_side_length = 2 * tank_copper_shell_radius
    return (
        cq.Workplane(xz_plane_y_up)
        .rect(bag_pocket_support_side_length, bag_pocket_support_side_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def build_tank_support_wedge():
    support_wedge_outer_radius = tank_copper_shell_radius - wall_and_floor_thickness
    support_wedge_ring_width = 9
    support_wedge_inner_radius = support_wedge_outer_radius - support_wedge_ring_width
    support_wedge_bottom_y = wall_and_floor_thickness
    filled_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y)
        .circle(support_wedge_outer_radius)
        .extrude(tank_support_wedge_height)
    )
    cut_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y)
        .circle(support_wedge_inner_radius)
        .extrude(tank_support_wedge_height)
    )
    ring = filled_cylinder.cut(cut_cylinder)
    # Recover ~3% thermal loss from removing the cone: 4 angular slots cut
    # through the ring at 45°/135°/225°/315°, 30° wide each. Leaves four
    # 60° support segments aligned with the cardinal axes.
    slot_radial_margin = 1.0
    slot_inner_radius = support_wedge_inner_radius - slot_radial_margin
    slot_outer_radius = support_wedge_outer_radius + slot_radial_margin
    slot_half_width = math.radians(15)
    for i in range(4):
        center_angle = math.radians(45 + 90 * i)
        a1 = center_angle - slot_half_width
        a2 = center_angle + slot_half_width
        p1 = (slot_inner_radius * math.cos(a1), slot_inner_radius * math.sin(a1))
        p2 = (slot_outer_radius * math.cos(a1), slot_outer_radius * math.sin(a1))
        p3 = (slot_outer_radius * math.cos(a2), slot_outer_radius * math.sin(a2))
        p4 = (slot_inner_radius * math.cos(a2), slot_inner_radius * math.sin(a2))
        slot = (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=support_wedge_bottom_y)
            .moveTo(*p1).lineTo(*p2).lineTo(*p3).lineTo(*p4).close()
            .extrude(tank_support_wedge_height)
        )
        ring = ring.cut(slot)
    return ring

def build_a_bag_pocket_shell(side=1):
    bag_pocket_height = tank_copper_shell_height

    # Bag pocket offset
    bag_pocket_x_offset = tank_copper_shell_radius + bag_pocket_depth / 2 - wall_and_floor_thickness
    bag_pocket_x_offset *= side

    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(bag_pocket_x_offset, 0, 0))
        .rect(bag_pocket_depth, bag_pocket_width)
        .extrude(bag_pocket_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def punch_a_bag_pocket_shell_hole(foam_bag_shell, side=1):

    # Bag pocket offset
    bag_pocket_x_offset = tank_copper_shell_radius + bag_pocket_depth / 2 - wall_and_floor_thickness
    bag_pocket_x_offset *= side

    # Hole offset
    hole_z_offset = bag_pocket_width / 2 - 10
    hole_x_offset = bag_pocket_x_offset
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness

    # Hole
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))

    return foam_bag_shell.cut(hole_punch)

def build_outer_shell():
    shell = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-outer_shell_wall_thickness)
    )
    for x_sign in (1, -1):
        for z_sign in (1, -1):
            boss_x = x_sign * (outer_shell_x_length / 2 - pin_boss_size / 2)
            boss_z = z_sign * (outer_shell_z_length / 2 - pin_boss_size / 2)
            boss = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, 0, boss_z), offset=0)
                .rect(pin_boss_size, pin_boss_size)
                .extrude(tank_copper_shell_height)
            )
            shell = shell.union(boss)
            for hole_y in (0, tank_copper_shell_height - pin_hole_depth):
                hole = (
                    cq.Workplane(xz_plane_y_up)
                    .workplane(origin=(boss_x, hole_y, boss_z), offset=hole_y)
                    .circle(pin_radius)
                    .extrude(pin_hole_depth)
                )
                shell = shell.cut(hole)
    return shell

def build_foam_cap():
    cap = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(foam_cap_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    for x_sign in (1, -1):
        for z_sign in (1, -1):
            boss_x = x_sign * (outer_shell_x_length / 2 - pin_boss_size / 2)
            boss_z = z_sign * (outer_shell_z_length / 2 - pin_boss_size / 2)
            boss = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, 0, boss_z), offset=0)
                .rect(pin_boss_size, pin_boss_size)
                .extrude(foam_cap_height)
            )
            cap = cap.union(boss)
            pin = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, foam_cap_height, boss_z), offset=foam_cap_height)
                .circle(pin_radius)
                .extrude(pin_height)
            )
            cap = cap.union(pin)
    return cap

def build_foam_cap_lid():
    lid = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(wall_and_floor_thickness)
    )

    pour_x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    vent_x = -(outer_shell_x_length / 2 - foam_cap_lid_hole_inset)
    vent_z = outer_shell_z_length / 2 - foam_cap_lid_hole_inset

    pour_hole = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(pour_x, 0, 0))
        .circle(foam_cap_lid_pour_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_a = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_b = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, -vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )

    lid = lid.cut(pour_hole).cut(vent_hole_a).cut(vent_hole_b)

    for x_sign in (1, -1):
        for z_sign in (1, -1):
            boss_x = x_sign * (outer_shell_x_length / 2 - pin_boss_size / 2)
            boss_z = z_sign * (outer_shell_z_length / 2 - pin_boss_size / 2)
            clearance = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, 0, boss_z), offset=0)
                .circle(lid_pin_clearance_radius)
                .extrude(wall_and_floor_thickness * 3)
            )
            lid = lid.cut(clearance)

    return lid

def build_a_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
    hole_punch_height=40,
):
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )

def cut_hole_for_co2_inlet(foam_bag_shell):
    hole_z_offset = (tank_copper_shell_radius + 20) * -1
    hole_x_offset = 0
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_hole_for_water_inlet(foam_bag_shell):
    hole_z_offset = tank_copper_shell_radius - 20
    hole_x_offset = 0
    hole_y_offset = tank_copper_shell_height - hole_shift_from_edge
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_hole_for_water_outlet(foam_bag_shell):
    hole_z_offset = tank_copper_shell_radius - 20
    hole_x_offset = 0
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell, which = 0):
    hole_z_offset = 20
    hole_x_offset = -30
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
    slit_above = tank_copper_shell_height

    if (which == 1):
        hole_x_offset = 30
        hole_y_offset = tank_copper_shell_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height

    hole_args = dict(
        origin=(hole_x_offset, hole_y_offset, hole_z_offset),
        hole_punch_height=tank_copper_shell_radius,
    )

    slit_width = 6.5
    # 12 rails per plug: one on each face of each of the 3 walls the plug
    # crosses (tank_copper_shell, bag_pocket_support_shell, outer_shell), on
    # each of the plug's ±X sides. Each rail is a small tab that hugs one
    # face of one wall — together each pair of rails clips the plug onto
    # the wall like a binder clip on a sheet of paper. Replaces the old
    # plug_x_extra interference fit.
    rail_x_protrusion = 1.0
    rail_z_thickness = 1.0
    plug_end_extension = 1.0

    slit_punch = (
        build_a_hole_punch(**hole_args)
        .moveTo(0, slit_above / 2)
        .rect(slit_width, slit_above)
        .extrude(tank_copper_shell_radius)
    )
    copper_hole = build_a_hole_punch(**hole_args)

    intersection_pieces = foam_bag_shell.intersect(slit_punch)
    slices = sorted(intersection_pieces.solids().vals(), key=lambda s: s.BoundingBox().zmin)

    # Innermost slice is the tank_copper_shell wall (cylindrical); outermost
    # is the outer_shell wall (planar). Middle slice (if any) is the
    # bag_pocket_support_shell wall.
    tank_copper_shell_slice = slices[0]
    outer_shell_slice = slices[-1]

    tank_copper_shell_cylindrical_faces = [
        f for f in tank_copper_shell_slice.Faces() if f.geomType() == "CYLINDER"
    ]
    tank_copper_shell_inner_face = min(
        tank_copper_shell_cylindrical_faces,
        key=lambda f: math.hypot(f.Center().x, f.Center().z),
    )
    outer_shell_outermost_face = max(
        outer_shell_slice.Faces(),
        key=lambda f: abs(f.Center().z),
    )

    # Plug body = original loft (curved on the tank_copper_shell side, flat
    # on the outer_shell side) with a 1 mm linear extension at each end so
    # the rails on those two end-wall faces have plug body to attach to.
    # The extensions are built with extrudeLinear on the loft's end faces;
    # 4-wire makeLoft and loft+fuse-of-slabs both produced malformed solids
    # that broke subsequent boolean ops with the rails.
    plug_main = cq.Solid.makeLoft([
        tank_copper_shell_inner_face.outerWire(),
        outer_shell_outermost_face.outerWire(),
    ])
    inner_slab = cq.Solid.extrudeLinear(
        tank_copper_shell_inner_face,
        cq.Vector(0, 0, -plug_end_extension),
    )
    outer_slab = cq.Solid.extrudeLinear(
        outer_shell_outermost_face,
        cq.Vector(0, 0, plug_end_extension),
    )
    plug_solid = plug_main.fuse(inner_slab, outer_slab)

    # 12 rails: 3 wall slices × 2 plug X-sides × 2 wall Z-faces. Each rail
    # is a small tab (rail_x_protrusion in X × rails_y_height in Y ×
    # rail_z_thickness in Z) flush with one face of one wall, attached to
    # the plug body at the slit edge.
    #
    # Rails span the rectangular portion of the slit only — from
    # hole_y_offset (where the slit-punch's small bore cylinder meets the
    # rectangular slit profile) to the top of the plug body. Below
    # hole_y_offset the plug narrows to the bore cylinder bump and there's
    # no plug face at the rail's slit-edge X to attach to.
    plug_y_max = max(s.BoundingBox().ymax for s in slices)
    rails_y_min = hole_y_offset
    rails_y_max = plug_y_max
    rails_y_height = rails_y_max - rails_y_min

    tank_copper_shell_inner_radius = tank_copper_shell_radius - wall_and_floor_thickness
    tank_copper_shell_outer_radius = tank_copper_shell_radius

    for s in slices:
        # Only the tank_copper_shell wall is curved. The other slices have
        # cylindrical faces too (left over from the hole-punch's small bore
        # cylinder), so we identify the curved wall by position — it's the
        # innermost slice.
        is_tank_copper_shell = s is tank_copper_shell_slice
        if not is_tank_copper_shell:
            bb = s.BoundingBox()

        for x_sign in (1, -1):
            slit_edge_x = hole_x_offset + x_sign * (slit_width / 2)

            # side_sign = -1: rail on the inner face of the wall (toward the
            # cylinder axis for curved, toward smaller Z for planar).
            # side_sign = +1: rail on the outer face.
            for side_sign in (-1, +1):
                if is_tank_copper_shell:
                    # Cylinder centered on world Y axis, so wall face Z =
                    # sqrt(R² − x²) at the slit edge X. The rail's tangent
                    # direction follows the cylinder surface at that point;
                    # its normal is radial.
                    r_face = (
                        tank_copper_shell_inner_radius if side_sign == -1
                        else tank_copper_shell_outer_radius
                    )
                    wall_z = math.sqrt(r_face**2 - slit_edge_x**2)
                    n_x = slit_edge_x / r_face
                    n_z = wall_z / r_face
                    tangent_x = x_sign * n_z
                    tangent_z = -x_sign * n_x
                    offset_x = side_sign * n_x
                    offset_z = side_sign * n_z
                else:
                    # Planar wall: tangent along world X, normal along world Z.
                    wall_z = bb.zmin if side_sign == -1 else bb.zmax
                    tangent_x = x_sign
                    tangent_z = 0
                    offset_x = 0
                    offset_z = side_sign

                # Parallelogram in X-Z plane spanning rail_x_protrusion
                # before AND after the slit edge along the tangent
                # direction. The "before" half overlaps the plug body so
                # boolean fuse has volumetric overlap to work with;
                # otherwise the curved-wall rails meet the plug body at
                # only a single point and fuse silently leaves them
                # disconnected. The "after" half is the visible rail.
                p1 = (
                    slit_edge_x - tangent_x * rail_x_protrusion,
                    wall_z - tangent_z * rail_x_protrusion,
                )
                p2 = (
                    slit_edge_x + tangent_x * rail_x_protrusion,
                    wall_z + tangent_z * rail_x_protrusion,
                )
                p3 = (
                    p2[0] + offset_x * rail_z_thickness,
                    p2[1] + offset_z * rail_z_thickness,
                )
                p4 = (
                    p1[0] + offset_x * rail_z_thickness,
                    p1[1] + offset_z * rail_z_thickness,
                )
                wire = cq.Wire.makePolygon(
                    [cq.Vector(p[0], rails_y_min, p[1]) for p in (p1, p2, p3, p4)],
                    close=True,
                )
                face = cq.Face.makeFromWires(wire)
                rail_solid = cq.Solid.extrudeLinear(
                    face,
                    cq.Vector(0, rails_y_height, 0),
                )
                plug_solid = plug_solid.fuse(rail_solid)

    plug_solid = plug_solid.cut(copper_hole.val())
    plug = cq.Workplane().add(plug_solid)

    return foam_bag_shell.cut(slit_punch), plug

# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():

    # Build shell
    tank_copper_shell = build_tank_copper_shell()
    tank_support_wedge = build_tank_support_wedge()
    bag_pocket_support_shell = build_bag_pocket_support_shell()
    bag_pocket_shell = build_a_bag_pocket_shell()
    bag_pocket_shell_2 = build_a_bag_pocket_shell(side=-1)
    outer_shell = build_outer_shell()
    foam_bag_shell = (
        tank_copper_shell
        .union(tank_support_wedge)
        .union(bag_pocket_support_shell)
        .union(bag_pocket_shell)
        .union(bag_pocket_shell_2)
        .union(outer_shell)
    )

    # Cut holes
    foam_bag_shell = punch_a_bag_pocket_shell_hole(foam_bag_shell)
    foam_bag_shell = punch_a_bag_pocket_shell_hole(foam_bag_shell, side=-1)
    foam_bag_shell = cut_hole_for_co2_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_outlet(foam_bag_shell)

    # Cut slits + extract their plugs
    foam_bag_shell, copper_inlet_plug = cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell)
    foam_bag_shell, copper_outlet_plug = cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell, which=1)

    # Build the foam cap (separate part, printed twice for top and bottom)
    foam_cap = build_foam_cap()
    # Foam cup must be unioned to turn from a "shell" into a "solid"
    foam_cap = foam_cap.union(foam_cap)

    # Build the foam cap lid (separate part, printed twice, sits atop a cap during pour)
    foam_cap_lid = build_foam_cap_lid()

    here = Path(__file__).resolve().parent
    cq.exporters.export(foam_bag_shell, str(here / "foam-bag-shell.step"))
    cq.exporters.export(copper_inlet_plug, str(here / "copper-inlet-plug.step"))
    cq.exporters.export(copper_outlet_plug, str(here / "copper-outlet-plug.step"))
    cq.exporters.export(foam_cap, str(here / "foam-cap.step"))
    cq.exporters.export(foam_cap_lid, str(here / "foam-cap-lid.step"))
    print(f"-> foam-bag-shell.step")
    print(f"-> copper-inlet-plug.step")
    print(f"-> copper-outlet-plug.step")
    print(f"-> foam-cap.step")
    print(f"-> foam-cap-lid.step")


if __name__ == "__main__":
    main()
