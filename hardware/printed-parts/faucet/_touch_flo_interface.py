"""Shared interface for the Touch-Flo faucet's stacked geometry — the
small set of physical dimensions and derived pill / shank geometry that
every part in the faucet column (shell, mounting plate, mounting gasket,
under-counter plate) must agree on so the column stacks concentrically
and the flavor tubes drop through together.

Coordinates are in the repo's +Z-up frame: +Z is height, +X is lateral
(width), +Y is depth — the gooseneck dispenses toward -Y (the user's
side), so the flavor-tube pill sits at world +Y, behind the body axis
(toward the back of the appliance)."""


# 1/4" LLDPE flavor tube — physical fact, set by the vinyl tube the
# pumps push the syrup through.
flavor_tube_od = 6.35

# Tubes touch each other at X = 0, so each tube's center sits one tube
# radius out from X = 0 on the lateral axis. The pill cutout that
# covers both tubes is centered at X = 0 and stretches X by ± this
# offset + the per-tube hole radius.
flavor_tube_x_offset = flavor_tube_od / 2.0  # 3.175

# Diametric (total) clearance around each flavor tube through the pill
# cutout — i.e. hole_dia − tube_od. Print-validated on PET-CF; see
# `touch-flo-shell/print-log.md`.
flavor_tube_hole_clearance = 0.7

# Per-tube hole diameter, derived.
flavor_tube_hole_dia = flavor_tube_od + flavor_tube_hole_clearance  # 7.05

# Pill cutout (rounded rectangle, X-oriented) that covers both flavor
# tubes as a single opening. The two per-tube circles overlap by
# (hole_dia − 2 × x_offset), so we model the combined opening as the
# pill formed by sliding a circle of `flavor_tube_hole_dia` from
# X = −x_offset to X = +x_offset.
pill_length_x = 2.0 * flavor_tube_x_offset + flavor_tube_hole_dia  # 13.4
pill_width_y = flavor_tube_hole_dia                                # 7.05

# Depth magnitude of the flavor-tube pill center from the body / shank
# axis at world origin. The pill sits at world Y = +flavor_tube_depth
# (BEHIND the body, opposite the −Y gooseneck-dispense direction), tangent
# to the body's back face. Derived from the Westbrass valve body's outer
# cylinder radius (15.75) plus the flavor-tube radius — the pill is
# tangent to the body's back face, so the flavor tubes butt up against
# the body wall.
flavor_tube_depth = 15.75 + flavor_tube_x_offset  # 18.925

# Central pocket for the body's threaded shank. Ø12.6 matches the
# factory mounting plate; the threaded shank is ~Ø11 nominal. Used by
# all four parts in the column (shell uses it for the shank pocket
# alongside its `body_bore_diameter` for the body OD).
shank_hole_diameter = 12.6


# Waveshare ESP32-S3-Touch-LCD-1.47 flavor display (faucet BOM §1) —
# caliper-measured device envelope, shared by the faucet-assembly
# stand-in and the shell's display cradle. Front to back: the plastic
# housing (screen glass flush in its front face) overhangs the PCB by
# ~0.275 mm per side; below the PCB underside, components protrude with
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
display_pcb_bottom_z = display_total_depth - display_pcb_bottom_from_front  # 3.90
display_pcb_top_z = display_total_depth - display_housing_depth             # 5.35
