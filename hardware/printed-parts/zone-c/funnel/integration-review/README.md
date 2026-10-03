# Funnel integration review

The exported frame enters front-top along Y, and back-top captures its opposite
rails as the enclosure closes. `check_fit.py` measures the actual frame and shell
STLs through those motions. The seated pairs have no shared volume, and the
closed enclosure captures the frame against 2 mm translations in every axis
direction. [`rail-motion-check.json`](rail-motion-check.json) binds those
readings to the exported meshes.

The silicone capacity is 455.437 mL, nominally 455 mL. The frame's flat underside is Z299.9, its
socket floor is Z302.9. The carrier and elbow hang 0.65 mm below their insertion datum;
the 12.85 mm silicone block bears on the released carrier's 3.15 mm hook tops at Z306.05.
Both end corbels cross the full 207 mm width at 30°
from vertical. The drain hole is 11.25 mm, with the elbow cradle's two wing
slots beside it. Eight samples on an 8 mm-radius ring around the outlet measure
the remaining 3 mm web outside the hole and slots.

The complete 207 × 142.283 mm frame has its collar centre at Y164.55, while
the plug and drain share its Y164.55 centre. Both full-width corbels, rail wings and
the socket's 3 mm floor remain present. The brim pocket keeps a 3.114 mm
roof landing behind the display arris. The native
[`forward expansion check`](forward-expansion-check.json) records its capacity,
mounting datums, cable-hook fit and neighbouring tube clearances.

The side cable hook runs from Y95 to Y111.5. Its complete upper jaw retains a
3 mm tip at both ends and the middle, with 2.532 mm air to the frame. The native
2 mm-thickness DC-5 lead-entry probe reaches its seat without shared volume
with front-top or the frame. Its declared local path is 137.491 mm long; this
is a clearance probe and does not qualify an entire bundled loom or its cut length.

## Placed clearances

The [assembly scorecard](/hardware/manifold-layout/enclosure-assembly.scorecard.json)
records the current placed machine. The independent native-solid readings in
[`forward-expansion-check.json`](forward-expansion-check.json) cover the complete
frame and the authored tube bodies:

| Pair | Native clearance |
| --- | ---: |
| V-K / frame | 1.456 mm |
| Fluid-24 / frame | 1.150 mm |
| Fluid-26 / frame | 1.150 mm |
| Fluid-14 / V-A | 1.305 mm |
| Fluid-14 / frame | 1.133 mm |
| Fluid-2 / water pump | 1.092 mm |
| Fluid-18 / frame | 35.725 mm |

The [cap and tube review](/hardware/printed-parts/cold-core/foam-cap/fluid-18-clearance-check.json)
records fluid-18's anchor and cap fit. The drain starts at the released elbow's
aft mouth at X1.85, Y185.112, Z280.41 and finishes at V-B-I, X−22.35, Y286.46,
Z263.05. Its 199.008 mm native centreline has four R14 corners and falls or stays
level throughout. The 25.792 mm stub reaches through its full 3 mm silicone
sealing land.

The rear cap pocket has 0.25 mm running air in XY and no added Z clearance. Its
rear floor retains a complete 3.75 mm wall behind the actual flat pocket face;
the entire rounded pocket's bounding width has at least 3.5 mm of stock. The
nameplate's inboard receiver stands 1.379 mm above the cap crown, with 1 mm air
to the PSU and 3.129 mm of wall below the supported mouth. These are native
geometry checks; silicone sealing, flexible tubing, installed fit and retention
remain physical qualifications.

[`assembly-intersections.json`](assembly-intersections.json) is a separate
mesh review bound to its recorded source hashes. Its measurements apply to
those meshes; the current machine's measurements are in the scorecard.

## Native slice records

The current [front-top H2C native slice receipt](/hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md)
is bound to front-top's current STEP and STL, including the complete 16.5 mm
cable hook. It records the emitted first layers, complete fine roof band,
show-face support clearance and support-removal lanes. Its physical finish,
removal and installed fit remain separate observations.

The current [expanded-frame H2C receipt](native-slice-reviews/2026-10-03-funnel-frame-h2c-v1/README.md)
reviews all 205 model layers and four bed-rooted support bodies beneath the
external rail bearings. Every native stock component receives model walls, and
every emitted support bead has a clear outward removal sweep after its contact
and branch junctions are detached. The single brim-seat perimeter diagnostic
receives actual top-surface roads. These measurements qualify the recorded
slice; physical removal and installed frame fit remain separate observations.

The current [receiver coupon receipt](native-slice-reviews/2026-10-03-cradle-trial-receiver-h2c-v1/README.md)
reviews all 50 model layers of the matching 3 mm web, drain hole and wing slots.
It has no supports or perimeter diagnostics. The full frame and receiver keep
their flat underside on the bed, with a 0.20 mm first layer and ordinary 0.24 mm
layers above it. The stored [frame support audit](frame-support-audit.json) retains
its own source hashes and measurement scope.

The current [cradle H2C receipt](native-slice-reviews/2026-10-03-elbow-cradle-h2c-v2/README.md)
reviews all 154 model layers and the two external hook supports. Every native
stock component receives model walls; there are no perimeter diagnostics or
support-motion obstructions. The non-bearing collet mouth opens through a
constant-radius clearance, retaining a 5.103 mm floor and 8.840 mm side walls.
Its main elbow seat, 0.65 mm catch gap and 269.895 mm² silicone bearing remain
whole. The current production and trial cradle meshes are byte-identical.

The stored upper-enclosure toolpaths' first-layer and local wall-count checks pass.
The stored front-top audit retains
35 support bodies, including 29 without explicit interface labels. Back-top has
14 support bodies, including one without an explicit interface label.

The stored back-top review placement leaves only 2.958 mm between a support extrusion
and the shared bed edge, below the recipe's 10 mm target. Its print layout and
that archive's upper-shell support removal require separate review. Current
print receipts must name the current mesh hashes, bed placement, emitted paths
and removal lanes. Physical support removal and fit remain unqualified for this
geometry.

The accepted [v4 cradle trial](../cradle-trial/physical-acceptance.json) records
insertion of its printed pair and the 0.65 mm released drop. That drop is retained.
The current 3.15 mm hook thickness and flat silicone bearing are separately
checked in native geometry, including 29 sampled insertion poses with the
silicone funnel removed. The v4 result does not establish physical acceptance
of those changed features or production frame and shell fit.
