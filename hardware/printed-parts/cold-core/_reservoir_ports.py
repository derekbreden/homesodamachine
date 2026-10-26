"""Matched flush TPU seats and independent reservoir air-tube datums, in mm.

Port XY belongs to the cold-core shell frame. Each lid captures a spool through
its flat plate; the casing cup and lid carry the air tube beyond the insulation.
"""
import cadquery as cq

plate_thickness = 4.0
liquid_grip = dict(waist_d=9.0, flare_d=11.0, bore_d=6.2, lead_d=7.0, lead_h=0.4)
air_grip = dict(waist_d=6.0, flare_d=8.0, bore_d=3.9, lead_d=4.5, lead_h=0.3)
air_position = {+1: (120.0, -26.0), -1: (-102.0, -32.5)}
air_tube_od = 4.0
air_tube_id = 2.5
air_tube_above_casing = 6.0
air_tube_below_lid = 1.0
air_passage_diameter = 5.2
air_passage_wall = 2.0
baffle_od = 13.0
baffle_id = 9.0
baffle_drop = 3.0
baffle_floor = 1.0
baffle_slot_width = 3.0
baffle_slot_height = 2.0


def cylinder(xy, z0, z1, diameter):
    return cq.Solid.makeCylinder(diameter / 2, z1 - z0, cq.Vector(*xy, z0))


def spool_envelope(xy, z0, specification):
    """Cylindrical waist with matching 45-degree flares at both flat ends."""
    z1 = z0 + plate_thickness
    waist = specification['waist_d'] / 2
    flare = specification['flare_d'] / 2
    depth = flare - waist
    return cylinder(xy, z0, z1, 2 * waist).fuse(
        cq.Solid.makeCone(flare, waist, depth, cq.Vector(*xy, z0)),
        cq.Solid.makeCone(waist, flare, depth, cq.Vector(*xy, z1 - depth))).clean()


def seat_tool(xy, z0, specification):
    """Matching profile; retain the perimeter lip beneath a partially overlapping seat."""
    z1 = z0 + plate_thickness
    return spool_envelope(xy, z0, specification).fuse(
        cylinder(xy, z1, z1 + .1, specification['flare_d']))


def build_grommet(specification, xy=(0.0, 0.0), z0=0.0):
    z1 = z0 + plate_thickness
    radius = specification['bore_d'] / 2
    lead_radius = specification['lead_d'] / 2
    lead_height = specification['lead_h']
    opening = cylinder(xy, z0 - .1, z1 + .1, 2 * radius).fuse(
        cq.Solid.makeCone(lead_radius, radius, lead_height, cq.Vector(*xy, z0)),
        cq.Solid.makeCone(radius, lead_radius, lead_height,
                         cq.Vector(*xy, z1 - lead_height)))
    return spool_envelope(xy, z0, specification).cut(opening).clean()


def build_baffle(xy, lid_underside_z):
    """Closed floor and four side slots; the 9mm chamber clears the lower flare."""
    floor_z = lid_underside_z - baffle_drop
    slots_z = floor_z + baffle_floor
    shell = cylinder(xy, floor_z, lid_underside_z + .01, baffle_od).cut(
        cylinder(xy, slots_z, lid_underside_z + .1, baffle_id))
    x, y = xy
    for angle in (0, 90, 180, 270):
        slot = cq.Solid.makeBox(10.0, baffle_slot_width, baffle_slot_height,
            cq.Vector(x, y - baffle_slot_width / 2, slots_z))
        shell = shell.cut(slot.rotate((x, y, 0), (x, y, 1), angle))
    return shell.clean()


def build_air_tube(side, lid_underside_z, casing_face_z):
    xy = air_position[side]
    z0 = lid_underside_z - air_tube_below_lid
    z1 = casing_face_z + air_tube_above_casing
    return cylinder(xy, z0, z1, air_tube_od).cut(
        cylinder(xy, z0 - .1, z1 + .1, air_tube_id)).clean()
