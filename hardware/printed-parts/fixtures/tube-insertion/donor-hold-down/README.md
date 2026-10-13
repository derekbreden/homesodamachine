# TPU donor hand hold-down pad

This one-piece TPU pad rests on the Touch-Flo's cylindrical metal body in
the existing tube-insertion base. Its flat hand face stands 2 mm above the
PET-GF reaction walls. A compression tongue parks the pad in the open
shank canyon. Downward hand pressure passes through the saddle to the
metal body.

The pad covers the first 12 mm of the cylindrical body above the threaded
shank, ending 1 mm before the column begins. The faucet lever remains
attached, down and unpressed throughout tube insertion, as recorded in
the [physical assembly observations](../../../faucet/lever-replica/assembly-observations.json).
The contact view below crops the donor at 20 mm along its axis; it does
not depict lever removal. The lever's measured installed pose is not
available, so its actual clearance remains an ordinary unloaded fit check.

![Contact zone: blue TPU pad, dark existing base and metal donor](art/fit.png)

| Feature | Nominal dimension |
| --- | ---: |
| Donor saddle diameter | 31.5 mm |
| Saddle length along donor axis | 12 mm |
| Hand face above PET-GF walls | 2 mm |
| Existing canyon width | 11.8 mm |
| Retention tongue width | 12.8 mm |
| Compression allowance | 0.5 mm per side |
| Tongue entry width | 11.3 mm |
| Thread clearance below tongue | 10.25 mm |
| Tongue engagement below wall top | 8.25 mm |
| Full-width compression engagement | 7.5 mm |
| Clearance above lower cradle | 1 mm |
| Minimum crown backing | 10.25 mm |
| Minimum side backing | 3.25 mm |
| Print bounding box | 37.5 × 38 × 25 mm |

## Print

Print one in black TPU 85A with the broad flat hand face on the bed and
the concave saddle opening upward. That face gives 782.4 mm² of bed
contact. Successive cross-sections shrink as the channel opens, so the
part needs no supports in this orientation.

![Manufacturing pose: flat hand face on the bed, concave saddle up](art/print-pose.png)

The editable native project is
[`ready/donor-hold-down-tpu85a-right06-z018-mark1.3mf`](ready/donor-hold-down-tpu85a-right06-z018-mark1.3mf).
The reviewed print archive is
[`ready/donor-hold-down-tpu85a-right06-z018-mark1.gcode.3mf`](ready/donor-hold-down-tpu85a-right06-z018-mark1.gcode.3mf).
Both use Mark1's right fixed 0.6 mm nozzle, external black TPU 85A spool
255, textured PEI, 0.18 mm layers, a 0.30 mm first layer and 100% zig-zag
infill. The user Z trim is Mark1's standard +0.18 mm; the emitted plate
compensation is `G29.1 Z0.16` after the reset to zero.

The native slice has 138 layers, no generated supports, at least 133.4 mm
full-bead bed-edge clearance and no slicer warning. Estimated use is
12.8 g and 1 hour 36 minutes. These files are prepared offline; no pad
print has been submitted.

## Fit and use

1. Leave the faucet lever attached, down and unpressed. Seat the donor in
   its existing cradle with its metal base annulus against the reaction wall.
2. Lower the pad over the cylindrical body and guide its narrow tongue
   into the canyon above the threaded shank. The two tongue sides provide
   the nominal compression fit.
3. During unloaded setup, confirm that the curved saddle contacts the
   donor, the tongue clears the threads, the sides clear the lower cradle
   and the attached lever remains untouched. The hand face should stand
   2 mm above the PET-GF walls.
4. Hold the broad face above the cylindrical body down with one hand.
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
confined to the retention tongue, and 251 supported manufacturing
cross-sections. The
[`native readiness record`](ready/donor-hold-down-tpu85a-right06-z018-mark1.readiness.json)
binds the STL, project, archive, G-code and emitted process.

The STEP files are `donor-hold-down.step` in manufacturing orientation
and `donor-hold-down-fit.step` for the cropped contact view. The slicer
mesh is [`donor-hold-down-print.stl`](donor-hold-down-print.stl).
Generate and slice explicitly from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/donor-hold-down/donor_hold_down.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/donor-hold-down/prepare_print.py --slice-output .cache/donor-hold-down-native-next
```

The slice directory must be empty. These manual operations submit no
print and are not part of a build, hook or watcher.
