# Asymmetric junction and fixed-return TPU preparation

The manual preparer makes eight station-specific projects: four permanent pump
junctions and four compound returns. Each plate contains one normal object and a
local support blocker. The source supplies the handed print pose, the actual wet
passage and the complete part geometry.

It uses the saved Siraya Tech Flex TPU85A Clear recipe from the
[October 14 single-elbow article](../../../../../../future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json),
with the right 0.6 mm nozzle mapping, 0.20 mm first layer and 0.12 mm normal
layers. Temperature, flow, retraction and wipe settings stay in that retained
recipe. Exterior supports use Tree (auto), Default, including the normal
sections that Bambu generates automatically.

Run from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python \
  hardware/printed-parts/enclosure/pump-dock/print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/prepare.py \
  --out .cache/pump-dock-engineering/compact-fixed-returns/prepared-wet-parts
```

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
| [West outer junction](plates/enclosure-pump-receiver-west-outer/enclosure-pump-receiver-west-outer.3mf) | 7.602 | 1:53:51 |
| [West outer return](plates/enclosure-pump-return-west-outer/enclosure-pump-return-west-outer.3mf) | 8.159 | 2:12:37 |
| [West inner junction](plates/enclosure-pump-receiver-west-inner/enclosure-pump-receiver-west-inner.3mf) | 7.792 | 1:55:52 |
| [West inner return](plates/enclosure-pump-return-west-inner/enclosure-pump-return-west-inner.3mf) | 7.039 | 1:53:19 |
| [East inner junction](plates/enclosure-pump-receiver-east-inner/enclosure-pump-receiver-east-inner.3mf) | 7.780 | 1:55:40 |
| [East inner return](plates/enclosure-pump-return-east-inner/enclosure-pump-return-east-inner.3mf) | 7.031 | 1:53:08 |
| [East outer junction](plates/enclosure-pump-receiver-east-outer/enclosure-pump-receiver-east-outer.3mf) | 7.539 | 1:53:07 |
| [East outer return](plates/enclosure-pump-return-east-outer/enclosure-pump-return-east-outer.3mf) | 8.153 | 2:12:25 |
| **All eight** | **61.094** | **15:50:00** |

These are the eight actual native-slice estimates, rounded here; exact values and
project hashes are in the [native review](native-review.json). They do not include
the twelve PET-GF fixture parts. No printer was contacted or launched.

The retained wet recipe requests six walls and 100% infill. Each readback also
records the actual mounting keys intersected with the cut body, including their
connected roots, with posed bounds, solid volume and an exact local-to-print
transform. The emitted-path review checks model perimeters and infill through
those regions. Settings and geometric bead coverage do not establish printed
key strength or life.

The blocker is the vertical projection of the actual wet passage, expanded
0.65 mm in XY and extended from 2 mm below the bed to 2 mm above the part. It
excludes support contacts in that named wet shadow. A blocker does not itself
prove that every tree branch avoids the passage: review the emitted support
beads, first and second layers, and nonextruding moves against the actual cavity.
The junction's lower socket retains its six-millimetre sealing land and tube-tip
station, with a 0.30 mm radial stop ledge followed by a 45-degree bore taper.

The [Siraya article's exterior result](../../../../../../future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json)
was accepted, while internal stringing was reported. That result does not qualify
these parts' internal finish, support release, wet service, seals, pressure
retention or life. Single-object placement and native travel avoidance do not
prove clean bores. The emitted-path review records opportunities for loose
strands; a printed inspection remains necessary to establish actual internal
finish.
