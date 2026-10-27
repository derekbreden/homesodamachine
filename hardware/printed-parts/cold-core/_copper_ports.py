"""Evaporator copper feed-throughs in the shell's native frame."""

from _cold_core_interface import front_wall_x, port_lane_mid_y, west_lane_mid_y

copper_outer_diameter = 6.35
hole_radius = 3.75
# The refrigeration base's two entries set these axes independently of wall stock.
evap_cross_z = 28.425


def stations():
    """Name -> (axis point, outward direction), at the retained copper datum."""
    return {
        "evap-inlet": ((front_wall_x, port_lane_mid_y, evap_cross_z), (-1., 0., 0.)),
        "evap-outlet": ((front_wall_x, west_lane_mid_y, evap_cross_z), (-1., 0., 0.)),
    }


def station(name):
    return stations()[name]
