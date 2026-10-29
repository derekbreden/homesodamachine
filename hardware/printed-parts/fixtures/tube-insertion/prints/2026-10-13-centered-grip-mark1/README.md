# Centred plus-handle jaws — Mark1 task 1335878319

Mark1 accepted both PET-GF jaw halves on October 13 at 10:08 am CDT.
Derek authorized the launch with “Mark1 is available for PET-GF right now,
please print your new plus handle there.” The printer's
[completion observation](completion.json) reports FINISH at 63/63 layers
with no printer error or HMS fault. The
[physical acceptance](../../physical-acceptance.json) records successful
insertion: the handle alone starts the tube well, and the full tool makes
the final press very easy.

D and E use the reviewed centred plus geometry from source commit
`b67ed572f`. Their closure screws, liner length and crossbar share X22.
The two 9 mm TPU liners are a separate plate; this job contains only the
PET-GF jaws. Reuse the existing base, carrier and metal hardware.

- [Exact launched native slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-13-centered-grip-mark1/tube-insertion-centered-grip-petgf-left04-z018-mark1.gcode.3mf)
- [Exact G-code for Studio preview](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-13-centered-grip-mark1/tube-insertion-centered-grip-petgf-left04-z018-mark1.gcode)
- [Editable native project](tube-insertion-centered-grip-petgf-left04-z018-mark1.3mf)
- [Project settings and source meshes](tube-insertion-centered-grip-petgf-left04-z018-mark1.print.json)
- [Native slice review and checksums](tube-insertion-centered-grip-petgf-left04-z018-mark1.readiness.json)
- [Native support review](tube-insertion-centered-grip-petgf-left04-z018-mark1.support-audit.json)
- [Preflight printer observations](preflight.json)
- [Launch receipt and startup spacing](launch.json)
- [Fresh startup observation](startup.json)

The slice uses black Polymaker PET-GF through Mark1's left hardened
0.4 mm nozzle and external spool 254, textured PEI, a 0.20 mm first layer,
0.24 mm normal layers, six walls and 100% zig-zag infill. Automatic
Tree/default supports reach the two underside locator pockets and two
side-entry nut pockets. Standard +0.18 mm user Z trim emits `G29.1 Z0.16`
after the reset to zero. All executable G-code lines match the reviewed
Mark2 slice after excluding those printer-specific trim commands.
The estimate is 2 hours 33 minutes and 126.7 g using the saved material
density. The complete emitted bead footprint has at least 100.25 mm of
usable-bed edge clearance.

Timelapse and bed leveling are On; flow dynamic calibration and nozzle
offset calibration are Auto. Mark2 task 1334704608 was accepted at
12:08 am CDT, 10 hours 18 seconds before Mark1's acceptance. The receipt
records both UTC observations and the required 180-second minimum.
The initial receipt retains the previous job's stale layer count;
`startup.json` records the fresh 0/63 observation for this task.
