# TPU donor hand hold-down pad

This one-piece TPU pad conforms to the Touch-Flo's rounded transition and
the flat metal face immediately below the lever attachment. Its flat hand
face stands 2 mm above the existing PET-GF reaction walls. A narrow bridge
clears the cylindrical base by 1 mm and joins a compression tongue in the
open shank canyon. Hand pressure passes through the conforming underside
to the donor metal.

The bearing pad covers donor axial coordinates 13.5–36 mm: the R6 transition
and 17 mm of the flat face. It ends 3 mm before the 39 mm plateau where the
lever attaches. The pad's sides stop on the upper flat metal face. The
faucet lever remains attached, down and unpressed throughout tube insertion,
as recorded in the
[physical assembly observations](../../../faucet/lever-replica/assembly-observations.json).
The contact view includes the donor up to its arches. The installed lever
transform is unmeasured and is not drawn; physical clearance remains an
ordinary unloaded fit check.

![Contact zone: blue TPU pad, dark existing base and metal donor](art/fit.png)

| Feature | Nominal dimension |
| --- | ---: |
| Transition radius | 6 mm |
| Bearing region along donor axis | 13.5–36 mm |
| Flat metal contact length × width | 17 × 26 mm |
| Bearing pad to lever attachment | 3 mm |
| Hand face above PET-GF walls | 2 mm |
| Bridge clearance above cylindrical base | 1 mm |
| Existing canyon width | 11.8 mm |
| Retention tongue width | 12.8 mm |
| Compression allowance | 0.5 mm per side |
| Tongue entry width | 11.3 mm |
| Thread clearance below tongue | 10.25 mm |
| Tongue engagement below wall top | 8.25 mm |
| Full-width compression engagement | 7.5 mm |
| Axial clearance from lower cradle | 1.5 mm |
| Backing above flat metal contact | 17.5 mm |
| Print bounding box | 61.5 × 26 × 17.5 mm |

## Print

Print one in black TPU 85A with the broad flat hand face on the bed and
the conforming transition and flat contact upward. That face gives
1084.2 mm² of bed contact. Successive cross-sections shrink as the contact
opens and the bridge and tongue end, so the part needs no supports in
this orientation.

![Manufacturing pose: flat hand face on the bed, conforming contact up](art/print-pose.png)

The editable native project is
[`ready/donor-hold-down-transition-tpu85a-right06-z018-mark1.3mf`](ready/donor-hold-down-transition-tpu85a-right06-z018-mark1.3mf).
The reviewed print archive is
[`ready/donor-hold-down-transition-tpu85a-right06-z018-mark1.gcode.3mf`](ready/donor-hold-down-transition-tpu85a-right06-z018-mark1.gcode.3mf).
Both use Mark1's right fixed 0.6 mm nozzle, external black TPU 85A spool
255, textured PEI, 0.18 mm layers, a 0.30 mm first layer and 100% zig-zag
infill. The user Z trim is Mark1's standard +0.18 mm; the emitted plate
compensation is `G29.1 Z0.16` after the reset to zero.

The native slice has 97 layers, no generated supports, at least 121.4 mm
full-bead bed-edge clearance and no slicer warning. Estimated use is
18.5 g and 2 hours 3 minutes. These files are prepared offline; the transition
pad has no printer submission or physical result. The separate
[cylindrical-base pad job](prints/2026-10-12-mark1/README.md) identifies
Mark1 task 1334447551 accepted on October 12 at 9:20 pm CDT and retains
its exact printed geometry and archive.

## Fit and use

1. Leave the faucet lever attached, down and unpressed. Seat the donor in
   its existing cradle with its metal base annulus against the reaction wall.
2. Lower the bearing pad onto the transition and flat metal face, guiding
   the narrow tongue into the canyon above the threaded shank. The two
   tongue sides provide the nominal compression fit.
3. During unloaded setup, confirm contact on the transition and flat face,
   clearance under the bridge and above the threads, and an untouched
   attached lever. The hand face should stand 2 mm above the PET-GF walls.
4. Hold the broad face above the flat metal contact down with one hand.
   Use the other hand to alternate the factory screw handles in the small
   steps described in the [fixture procedure](../README.md#fixture-setup-and-motion).
5. Unload the axial clamps and lift out the pad before lifting the donor
   and tube from the cradle.

The pad is an unprinted fit candidate. The 1 mm excess tongue width is
an interference dimension; it does not establish insertion force,
retention force or automatic donor clamping. Physical fit and manual
hold-down performance remain unmeasured. The existing base and its
axial load path retain their geometry.

## CAD and review

[`dimensions.json`](dimensions.json) records the geometry and source
bindings. [`geometry-review.json`](geometry-review.json) records one valid
solid, zero nominal overlap with the metal donor, base interference
confined to the retention tongue, and 176 supported manufacturing
cross-sections. The
[`native readiness record`](ready/donor-hold-down-transition-tpu85a-right06-z018-mark1.readiness.json)
binds the STL, project, archive, G-code and emitted process.

The STEP files are `donor-hold-down.step` in manufacturing orientation
and `donor-hold-down-fit.step` for the cropped contact view. The slicer
mesh is [`donor-hold-down-print.stl`](donor-hold-down-print.stl).
Generate and slice explicitly from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/donor-hold-down/donor_hold_down.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/donor-hold-down/prepare_print.py --slice-output .cache/donor-hold-down-transition-native-next
```

The slice directory must be empty. These manual operations submit no
print and are not part of a build, hook or watcher.
