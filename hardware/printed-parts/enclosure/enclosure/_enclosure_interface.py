"""Shared enclosure dimensions that do not require building the enclosure model.

Parts that mate with the shell import this module. The enclosure module re-exports the same
names so its public geometry API stays intact without making a small mating part load the whole
machine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents
                            if p.name == "printed-parts") / "cadlib"))

import fits  # noqa: E402

wall = 3.0
rear_seam_clear = 3.0

# THE MOVING PUMP ENDS' FORE/AFT LEAD OVER THE FIXED TEE DECK. The four short barb tubes spend
# this first, then `manifold_layout.BARB_PLATE_BERTH` on the steel plate and its working airs.
# With the measured 54 mm pump body and its three-millimetre Y+ skirt band, this lead leaves the
# physical skirt 0.30 mm fore of the fixed plate-guide wall and the cradle 0.20 mm fore of the
# steel. The enclosure's front wall wraps out to the cartridge's show face; this is an internal
# pump-to-deck figure, not an exterior protrusion.
pump_station_lead = 1.28

# THE PUMPS' VERTICAL SERVICE DATUM. In `manifold_layout`'s authored frame the pump depth axis
# is Y; `enclosure_assembly` stands that axis on world Z. This shift therefore moves only the
# two pumps and the four barb ends downward in the installed machine while the anchor tees,
# collet plate and valve manifold keep their stations.
pump_station_drop = 2.0

# THE FIELD THE BOX'S SHOW FACES CARRY, in the two figures a piece that does NOT carry it still
# has to know. The fade is driven by how far a station stands from the nearest edge of the show
# face (`cadlib/flute_skin._depth_field`), so a band's own two faces are both edges and the
# deepest station on a band of height h stands h / 2 from one — full depth only once that
# clears `flute_rise`. `flute_full_depth_height` is that threshold, and the pieces let into the
# box's faces read it to say which side of it they fall on: `display_cover.display-cover-reveal`,
# `ceiling_panel.ceiling-panel-reveal`. `enclosure.py` cuts the field with the same two.
flute_depth = 1.2
flute_rise = 5.0
flute_full_depth_height = 2.0 * flute_rise


def flute_reach(band_height):
    """How deep a groove lands on a band `band_height` tall — the field's own expression.

    `flute_skin._depth_field` ramps on `smoothstep(far / flute_rise)`, where `far` is the
    distance to the nearest edge of the show face; on a band the deepest station stands half
    the height from either face. So this is what a piece gets for being as tall as it is, and
    it is the reading a reveal is stated against rather than a number typed beside one."""
    t = min(band_height / 2.0, flute_rise) / flute_rise
    return flute_depth * t * t * (3.0 - 2.0 * t)

screw_clear_dia = 3.9
head_cbore_dia = 6.15
heatset_dia = 4.0
heatset_depth = 5.25
mount_boss_dia = 7.0
boss_ligament = (mount_boss_dia - heatset_dia) / 2.0
mount_bore_relief = 1.0
relief_chamfer = 45.0

display_bezel_x = 113.5
display_bezel_slope = 77.0
display_corner_r = 2.5
display_inset_lap = 3.0
display_inset_reach = 20.0
display_inset_depth = 2.0
display_inset_x = display_bezel_x + 2 * display_inset_reach
display_inset_slope = display_bezel_slope + 2 * display_inset_lap
display_bezel_depth = 4.0
display_cover_thickness = 2.0
display_cover_slip = fits.slip      # per side, plate edge into the inset it drops in
display_cover_head_h = 3.0
display_cover_seat_recess = 0.2
display_cover_cbore_depth = display_cover_head_h + display_cover_seat_recess
display_cover_seat = display_cover_cbore_depth + display_cover_thickness
display_screw_x = (display_bezel_x + display_inset_x) / 4.0
