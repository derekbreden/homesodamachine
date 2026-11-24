# PET-GF supports

Take Support D's contact and bridge settings from the [shared PET-GF profile](petgf.profile.json),
including when a preparer takes its other settings from an accepted older print. Match the
embedded filament bridge speeds to the project. The [rollout record](support-D-rollout.json)
identifies the projects and slices using D. Archived prints retain the settings they ran.

Each part owns its support style, roots, removal access, authored fins and support-free
regions. For accessible exterior features, use Tree (auto) with the saved Bambu Default
style. Enclosed cavities need branching trees with room to extract them. Read the actual
contact planes, removal openings and first underside courses in the native slice. A narrower
bed footprint is no reason to put a rectangular support block inside a cavity.

## Tree trunks

Keep the profile's `tree_support_branch_diameter`, `tree_support_branch_diameter_angle`
and `tree_support_wall_count`. A `tree_support_branch_angle` override must still let
tips meet and form a trunk that thickens toward its root. This applies to isolated
tips as well as groups of columns. On the [stopped back-top print](https://github.com/derekbreden/homesodamachine/blob/442ac2b7c23d85ee12d16088b3ad89388730cc91/hardware/printed-parts/enclosure/enclosure/prints/2026-11-14-back-top-engineering-stock-z-mark1/physical-result/physical-result.json),
tip-sized columns broke away and left the surfaces above them unsupported.

## Edge fins

For a visible overhang edge with reported roughness, carry the edge on a removable fin
wall and use Tree (auto)/Default on the remaining surfaces. On a curved edge, interrupt
the arc and put the release gaps away from the most visible midpoint. Keep each fin's
contact strip, breaks, bed anchorage and reason with the part. The [faucet-base trial](faucet/finish-coupons/README.md#curved-edge-fins)
records the finish and release for the tested pose.
