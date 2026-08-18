"""Top-level foam-shell assembly: union the wall builders, then cut
all the port holes and channel openings."""

from _cold_core_interface import corner_boss_slots, foam_shell_outer_height
from _reservoir_pocket_walls import build_reservoir_pocket_walls
from _reservoir_supports import build_reservoir_supports
from _support_ring import build_tank_support_ring
from _outer_shell import build_outer_shell, cut_insert_pockets, _rounded_footprint
from _port_cuts import (
    cut_line_corridors,
    cut_lane_slots,
    cut_prv_vent_port,
)
from _reed_channels import (
    build_reed_channels,
    cut_reed_channel_openings,
)


def build_full_shell():
    # WHAT GIVES WAY TO A LINE, named here because this is where the bodies are. A bag
    # pocket's ±Y wall is two millimetres of PETG a draw crosses on its way out and the CO2
    # crosses on its way in; the pocket corner posts stand under the reservoirs in the space
    # the CO2's reach to the vessel runs through. Each is opened along the line's own
    # corridor where it meets one (`_port_cuts.cut_line_corridors`). Nothing else in the
    # shell does — the outer shell, the tank support ring and the reed channels all fence a
    # line, and `_internal_routes.report_routes` reads what that costs at every build.
    #   THE OUTER SHELL IS FENCE, NOT GIVE-WAY, and that is what sends six of the seven lines
    # up to the lid. The one opening in the skin is `cut_prv_vent_port`, below: named for the
    # single line it lets out, so opening the skin stays a decision about that line rather
    # than a property of every corridor that happens to touch it.
    #   THE OUTER SHELL IS FENCE, NOT GIVE-WAY, and that is what sends six of the seven lines
    # up to the lid. The one opening in the skin is `cut_prv_vent_port`, below: named for the
    # single line it lets out, so opening the skin stays a decision about that line rather
    # than a property of every corridor that happens to touch it.
    pocket_walls = build_reservoir_pocket_walls()
    corner_posts = build_reservoir_supports()

    foam_shell = (
        pocket_walls
        .union(corner_posts)
        .union(build_tank_support_ring())
        .union(build_outer_shell())
        .union(build_reed_channels(side=+1))
        .union(build_reed_channels(side=-1))
    )
    # The enclosure's four-corner boss slots: an inward emboss on each ±Y flank, the liner
    # unioned before the void is cut so the pour stays sealed behind and beside it
    # (`_cold_core_interface.corner_boss_slots`). The liner is trimmed to the rounded
    # footprint, since its fore end reaches into the corner round.
    footprint = _rounded_footprint(foam_shell_outer_height).unwrap()
    for liner, void in corner_boss_slots():
        foam_shell = foam_shell.union(liner.intersect(footprint)).cut(void)
    foam_shell = cut_insert_pockets(foam_shell)
    foam_shell = cut_line_corridors(foam_shell, (pocket_walls, corner_posts))
    for cut in (
        cut_prv_vent_port,
        cut_lane_slots,
        cut_reed_channel_openings,
    ):
        foam_shell = cut(foam_shell)
    return foam_shell
