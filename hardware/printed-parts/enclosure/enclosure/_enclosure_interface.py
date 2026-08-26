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
