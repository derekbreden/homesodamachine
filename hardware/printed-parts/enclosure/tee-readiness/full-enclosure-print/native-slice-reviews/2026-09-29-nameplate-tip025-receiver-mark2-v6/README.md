# Nameplate wing-tip clearance receiver

Mark2 accepted task **1295032042** at 2026-09-30T02:37:46.257148+00:00.
The receiver-only native estimate is **42 min 37 sec**, **20.12 g**. Use the
existing flat 3.36 mm nameplate from the v5 pair.

Each wing tip has **0.25 mm X clearance**, measured with the plate centered.
The body locates X with 0.15 mm per side, so the minimum tip gap at full body
float is 0.10 mm. All other mating geometry is unchanged. Slot normal clearance
is 0.15 mm, Z travel is 0.55 mm including the one rough-end allowance, and
minimum wing retention overlap is 2.10 mm.

[Geometry comparison](geometry-delta.json) confirms exactly two 0.10 mm strips
removed from the slot ends, zero material added, no changes outside those strips,
and the same nameplate STL. Printed corner rounding is a hypothesis for the
reported bow, not a measured defect or established universal clearance rule.

The receiver is in its enclosure orientation, using the shared PET-GF tree
support profile: 0.40 mm XY, 0.45 mm upper Z and 0.30 mm lower Z. Every support
bead clears both wing slots and entry bevels. It uses black PET-GF on the left
0.4 mm nozzle, the established +0.04 mm trim, a 0.20 mm first layer and 0.24 mm
above it, normal speeds and wall order. Nozzle Offset Calibration remains Auto.

[Verification](verification.json) checks source hashes, native archive integrity,
192 model layers, support settings and slot paths. Geometry lint has zero
unanswered findings. [Launch](launch.json) records the accepted job and ordinary
startup settings. The [physical result](physical-result.json) records residual bowing with no clear
improvement. The plate lies flat when removed and when inverted with its wings
disengaged; the contact surface causing engagement load is unresolved.
