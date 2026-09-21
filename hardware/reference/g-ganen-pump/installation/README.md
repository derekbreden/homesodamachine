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
places its **Z = 0 bearing datum on the cap face**, and strikes its rigid rear
against the core rear. The lowest free-rubber point does not set pump height.
The native tray and flavor-union bands determine the lateral position.

For the retained cap and gate fixture, the reference-origin translation is
**(2.071135, 378.635458, 253.400000) mm**. Local +Y discharge points toward
**enclosure −X**, as Derek identifies. The independently measured suction and
discharge axes remain distinct. The suction tip is
(39.332171, 345.347023, 280.124302) mm and discharge tip is
(−34.946262, 345.376488, 280.168822) mm.

Both fitting chains seat their real hex midpoints on the existing cap anchors.
Their native bounds and V-K's native bounds match the retained fitted fixture
exactly. The rear flavor unions keep their gate storey. `pan_front_y()` uses the
placed native discharge barb/root envelope instead of a common nominal diameter.

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
- `profiled_barb_length(port)`: observed external length. Tube-export metadata
  names its use as a candidate insertion allowance; actual hose grip is unqualified.

## Native checks and assembly test

Run the bounded producer from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/reference/g-ganen-pump/installation/validate_installation.py
```

It builds the selected pump, chains and V-K; the actual cap cup and lid are built
in memory. It does not overwrite a production STEP/STL or alter a submitted print.
`native-installation-check.json` binds source/native hashes to the placed datums,
mount alignment, available rail stock, washer/straight-driver corridor, native
hose bends and overlaps, print stock, screw passage and neighboring printed lid.
The gate fixture is explicitly the retained baseline facts reading. The complete
candidate assembly must rebuild and check its own final routing and neighbors.

The M3 shank envelopes have zero overlap with the printed cup/lid. The deeper
blind bores leave **6.0857 mm of stock** above the cup underside. The largest
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

The new columns print vertically from the cup floor and their blind bores open
at the top. The top lid holes pass straight through. No new horizontal bearing
face is sloped, and no new enclosed support-removal pocket is introduced.

## Production dependency handoff

The changed printed consumers are `foam-cap-top` and `foam-cap-lid-top`. Rebuild
those, then `foam-assembly`, before the complete enclosure assembly/Box producer.
The G pump source replaces the selected pump scene identity throughout topology,
assembly cards, BOM mount count and tube-export metadata. Generated facts, checks,
viewer inventories and docs remain baseline until that coordinated regeneration.

The shared dependency trace must include the installation module, the measured
reference parameters, the conservative envelope module, its native STEP and
native-validation proof, and `native_queries.py`. This bounded checker does not
write the shared trace. Final enclosure pieces derive from the freshly checked
Box; no submitted cartridge/cap artifact is repurposed as evidence for this pump.
