"""Shared interface for the Touch-Flo faucet's stacked geometry — the
small set of physical dimensions and derived pill / shank geometry that
every part in the faucet column (shell, mounting plate, mounting gasket,
under-counter plate) must agree on so the column stacks concentrically
and the flavor tubes drop through together."""


# 1/4" LLDPE flavor tube — physical fact, set by the vinyl tube the
# pumps push the syrup through.
flavor_tube_od = 6.35

# Tubes touch each other at Y=0, so each tube's center sits one tube
# radius out from Y=0. The pill cutout that covers both tubes is
# centered at Y=0 and stretches Y by ± this offset + the per-tube hole
# radius.
flavor_tube_y_offset = flavor_tube_od / 2.0  # 3.175

# Diametric (total) clearance around each flavor tube through the pill
# cutout — i.e. hole_dia − tube_od. Print-validated on PET-CF; see
# `touch-flo-shell/print-log.md`.
flavor_tube_hole_clearance = 0.7

# Per-tube hole diameter, derived.
flavor_tube_hole_dia = flavor_tube_od + flavor_tube_hole_clearance  # 7.05

# Pill cutout (rounded rectangle, Y-oriented) that covers both flavor
# tubes as a single opening. The two per-tube circles overlap by
# (hole_dia − 2 × y_offset), so we model the combined opening as the
# pill formed by sliding a circle of `flavor_tube_hole_dia` from
# Y=−y_offset to Y=+y_offset.
pill_length_y = 2.0 * flavor_tube_y_offset + flavor_tube_hole_dia  # 13.4
pill_width_x = flavor_tube_hole_dia                                # 7.05

# +X offset of the flavor-tube pill center from the body / shank axis
# at world (0, 0). Derived from the Westbrass valve body's outer
# cylinder radius (15.75) plus the flavor-tube radius — the pill is
# tangent to the body's +X face, so the flavor tubes butt up against
# the body wall.
flavor_tube_x = 18.925  # = body_r (15.75) + tube_r (3.175)

# Central pocket for the body's threaded shank. Ø12.6 matches the
# factory mounting plate; the threaded shank is ~Ø11 nominal. Used by
# all four parts in the column (shell uses it for the shank pocket
# alongside its `body_bore_diameter` for the body OD).
shank_hole_diameter = 12.6
