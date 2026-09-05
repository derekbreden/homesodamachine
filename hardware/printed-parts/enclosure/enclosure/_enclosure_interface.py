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

# Pump-to-tee spacing on the four straight release tubes.
pump_station_lead = 1.28
pump_station_drop = 3.0
manifold_rise = 2.0

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
# THE INSERT'S OWN BODY, both lengths ruthex sells in M3. They are the same insert otherwise —
# same ⌀4.6 knurl over the same ⌀4.0 recommended hole — so a station picks between them on the
# depth of its own bore and nothing else, and `heatset_dia` serves either.
#   A BORE IS NOT AN INSERT. `heatset_depth` is the POCKET: the body plus the relief a screw
# that outruns it needs. Anything asking how much thread a screw actually takes reads a length
# here and not that.
heatset_len = 4.0        # RX-M3Sx4.0, where a station cannot give the long body its depth
heatset_long_len = 5.7   # RX-M3x5.7, everywhere a station can
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
