"""Shared ASA Aero float and guide datums, in millimetres.

These dimensions place the trial article in the carbonator and reservoirs.
Reed reach is bench evidence; liquid switching levels still need calibration.
No import here builds CAD, slices a project or changes an accepted print.
"""

import math

diameter = 36.0
bore_diameter = 4.8
guide_diameter = 3.175
magnet_od = 19.05
magnet_id = 9.525
magnet_thickness = 3.175
magnet_tolerance = 0.1
magnet_mass = 5.09
pocket_od = 19.35
pocket_id = 9.225
pocket_depth = 3.6
water_density = 0.9997
design_foam_density = 0.65
minimum_reserve_lift_g = 5.0
height_increment = 1.0
layer_height = 0.2
xy_contour_compensation = 0.05
xy_hole_compensation = -0.05

annular_area = math.pi * ((diameter / 2) ** 2 - (bore_diameter / 2) ** 2)
pocket_volume = math.pi * ((pocket_od / 2) ** 2 - (pocket_id / 2) ** 2) * pocket_depth
minimum_height = ((minimum_reserve_lift_g + magnet_mass
                   - design_foam_density * pocket_volume / 1000)
                  / ((water_density - design_foam_density) * annular_area / 1000))
height = math.ceil(minimum_height / height_increment) * height_increment
magnet_midplane = height / 2
magnet_seat = magnet_midplane - magnet_thickness / 2
pocket_roof = magnet_seat + pocket_depth
pause_before_z = math.ceil(pocket_roof / layer_height - 1e-9) * layer_height
displacement_cc = annular_area * height / 1000
foam_cc = displacement_cc - pocket_volume / 1000
design_mass_g = foam_cc * design_foam_density + magnet_mass

# 18 mm body radius + 2 mm nominal wall clearance. The running bore allows
# 0.8125 mm radial motion; reserve that motion on BOTH sides of the guide.
wall_clearance = 2.0
rod_axis_from_inner_wall = diameter / 2 + wall_clearance
guide_radial_clearance = (bore_diameter - guide_diameter) / 2
minimum_wall_clearance = wall_clearance - guide_radial_clearance
maximum_wall_clearance = wall_clearance + guide_radial_clearance
magnet_edge_inset = (diameter - magnet_od) / 2

reed_model = "Littelfuse MDSR-7-10-15"
# Retain the 14 x 2.5 mm mounting envelope for glass, capture tape and leads.
# The MDSR-7 glass itself is 12.7 mm long. A mounting envelope is not an AT rating.
reed_mount_length = 14.0
reed_mount_diameter = 2.5
# Bare-magnet reference measurements use the RC62 edge, not the foam perimeter.
bench_edge_distance = 30.0
bench_stable_travel = 30.0
bench_scope = "One bare RC62 and one MDSR-7-10-15, axial reed; nearest magnet edge datum; no installed-wall calibration"
# The reported printed-float test uses FLOAT EDGE to REED CENTER: 20 mm
# usable, 21–24 mm intermittent, 25 mm consistently absent. Keep the initial
# installed geometry within 18 mm, including retreat through the running bore.
float_edge_reported_usable_limit = 20.0
float_edge_design_maximum = 18.0
float_edge_evidence = "magnetic-float/all-aero/physical-observations.json#reed_reach_report"


def magnet_above_waterline(mass_g=design_mass_g, liquid_density=water_density):
    """Magnet centre minus surface height for a guided dry upright article.

    A negative value puts the magnet below the surface. Assumes the body keeps
    its envelope, its pocket stays dry, and liquid enters neither foam nor skin.
    Measured mass/float height and the actual liquid replace these seed values.
    """
    return magnet_midplane - mass_g / (liquid_density * annular_area / 1000)


def reed_edge_distance(rod_axis, reed_axis):
    """Conservative collinear horizontal reed-centre to nearest RC62 edge."""
    return abs(reed_axis - rod_axis) + guide_radial_clearance - magnet_od / 2


def reed_float_edge_distance(rod_axis, reed_axis):
    """Greatest collinear float-perimeter to reed-center distance with bore play."""
    return abs(reed_axis - rod_axis) + guide_radial_clearance - diameter / 2


assert minimum_wall_clearance > 1.0
assert height == 28.0 and magnet_midplane == 14.0
