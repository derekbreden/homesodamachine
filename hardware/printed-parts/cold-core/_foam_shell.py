"""Top-level foam-shell assembly: union the wall builders, then cut
all the port holes and channel openings."""

from _cold_core_interface import foam_shell_outer_height
from _reservoir_pocket_walls import build_reservoir_pocket_walls
from _support_ring import build_carbonator_support_ring
from _outer_shell import build_outer_shell, cut_insert_pockets
from _port_cuts import (
    cut_copper_ports,
    cut_prv_vent_port,
)
from _reed_channels import (
    build_reed_channels,
    cut_reed_channel_openings,
)
import _reed_b_outlet


def build_full_shell():
    # Reservoir fluid lines enter through their caps. B's dry reed ribbon
    # leaves through the open shell rim, closed above by the top cap floor.
    foam_shell = (
        build_reservoir_pocket_walls()
        .union(build_carbonator_support_ring())
        .union(build_outer_shell())
        .union(build_reed_channels(side=+1))
        .union(build_reed_channels(side=-1))
    )
    foam_shell = cut_insert_pockets(foam_shell)
    for cut in (
        cut_prv_vent_port,
        cut_copper_ports,
        cut_reed_channel_openings,
    ):
        foam_shell = cut(foam_shell)
    return _reed_b_outlet.apply(foam_shell)
