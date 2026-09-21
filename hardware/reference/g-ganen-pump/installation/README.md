# Installed G Ganen candidate

The selected pump uses its four purchased sliding rubber feet, an M3 × 20 screw
at each foot, and a candidate Ø9 × 0.8 mm washer. The cap has four explicit
stations; there is no rectangular purchased hole-pattern assumption.

The front pair is selected at reference X = 12 mm and the rear pair at X = 50 mm.
Each observed rubber component translates only along X. Their complete external
axial envelopes remain within the observed fixed-rail region, and the rear pair
clears the rear flavor-union passage. The hidden clip, exact rail hard stops and
loaded rubber behavior remain physical qualification items.

`g_ganen_installation.py` consumes the separately verified conservative native
integration envelope. The frozen detailed scan reference remains separate.
Occupied envelopes, including filled foot slots and clip cavities, are not
material volumes, screw-passage evidence or a pump strength model.

## Datums and connections

`enclosure_assembly.build_water_pump()` rotates the reference +90° about Z,
places its **Z = 0 bearing datum on the cap face**, and keeps its rigid rear
8.7 mm forward of the core rear. The lowest free-rubber point does not set pump height.
The native tray and flavor-union bands determine the lateral position.

At the current core placement, the reference-origin translation is
**(2.071135, 374.235458, 253.400000) mm**. Local +Y discharge points toward
**enclosure −X**, as Derek identifies. The independently measured suction and
discharge axes remain distinct. The suction tip is
(39.332171, 340.947023, 280.124302) mm and discharge tip is
(−34.946262, 340.976488, 280.168822) mm.

Both fitting chains seat their real hex midpoints on the existing cap anchors.
Their positions and V-K follow the core. The rear flavor-A union keeps its gate
storey; flavor B is 1.55 mm below it. `pan_front_y()` preserves the pan's core-relative station with 18.7 mm
between its sleeve front and the placed native discharge barb/root envelope.
The complete westward pan withdrawal clears the pump by at least 9.1678 mm;
the sleeve's enclosing stock clears it by at least 5.9178 mm.

The four cap mounting axes are (−100.435458, 40.587882),
(−100.435458, −36.709857), (−62.435458, 41.324566), and
(−62.435458, −36.268488) mm in the cap's own XY frame. Pump placement and these
axes share `REAR_CLEARANCE`; `pump_mount_rows()` independently checks alignment.

Stable production interfaces are:

- Scene/frame key: `g-ganen-pump`.
- `suction()`, `discharge()` and `port_profile(name)`: independent measured ports.
- `bearing_datum()`, `placed_bearing_z(carry)` and
  `bearing_z_from_frame(frame)`: explicit cap-bearing datum; the frame accessor
  applies to this yaw-only installation.
- `mount_stations()` and `mount_holes()`: selected slider poses and screw axes.
- `CAP_MOUNT_XY`: authored cap axes, checked against the placed feet each build.
- `feet_shapes(carry)`, `rigid_shape()` and `discharge_shape(carry)`: independent
  occupied components for checks in their actual rooms.
- `cap_bearing_contact_parts(carry, cap_plane_z)`: the rigid pump and exactly four
  native free-foot masks at or below the independently located cap plane. A
  mismatched bearing height or tilt is rejected. Complete-pump overlaps outside
  those masks remain interference; every other neighbor sees the complete pump.
- `profiled_barb_length(port)`: observed external length. Tube-export metadata
  names its use as a candidate insertion allowance; actual hose grip is unqualified.

## Native checks and assembly test

Run the bounded producer from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/reference/g-ganen-pump/installation/validate_installation.py --skip-hoses --output hardware/reference/g-ganen-pump/installation/corrected-mount-check.json
```

It builds the selected pump, chains and V-K; the actual cap cup and lid are built
in memory. It does not overwrite a production STEP/STL or alter a submitted print.
`corrected-mount-check.json` binds source/native hashes to the placed datums,
mount alignment, available rail stock, washer/straight-driver corridor, native
print stock, screw passage and neighboring printed lid. All 45 checks pass. Hose
routing is checked separately against the complete current route set. The gate
fixture retains its Z from the facts reading; the chains' expected positions
include the independently measured core translation. The complete assembly must
read the regenerated cap and lid and check its final shell and routes.

`verify_cap_contact.py --pack <retained-pack-directory>` exercises the production
contact classifier. `cap-contact-check.json` records the actual four-foot contact,
then proves that a rigid intrusion, extra shared material outside the foot masks,
and an incorrect bearing height are rejected. The positive test uses the retained
placed foam; the separate mount check constructs the current cap/lid from source.
Neither reading predicts loaded rubber deformation.

The M3 shank envelopes have zero overlap with the printed cup/lid. The blind
bores leave **6.0857 mm of stock** above the cup underside. The largest
observed free-pad stack gives **5.7149 mm nominal screw reach** into a 5.7 mm
insert. That 0.0149 mm nominal margin is not a manufacturing tolerance or proof of
actual engagement. Washer seating, rubber compression and real screw length must
be read at assembly; an apparently tight screw must not be treated as a qualified
clamp merely because the scan-based calculation passes.

The remaining physical observations are a freely passing M3 through each complete
slot, flat washer seating clear of the rubber upstand, loaded screw engagement
and compression, and hose insertion/clamp retention. Washer and screw receipt is
not inferred from the purchase ledger. An underside foot scan is unnecessary for
this stock-foot mount unless those direct checks expose a hidden obstruction.

Assembly uses four stock feet, four washers and four screws. Slide each foot to
its corresponding cap station, place the bearing plane on the lid, pass each
screw and washer through its actual slot, then seat all four without forcing an
unobserved compression target. The casing carries load through its existing
rails and rubber feet into the broad lid and the four internal columns.

The columns print vertically from the cup floor and their blind bores open
at the top. The top lid holes pass straight through. The mounting bores have
open vertical support-removal paths and no enclosed horizontal pockets.

`corrected-placement-check.json` reads 97 native neighbors, including the current
nameplate, the pan and its complete withdrawal envelope. Its nearest queried
rigid component is the flavor-A bulkhead at **1.2651 mm**. The nameplate has a
**1.0000 mm** enclosing-box clearance. The complete regenerated shell is a
separate final assembly check.

Both pump hoses leave and enter on their measured port axes and keep **R15.9 mm**
bends. The nearby reservoir-A fill tube keeps **R14 mm** bends and its complete
cap bearing at world Y **254.4–263.2 mm**. Its local valve-side descent clears
V-A by **1.155 mm** and V-K by **1.125 mm**; its rear descent clears the suction
hose by **1.3672 mm**. The cap anchor and fill conduit keep their declared datums.
`corrected-pump-routes-check.json` contains the hose and complete-neighbor readings;
`inner-valve-route-check.json` binds the valve-side route to the current lowered
inner valves and complete native lid. The lid has zero fill-tube overlap and
**0.15 mm** intended bearing air. Those reports identify their exact retained
inputs; final regenerated routes and the complete shell remain assembly checks.

## Production dependency handoff

The printed mounting consumers are `foam-cap-top` and `foam-cap-lid-top`. Rebuild
those, then `foam-assembly` and `cold-core-assembly`, before the enclosure Box and
complete assembly. Generated facts, checks and viewer inventories must bind to
those exact regenerated inputs.

The shared dependency trace must include the installation module, the measured
reference parameters, the conservative envelope module, its native STEP and
native-validation proof, and `native_queries.py`. This bounded checker does not
write the shared trace. Final enclosure pieces derive from the freshly checked
Box; no submitted cartridge/cap artifact is repurposed as evidence for this pump.
