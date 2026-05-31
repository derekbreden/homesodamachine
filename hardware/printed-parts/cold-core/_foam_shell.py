"""Top-level foam-shell assembly: union the wall builders, then cut
all the port holes and channel openings."""

from _reservoir_pocket_walls import build_reservoir_pocket_walls
from _reservoir_supports import build_reservoir_supports
from _support_ring import build_tank_support_ring
from _outer_shell import build_outer_shell
from _corner_gussets import build_corner_gussets
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
        build_reservoir_pocket_walls()
        .union(build_reservoir_supports())
        .union(build_tank_support_ring())
        .union(build_outer_shell())
        .union(build_corner_gussets())
        .union(build_reed_channels(side=+1))
        .union(build_reed_channels(side=-1))
    )
    for cut in (
        cut_circular_port_holes,
        cut_co2_inlet,
        cut_slot_for_copper_and_water_inlet,
        cut_reed_channel_openings,
        cut_reed_cable_holes,
    ):
        foam_shell = cut(foam_shell)
    return foam_shell
