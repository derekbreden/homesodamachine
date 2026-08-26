"""Shared interface for the faucet's stacked geometry — the
small set of physical dimensions and derived pill / shank geometry that
every part in the faucet column (shell, above-counter plate, above-counter
gasket, under-counter plate) must agree on so the column stacks concentrically
and the flavor tubes drop through together.

Coordinates are in the repo's +Z-up frame: +Z is height, +X is lateral
(width), +Y is depth — the gooseneck dispenses toward -Y (the user's
side), so the flavor-tube pill sits at world +Y, behind the Westbrass's axis
(toward the back of the appliance)."""

import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents
                            if p.name == "printed-parts") / "cadlib"))

import fits  # noqa: E402


# 1/4" LLDPE flavor tube — physical fact, set by the vinyl tube the
# pumps push the syrup through.
flavor_tube_od = 6.35

# Tubes touch each other at X = 0, so each tube's center sits one tube
# radius out from X = 0 on the lateral axis. The pill cutout that
# covers both tubes is centered at X = 0 and stretches X by ± this
# offset + the per-tube hole radius.
flavor_tube_x_offset = flavor_tube_od / 2.0  # [3.175 mm](FLAVOR_TUBE_X_OFFSET)

# Diametric (total) clearance around each flavor tube through the pill
# cutout — i.e. hole_dia − tube_od. Set from tube fitment on printed
# fibre-filled PET; see `faucet-shell/print-log.md`.
flavor_tube_hole_clearance = 0.9

# Per-tube hole diameter, derived.
flavor_tube_hole_dia = flavor_tube_od + flavor_tube_hole_clearance  # [7.25 mm](FLAVOR_TUBE_HOLE_DIA)

# Pill cutout (rounded rectangle, X-oriented) that covers both flavor
# tubes as a single opening. The two per-tube circles overlap by
# (hole_dia − 2 × x_offset), so we model the combined opening as the
# pill formed by sliding a circle of `flavor_tube_hole_dia` from
# X = −x_offset to X = +x_offset.
pill_length_x = 2.0 * flavor_tube_x_offset + flavor_tube_hole_dia  # [13.6 mm](PILL_LENGTH_X)
pill_width_y = flavor_tube_hole_dia                                # [7.25 mm](PILL_WIDTH_Y)

# Depth magnitude of the flavor-tube pill center from the Westbrass /
# shank axis at world origin. The pill sits at world Y = +flavor_tube_depth
# (BEHIND the Westbrass, opposite the −Y gooseneck-dispense direction),
# tangent to its back face. Derived from the Westbrass's outer cylinder
# radius (15.75) plus the flavor-tube radius — the pill is tangent to that
# back face, so the flavor tubes butt up against the Westbrass wall.
flavor_tube_depth = 15.75 + flavor_tube_x_offset  # [18.925 mm](FLAVOR_TUBE_DEPTH)

# Central pocket for the shank. Ø12.6 matches the donor's own factory
# plate; the threaded shank is ~Ø11 nominal. Used by all four parts in the
# column (shell uses it for the shank pocket alongside its
# `westbrass_bore_diameter` for the Westbrass OD).
shank_hole_diameter = 12.6


# Waveshare ESP32-S3-Touch-LCD-1.47 faucet display (faucet BOM §1) —
# caliper-measured device envelope, shared by the faucet-assembly
# stand-in and the shell's display cradle. Front to back: the plastic
# housing (screen glass flush in its front face) overhangs the PCB by
# ~[0.275 mm](DISPLAY_HOUSING_OVERHANG) per side; below the PCB underside, components protrude with
# the metal feet as the extreme point. Native depth axis: z = 0 at the
# feet (the device's bounding back), +z toward the screen.
display_housing_width = 24.50   # plastic housing, lateral
display_housing_length = 44.50  # plastic housing, along the device's long axis
display_pcb_width = 23.95       # PCB centered under the housing
display_pcb_length = 43.95
display_corner_r = 5.75         # housing corners (vendor drawing)
display_pcb_corner_r = display_corner_r - (display_housing_width - display_pcb_width) / 2.0
display_total_depth = 10.35     # housing front face → bottom of the metal feet
display_housing_depth = 5.00    # housing front face → housing bottom (= PCB top)
display_pcb_bottom_from_front = 6.45  # housing front face → PCB underside
# Native-frame boundary planes, z = 0 at the feet.
display_pcb_bottom_z = display_total_depth - display_pcb_bottom_from_front  # [3.9 mm](DISPLAY_PCB_BOTTOM_Z)
display_pcb_top_z = display_total_depth - display_housing_depth             # [5.35 mm](DISPLAY_PCB_TOP_Z)


# Display cover plate — the printed face plate screwed down over the
# device, and the figures the shell's cradle and the plate both cut to.
# The cradle parts at the device's own PCB-to-housing step: the shell
# holds the board and the plate comes down over the housing, so the seam
# a hand finds is a step the device already has rather than a height
# chosen for it.
#
# The plate butts the shell's land the whole way round, and is held at
# one end by a screw and at the other by a hook the cradle's south wall
# makes for it. That wall's thickness is the hook's, not a wall's: see
# the DISPLAY CRADLE section of faucet_shell.py.
display_cover_wall = 1.86       # skirt and bezel — three 0.62 extrusions, the cradle's wall
display_cover_slip = fits.slip  # per side, plate against the shell
# How far the bezel laps the device's face on every edge. The screen is
# 17.75 x 32.93 in a 24.5 x 44.5 housing, so 2 mm of lap stops 1.4 mm
# short of the glass on the sides and 3.8 mm short on the ends.
display_cover_lap = 2.0
display_cover_over_face = 0.10  # the bezel clears the device's face by this
# One M3 above the device's north edge. The plate's skirt bottoms on the
# shell's land, so the screw pulls the plate down onto a hard stop and
# the device is captured with clearance rather than clamped.
display_cover_screw_len = 8.0   # M3 x 8 DIN 912 socket head cap, black oxide
display_cover_head_h = 3.0
display_cover_seat_recess = 0.2                                          # head sits this far under the face
display_cover_cbore_depth = display_cover_head_h + display_cover_seat_recess  # [3.2 mm](DISPLAY_COVER_CBORE_DEPTH)
