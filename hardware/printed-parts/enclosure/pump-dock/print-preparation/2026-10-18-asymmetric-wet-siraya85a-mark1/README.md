# Asymmetric junction and fixed-return TPU preparation

Scope: the eight saved October 18 meshes and native projects. Current elbow-fed junction geometry and the three gravity-seated keepers are specified in the [current dock design](../../README.md). These archived projects do not prepare current parts.

The manual preparer makes eight station-specific projects: four permanent pump
junctions and four compound returns. Each plate contains one normal object and a
local support blocker. The source supplies the handed print pose, the actual wet
passage and the complete part geometry.

It uses the saved Siraya Tech Flex TPU85A Clear recipe from the
[October 14 single-elbow article](https://github.com/derekbreden/homesodamachine/blob/e59c4f46ec277160e3eba3883aac7b79aba253e3/future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json),
with the right 0.6 mm nozzle mapping, 0.20 mm first layer and 0.12 mm normal
layers. Temperature, flow, retraction and wipe settings stay in that retained
recipe. Exterior supports use Tree (auto), Default, including the normal
sections that Bambu generates automatically.



Preparation does not contact a printer. Native slicing is opt-in for the exact
part names passed with `--slice`; `--slice-all` slices every selected project.
`--part` restricts preparation to named parts; every explicit `--slice` name must
also be selected. This manual helper is outside the
normal CAD producer path.

The eight editable projects live in `plates/{part}/`. The
[native review](native-review.json) binds each project to its own emitted G-code,
source geometry and preparation mesh. Preparation uses 0.025 mm STL deflection
and 0.10 rad angular tolerance. The canonical download meshes use 0.005 mm and
0.05 rad; the prepared project meshes are separate artifacts, with their own
hashes. The bead reader retains a 0.05 mm distance allowance.

| Editable project | Native filament (g) | Native time (h:mm:ss) |
| --- | ---: | ---: |
| [West outer junction](https://homesodamachine.com/print-archive/d9c6a4af163a674b8372e0f78dcd692aa4d4d3fb/enclosure-pump-receiver-west-outer.3mf) | 8.045 | 1:49:26 |
| [West outer return](https://homesodamachine.com/print-archive/6ed0809b2c8dd68411f02ef768b57a4397da312d/enclosure-pump-return-west-outer.3mf) | 6.664 | 1:54:51 |
| [West inner junction](https://homesodamachine.com/print-archive/813ae80784b74d2958cdbce27fdef7bb4aeccc82/enclosure-pump-receiver-west-inner.3mf) | 8.024 | 1:49:11 |
| [West inner return](https://homesodamachine.com/print-archive/8ab8abb0ca3d98894f05fe5fd2859be9d7615477/enclosure-pump-return-west-inner.3mf) | 5.662 | 1:36:06 |
| [East inner junction](https://homesodamachine.com/print-archive/0664024d12e7bcc10fa85ac4b1c01aed17329e4a/enclosure-pump-receiver-east-inner.3mf) | 8.024 | 1:49:11 |
| [East inner return](https://homesodamachine.com/print-archive/46df69183746976d74278c3e8d4f17b5d7ec8bdc/enclosure-pump-return-east-inner.3mf) | 5.662 | 1:36:06 |
| [East outer junction](https://homesodamachine.com/print-archive/4f7a1faf440940fe5cc9d24f2e188bbbbe328e59/enclosure-pump-receiver-east-outer.3mf) | 8.054 | 1:49:38 |
| [East outer return](https://homesodamachine.com/print-archive/b8cd081deb8be00e101fcb5be015d64e69e618f9/enclosure-pump-return-east-outer.3mf) | 6.662 | 1:54:50 |
| **All eight** | **56.798** | **14:19:19** |

These are the eight actual native-slice estimates, rounded here; exact values and
project hashes are in the [native review](native-review.json). Every project's emitted-path
readings bind its current G-code. They do not include
the four PET-GF dock parts. No printer was contacted or launched.

The retained wet recipe requests six walls and 100% infill. The parts carry no
keys: the return block holds each return by its round body, and each junction's
neck snaps into its flat keeper.

The blocker is the vertical projection of the actual wet passage, expanded
0.65 mm in XY and extended from 2 mm below the bed to 2 mm above the part. It
excludes support contacts in that named wet shadow. A blocker does not itself
prove that every tree branch avoids the passage: review the emitted support
beads, first and second layers, and nonextruding moves against the actual cavity.
The junction's lower socket retains its six-millimetre sealing land and tube-tip
station, with a 0.30 mm radial stop ledge followed by a 45-degree bore taper.

The [Siraya article's exterior result](https://github.com/derekbreden/homesodamachine/blob/e59c4f46ec277160e3eba3883aac7b79aba253e3/future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json)
was accepted, while internal stringing was reported. That result does not qualify
these parts' internal finish, support release, wet service, seals, pressure
retention or life. Single-object placement and native travel avoidance do not
prove clean bores. The emitted-path review records opportunities for loose
strands; a printed inspection remains necessary to establish actual internal
finish.

The [recorded source](https://github.com/derekbreden/homesodamachine/blob/651f0d96d5fb06c74aea20a49442740bdb2f191f/hardware/printed-parts/enclosure/pump-dock/print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/prepare.py) defines this artifact's preparation and reading.
