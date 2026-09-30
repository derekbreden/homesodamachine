# Nameplate receiver with 0.35 mm body X clearance

Mark2 accepted task **1296373726** at 2026-09-30T15:01:53.496691+00:00.
The native estimate is **43 min 6 sec**, **20.10 g** at the saved profile density.
Use the existing flat 3.36 mm nameplate from task 1294806669.

| Interface | Clearance |
|---|---:|
| Body X, each side through the full seating depth | 0.35 mm |
| Total body X travel | 0.70 mm |
| Wing tip X, centered | 0.45 mm |
| Wing tip X at full body sideways travel | 0.10 mm |
| Wing thickness to flat retaining bearing in Y | 0.30 mm |
| Body and wing ordinary Z end | 0.15 mm |
| Body and wing print-down Z end | 0.40 mm |
| Total Z travel | 0.55 mm |
| Back and wing undersides at the seating datum | 0 mm |
| Minimum wing overlap at full sideways travel | 1.70 mm |
| Minimum flat bearing width at full sideways travel | 0.80 mm |

[Exact solid comparison](geometry-delta.json) confines the 47.3676 mm³ removal
to the full-depth body X opening and wing-slot X ends, with no added material.
The slot ends permit the wider body travel while retaining 0.10 mm at its limits.
The seating floor, Y thickness gap, Z gaps, entry bevel planes, external stock
and existing nameplate are fixed. All six pure-axis seating limits and clashes
just beyond them pass. Shared clearance rules are unchanged.

The receiver prints in the enclosure back-top orientation with shared PET-GF
tree supports: 0.40 mm support XY, 0.45 mm upper Z and 0.30 mm lower Z gaps.
Every emitted support bead clears both wing slots and entry bevels. One support
body rises from the bed to a labelled interface after 41.28 mm; physical removal
remains a bench check. The job uses black PET-GF on Mark2's left 0.4 mm nozzle,
+0.04 mm trim, a 0.20 mm first layer and 0.24 mm above, with saved speeds and
wall order. Usual startup options apply, including Auto nozzle offset.

[Native verification](verification.json) binds source hashes, archive checksum,
192 model layers and the support review. The ideal 101-position insertion envelope
and [geometry lint](geometry-lint.log) pass. These checks do not establish printed
flatness, force or retention. [Published artifacts](published-artifacts.json)
match the live STEP and viewer payload.

[Launch](launch.json) records the accepted job and more than three minutes of
spacing after H2C's display receiver. [Postlaunch](postlaunch.json) confirms the
matching task is RUNNING without errors.
