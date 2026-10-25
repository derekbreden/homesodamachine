# Integral pump mount: native assembly reading

The upper fitted pump pockets belong to `enclosure-front-top`, in one broad body
continuous into the display housing and roof. The plain rectangular
`enclosure-pump-retainer` carries both pumps for motor-first insertion from the
open underside. Three M3 × 60 screws close the skirt capture from below. The four
prepared tubes rise through bottom-open tee-wall gates. Pump and display leads
share the rear exit at X0/Z280.

[`native-review.json`](native-review.json) records explicit native geometry
queries. [`print-review.json`](print-review.json) records the identified native
slices. These are manual reviews, with no build, hook or scorecard integration.

The current parts are front-top STEP `38930496…` and retainer STEP `bd394956…`.
The original complete path receipts bind front-top `455cd05a…` and retainer
`ea79019f…`; the report preserves those actual input hashes. Its
`printed_stock_refinements` records bind the current parts separately. The
retainer removes only the upper fore-corner films, preserving its lower land
and screw columns. Front-top `d65c9d61…` has direct complete added-stock motion
queries against the retained native hardware. The current front-top is its
native material subset; removed stock cannot introduce a rigid collision.
All nine front-top modifier boxes and both complete valve tray/post/bearing
envelopes remain unchanged. The nearest fore-valve envelope is 5.55 mm below
the removed stock. The intermediate `e0b491ba…` review retains its own scope
and is not used as a subset inference for `d65c9d61…`.

| Recorded interaction | Native result |
|---|---|
| Prepared pump/retainer unit, 130 mm motor-first loading | Complete path; minimum gap 0.25 mm |
| Declared pump-port casing probes, same loading | Complete path; minimum gap 5.351 mm |
| Four prepared tee/link/fore-valve groups, 11.65 mm axial approach | Every path complete; intended post and bearing mates separated explicitly |
| All 16 valve-post swept cylinders | Zero fixed-stock overlap |
| Three underside driver columns, Ø3.5 × 70 mm | Zero overlap |
| Changed pump mount, 97.664 mm front-column closing slide | Complete path; minimum gap 5.195 mm |
| Installed display and funnel-frame neighbors | Zero overlap with the revised printed parts |
| Pump unit at nominal and +0.40 mm height | Zero rigid overlap; minimum screw-pilot tip reserve 0.60 mm |

The 11.65 mm group approach exceeds the measured branch's 11.50 mm extended
insertion. All four groups install before the rear valve row. Their transverse
envelopes remain at least 11.20 mm apart, so sequential installation does not
create an inter-group collision. Both east WAGO wells retain their own pocket
and backing at a common broad fore plane, Y166.10. The yoke's furthest aft
position in the conservative approach is Y165.04, leaving 1.06 mm to that plane.

The added front-top stock clears the complete 130 mm pump-loading path by at
least 5.278 mm and the 11.65 mm fore-group path by at least 4.540 mm. It also
clears the declared casing loading, front-column slide, driver columns,
nominal/+0.40 mm takeup, display and funnel frame. The fixed bearing and screw
stock through Z236.074 is unchanged. The shared passage has a 22 mm diamond
section forward and a rear upper-half U breakout over the bulkhead lip;
the terminal rooms close at 36° into continuous stock below the display seat.
Wire and Faston clearance retain their separate native review and physical
fit limits.

Run the geometry reading after exporting the named parts and appliance:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/pump-mount-review/review.py
```

`--query front-plumbing` limits the reading to prepared fore-group installation,
the screw-closing allowance and the display/funnel neighbors. `--query static`
omits motion queries. The first native assembly read saves the selected named
BReps under `.cache/pump-mount-review/<assembly-sha256>/` before running a query.
The report binds their original assembly hash, cache index and individual body
hashes. Subsequent readings reuse that exact native subset while its source
assembly hash remains the same.
`--hardware-cache-sha256 <original-aggregate-hash>` explicitly reuses a retained
subset after the aggregate path is replaced. It records the cache inputs read
and keeps the original aggregate identity in the hardware provenance.

When a final producer emits the same named hardware as a small native subset,
`verify_hardware.py <reading.json> <final-subset.step> --out <report.json>`
compares every body by native serialization or two-way native Boolean difference.
Its agreement record preserves the original path-query inputs and binds the
final subset separately.
`refine_review.py --old-directory <saved-native-parts> --stage all` appends an
old/new native stock comparison and the required added-stock motion queries.
It keeps the original path-query identities and checks the lower skirt land
and screw-column stock separately.
`verify_successor.py <saved-predecessor.step>` compares a subsequent front-top
to its recorded predecessor. Any added material triggers direct complete
stock-path queries against the original native baseline.
`verify_rear_breakout.py <saved-predecessor.step>` binds a removal-only rear
breakout and checks every existing front-top modifier box plus the valve
tray/post/bearing envelopes and pump guards.

A complete translation is bounded by native minimum-distance intervals. Each
proved interval is shorter than the current solid-to-solid gap, after a
0.00001 mm retreat. A zero gap stops that bound. The valve posts receive a
separate complete swept-cylinder query because their nominal socket fit has no
radial gap; every other native body surface remains in the distance query.
At the valve's bearing plane, the body and fixed stock are partitioned into
fore and aft material. Body material at or aft of that plane cannot meet
fore-side stock before home. Its terminal bearing faces may touch at home.
The port barrel extends below the bearing plane and receives its own complete
path query against the whole quadrant.
For each valve, the fixed-solid query uses its complete swept bounding box
expanded by 2 mm. Material outside that box has at least 2 mm of separation
throughout the translation; each interval uses the lesser of that bound and the
native gap inside the box. The report stores these domains and bounds.
The coaxial pump-stub/tee joint is a declared mate. Its nominal bore does not
model gripping teeth or the O-ring. Recorded transverse envelopes separate each
group from the other groups and nonmating stubs. Actual tube insertion marks
and joint checks remain part of the bench procedure.

The factory order is: prepare pumps, tubes and wiring on the loose retainer;
raise and secure that unit in loose front-top; fit all four prepared tee,
upper-tube and fore-valve groups straight from aft; fit the rear valve row and
lower returns; finish the accessible wiring and display; join the front column.
The funnel frame enters after the central connections. See
[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3 for the
bench procedure.

The fixed skirt face has 0.40 mm of supported-face allowance. The retainer's
nonbearing top starts 0.65 mm below that face. The report queries nominal and
+0.40 mm unit heights and records the remaining screw-pilot tip reserve. These
are closing and printed-face allowances; they do not establish measured axial
play after tightening. Tube-tip Y depth is unchanged by that Z-only motion;
nominal tube-axis height is not a physical insertion measurement.

These readings cover the declared rigid geometry. They do not qualify connector
boots, hands, flexible wire or tube handling, printed assembly force, screw
preload, operating retention or lifetime. The earlier firm-holding/no-play
observation remains evidence for its identified separate cradle and cap. It
does not qualify this upper/lower skirt capture. The
[physical evidence index](/hardware/mechanical-qualification/README.md) retains
that scope.
