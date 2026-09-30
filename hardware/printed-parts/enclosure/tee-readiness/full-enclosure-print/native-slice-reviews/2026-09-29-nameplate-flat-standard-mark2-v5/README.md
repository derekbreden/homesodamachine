# Flat nameplate and standard-clearance receiver — Mark2

Mark2 job **1294806669** was accepted at **2026-09-30 00:41:09 UTC**. Native estimate:
**1 h 13 min 9 s**, **33.64 g**. The [launch receipt](launch.json) records the correct
new job name, RUNNING state and no printer error or HMS. H2C's display trial accepted
at 22:36:15 UTC; the launches meet the three-minute minimum spacing.

The nameplate has a uniform 3.36 mm face without a raised perimeter, and both
horizontal wings start on the bed. All 29 artwork solids rise 0.48 mm, with the
accepted native white correction X −0.50 mm, Y +0.70 mm. Both 0.4 mm hotends use
external PET-GF: black left, white right. Requested Mark2 trim is +0.04 mm; the
textured-plate branch emits +0.02 mm. Normal launch options are preserved.

The matching receiver uses standard static clearances. Total pure-axis travel is
0.30 mm in X, 0.15 mm in Y and 0.55 mm in Z. Z includes 0.15 mm at each end plus
0.25 mm at the one rough print-down receiver end. There is no sliding or low-force
addition. A 1.10 × 0.40 mm entry bevel clears wing rotation during hand-bent insertion;
the flat retaining bearing retains the 0.15 mm seated gap. Minimum flat bearing
width is 1.00 mm, with 2.10 mm geometric overlap at full X travel.

The nameplate has **no supports**. The receiver uses the shared PET-GF **tree**
supports, in its enclosure orientation, with black body and interface material.
All emitted support beads clear the wing slots and their entry bevels. Requested
support clearances are XY 0.40 mm, top Z 0.45 mm and bottom Z 0.30 mm.

Both objects share a 0.20 mm first layer, a 0.28 mm second layer and 0.24 mm layers
above. This schedule permits the prime tower and puts complete raised artwork
layers at 3.60 and 3.84 mm. The nameplate finishes at layer 16; the paired job has
192 layers. Saved speeds and wall order apply.

[Verification](verification.json) checks exported-solid travel limits, emitted
artwork, wing layers and support paths. [Registration verification](registration-verification.json)
compares the native corrected paths with a zero-offset slice of the same geometry.
The exact archive, source and verification hashes are in [manifest.json](manifest.json).
Geometry lint has no unanswered findings. An ideal bend check covers 101 insertion
positions; insertion force, warping, looseness, support removal, retention and QR
scanning require the physical pair.
