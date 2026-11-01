"""Numbers for the enclosure's swept structural exterior, shared with its native builders."""

import _swept_top
from overhang_round import transition, OUTWARD_PER_HEIGHT


def numbers(outer):
    """The exact display profile and print-down roof sections; no native geometry is built."""
    height, foot = transition(_swept_top.SIDE_RADIUS)
    return {
        "outer": outer,
        "profile": _swept_top.profile(outer),
        "standing_radius": _swept_top.FRONT_RADIUS,
        "side_radius": _swept_top.SIDE_RADIUS,
        "angle": _swept_top.ANGLE,
        "roof_fill_sections": _swept_top.roof_fill_sections(outer),
        "roof_transition": {"height": height, "foot": foot,
                            "outward_per_height": OUTWARD_PER_HEIGHT},
    }
