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


def build_full_shell():
    # NOTHING HERE GIVES WAY TO A LINE. Each reservoir stands on its pocket's own floor and is
    # filled and drawn through its cap, so no line crosses a pocket; the outer shell, the
    # carbonator support ring and the reed channels all fence a line, and
    # `_internal_routes.report_routes` reads what that costs at every build.
    #   THE OUTER SHELL IS FENCE, and that is what sends six of the seven lines up to the lid.
    # The one opening in the skin is `cut_prv_vent_port`, below: named for the single line it
    # lets out, so opening the skin stays a decision about that line.
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
    return foam_shell
