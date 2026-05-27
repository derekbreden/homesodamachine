"""Shared interface for the Touch-Flo faucet's stacked geometry — the
small set of physical dimensions and derived pill / shank geometry that
every part in the faucet column (shell, mounting plate, mounting gasket,
under-counter plate) must agree on so the column stacks concentrically
and the flavor tubes drop through together.

Coordinates are in the repo's +Y-up frame: +Y is height, +X is lateral
(width), +Z is depth — the gooseneck dispenses toward +Z (the user's
side), so the flavor-tube pill sits at world -Z, behind the body axis."""


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
pill_width_z = flavor_tube_hole_dia                                # 7.05

# Depth magnitude of the flavor-tube pill center from the body / shank
# axis at world origin. The pill sits at world Z = −flavor_tube_depth
# (BEHIND the body, opposite the +Z gooseneck-dispense direction), tangent
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
