# Rear equipment snap fit trial

Five complete receiver/cap pairs test 2.0 mm spring leaves, R1.5 inside root
transitions and a centered 5 × 1 mm screwdriver entry beneath each hook.
The hook's 2.6 mm flat overlap continues on either side of the tool entry.
Root-to-catch length is 22.25 mm, with a 21.25 mm water-regulator exception;
the straight wall above the root blend is 20.75 mm and 19.75 mm respectively.
All five caps stand on an axial end so the wing bending lies in the layer
plane. Receivers retain their parent production orientation.

The accepted pump and ASSE hardware cavities and the meter receiver/wire
room are retained. Local receiver relief clears the rounded spring roots.
The pump retains its filled 6.2 mm-crown box body and continuous rail seats.
The meter cap has a 9 mm solid spine, 4 mm of central bearing stock toward
the hardware and 0.25 mm shaped clearance; its receiver retains 0.75 mm air.
The PISCO cap has body-bearing stock and a separate raised lip around the
exposed outlet neck, clear of the collet. Its cap air is 0.4 mm; receiver
radial air is 0.5 mm.

The water-regulator cavity follows the measured native radial profile and
its actual installed axis. Receiver radial air is 0.30 mm, cap radial air
0.25 mm and axial air 0.25 mm. The profile preserves the housing-to-neck
shoulder; its reduction can enlarge the clearance envelope by at most
0.06 mm. The cap's central bearing stock reaches the hardware axis while
the spring leaves retain their independent length. The lowest cap face
remains Z315.924 mm. [revision.json](revision.json) records the fit
investigation and the selected dimensions.

[geometry.json](geometry.json) records ten valid single native solids and
watertight meshes, zero seated cap/receiver interference, zero installed
hardware interference, and blocked empty-cap removal. Meter insertion is
clear at 0, 4, 8, 12 and 16 mm.
[native-review.json](native-review.json) records clear neighboring hardware
and caps, and obstruction of water-regulator translations of 0.5 mm in all
six directions. These are geometric checks; hand force, distributed bending,
release, fatigue and pump vibration require the physical trial.
[production-comparison.json](production-comparison.json) binds the native
trial caps to their matching Rust production exports.

[assembly-integration.json](assembly-integration.json) binds the revised
production receivers, lid and five caps in the retained assembly context.
All 447 unrelated appliance viewer members retain their exact arrays.

| Printer | Samples | Native estimate | PET-GF | Minimum bead margin |
| --- | --- | --- | --- | --- |
| Mark1 | Pump receiver, ASSE pair, PISCO pair | 3 h 13 min | 112.16 g | 86.522 mm |
| Mark2 | Pump cap, meter pair, water regulator pair | 4 h 24 min | 173.85 g | 96.222 mm |

[print-jobs.json](print-jobs.json) binds the prepared plates and unchanged
G-code in their print-only archives, and records whether each job has been
accepted. PET-GF uses three Classic walls, solid cap infill, 15% gyroid
receiver infill, Tree(auto)/Default supports, 0.20 mm first layers and
0.24 mm normal layers with localized cooling. First-to-second-layer bead
overlap is at least 91.5% on Mark1 and 91.1% on Mark2. Textured-plate trims
emitted in the G-code are Z0.16 and Z0.02 respectively.
Both plates are prepared. Neither new job has been accepted: Connect drops
the imports and Studio stops responding during sender setup. The recorded
printer readback still names the completed v2 jobs.

Use a tiny flathead screwdriver that fits inside the cavities to remove
their accessible automatic supports. Derek reports easy removal with that
tool. Use a flat blade no wider than 5 mm and no thicker than 1 mm at the
centered hook entries for cap release. Preserve the flat retention bearings.
Fit each empty cap first, then the hardware; record insertion, release,
rocking, whitening, where the wings bend and any residual deformation.
Test the pump's fixed rail seats with all four removable rubber foot
assemblies removed.

The [v2 physical result](../v2/physical-result/physical-result.json) records
the fit observations this trial answers. The pump-base fracture is an
observation only and requests no geometry change.

```sh
python3 tools/run.py --cad -- tools/cad-venv/bin/python hardware/print-tests/rear-snap-retention/build.py --output hardware/print-tests/rear-snap-retention/v3 --check-fit
python3 tools/run.py -- tools/cad-venv/bin/python hardware/print-tests/rear-snap-retention/prepare.py --trial hardware/print-tests/rear-snap-retention/v3 --plate all
```
