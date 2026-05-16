"""Top-level foam-shell assembly: union the wall builders, then cut
all the port holes and channel openings."""

from _tank_walls import build_tank_and_bag_pocket_walls
from _support_ring import build_tank_support_ring
from _outer_shell import build_outer_shell
from _port_cuts import (
    cut_circular_port_holes,
    cut_co2_inlet,
    cut_slot_for_copper_and_water_inlet,
)
from _reed_channels import (
    build_reed_channels,
    cut_reed_channel_openings,
    cut_reed_cable_holes,
)


def build_full_shell():
    foam_shell = (
        build_tank_and_bag_pocket_walls()
        .union(build_tank_support_ring())
        .union(build_outer_shell())
        .union(build_reed_channels(side=+1))
        .union(build_reed_channels(side=-1))
    )
    foam_shell = cut_circular_port_holes(foam_shell)
    foam_shell = cut_co2_inlet(foam_shell)
    foam_shell = cut_slot_for_copper_and_water_inlet(foam_shell)
    foam_shell = cut_reed_channel_openings(foam_shell)
    foam_shell = cut_reed_cable_holes(foam_shell)
    return foam_shell
