# Integral pump mount: native assembly reading

These receipts bind the identified three-screw pump-mount articles listed below. The
current snap-wing retainer and receivers are described in the
[pump-snap review](../pump-snap-review/README.md); the receipts here do not qualify that
interface or its print preparation.

The upper fitted pump pockets belong to `enclosure-front-top`, in one broad body
continuous into the display housing and roof. The plain rectangular
`enclosure-pump-retainer` carries both pumps for motor-first insertion from the
open underside. Three M3 × 60 screws close the skirt capture from below. The four
prepared tubes rise through bottom-open tee-wall gates. Pump and display leads
share the rear exit at X0/Z280.

[`native-review.json`](native-review.json) records explicit native geometry
queries. [`print-review.json`](print-review.json) records the identified native
slices. These are manual reviews, with no build, hook or scorecard integration.

The parts bound by these receipts are front-top STEP `6120cf94…` and retainer STEP `bd394956…`.
The original complete path receipts bind front-top `455cd05a…` and retainer
`ea79019f…`; the report preserves those actual input hashes. Its
`printed_stock_refinements` records bind those parts separately. The
retainer removes only the upper fore-corner films, preserving its lower land
and screw columns. Complete added-stock motion queries identify front-top
`08cc2019…`. The cleanout receipt identifies `481f83f6…` → `c9fdbec4…`, removing
7,570.865 mm³ with zero added material. The separately bound M5 extensions
identify `c9fdbec4…` → `7e676118…` and `7e676118…` → `6120cf94…`. The latter
adds 83.232 mm³, removes no material and lies at Y212.7–217.8 within the
declared Y197–218 joint band. All eleven bound modifier boxes are identified. Four
Y-seam hosts retain their exact-input M5 review; the other seven boxes, both
complete valve tray/post/bearing envelopes and the fixed pump bearing/screw
region retain their native material. The 3 mm backing below the glass seat,
accepted wing/lip stock and clear cleanout apertures are unchanged. The earlier
receipts retain their identified inputs and scope.

The [M5-joint review](../y-seam-100-review.json) identifies the landed native
quadrants. The latest top addition is separated from the complete
pump-loading, casing, prepared fore-group, driver and closing-allowance
domains; its smallest swept-domain bound is 69.951 mm at the fore groups.
Its complete front-column slide clears the bound lower assembly by at least
159.40 mm; installed display and funnel-frame queries have zero overlap.
Preceding additions retain their own recorded native queries and bounds.
The bound front-bottom `f856ca97…` removes 8,626.797 mm³
from the original cached body and adds no material. These native comparisons
extend the original rigid-path scope without treating the changed quadrants
as unchanged hardware. The report binds the joint review's exact hash.

The final named-body agreement comes from a small STEP subtree extracted
directly from the frozen full-appliance export `8f7ed840…`, without importing
the complete appliance into CAD. Its original geometry and ancestor placement
records are retained. All 32 other cached hardware bodies agree natively;
front-bottom agrees with its identified `f856ca97…` part. The
[`extraction receipt`](final-native-extraction.json) binds the actual full
export and subset hashes. The full-appliance viewer names that same export,
and the installation GLB bound by these receipts includes all three retainer screws and inserts at
X−92/0/+92, Y45.859. The earlier 33-body agreement retains its original inputs.

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
The cross passage ends at the motor axes, with a level Z274.224 floor and a
45° roof. The display entry, link and chimney occupy one straight-sided
corridor. The display wings retain their complete canonical 12 mm exits,
17.223 mm from the pump inverse and 22.254 mm from the cross passage.
The complete canonical display cutter has zero native overlap with front-top.
Two plain side cleanouts connect the wing exits to the empty PCB room, each
with a 69.3 × 4.96 mm nominal clear aperture. Their roofs retain 3 mm below
the glass seat. They remain at least 13.84 mm from the pump inverse and
8.84 mm from the outer silhouette. Clear supports through the empty display
and PCB opening before installing the pumps and screen; physical support
removal remains unqualified.
Wire and Faston clearance retain their separate native review and physical
fit limits.

## Purpose and bearing review

The [independent intent reading](design-intent-reading.json) binds front-top
`6120cf94…`, retainer `bd394956…` and back-top `4058c568…`. Within the declared
filled upper-mount stock, subtracting the pump, tube, wire and display cutters
accounts for the missing material; no further disconnected void remains in that
region. This scope does not cover every cavity in the enclosure.

Both pump heads have about 534 mm² of nominal planar lower contact and
2,163 mm² of upper contact after 0.40 mm closing take-up. At that height the
retainer's non-bearing body remains 0.25 mm below the fixed mount. These native
contacts establish the intended skirt capture, not printed preload or holding
capacity.

The two forward flank recesses have no mating feature on the bound three-screw
retainer. Each is 6 mm deep and 56.515 mm long; the retainer stops 6.25 mm from
its back wall. The snap-wing retainer is outside these identified
STEP/STL inputs. The existing aft Z-joining rails are separate.

The Y-seam passages are Ø5.6 mm around the nominal Ø5 mm outside-thread
envelope. Their 0.6 mm nominal diametral air does not establish close lateral
support or an absence of rattle. The final printed bearing fit remains a design
decision. The installed appliance model includes all four M5 × 100 screws and
four RX-M5x9.5 inserts; the screw bodies show thread envelopes, not smooth shanks
or detailed helical contact.

## Receipt workflow

The commands below belong to the bound three-screw reading and do not qualify the snap
interface. Its geometry reading uses the named part and appliance exports:

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
`--front-bottom-reference <current-front-bottom.step>` compares the other 32
bodies with their original cache inputs and front-bottom with its separately
identified current native part. It appends a current agreement while retaining
the earlier subset receipt and the old/new front-bottom stock comparison.
`refine_review.py --old-directory <saved-native-parts> --stage all` appends an
old/new native stock comparison and the required added-stock motion queries.
It keeps the original path-query identities and checks the lower skirt land
and screw-column stock separately.
`verify_successor.py <saved-predecessor.step>` compares a subsequent front-top
to its recorded predecessor. Any added material triggers direct complete
stock-path queries against the original native baseline. Its optional
`--delta-directory <directory>` retains native added/removed bodies and their
exact input hashes for a separate manual reading.
`verify_rear_breakout.py <saved-predecessor.step>` binds a removal-only rear
breakout and checks every existing front-top modifier box plus the valve
tray/post/bearing envelopes and pump guards.
`verify_passage_stock.py <saved-predecessor.step>` compares both added and
removed stock with those mounting regions and checks the canonical display
pocket and wing-exit separation. `--regions <print-regions.json>` identifies
the exact modifier specification read; `--cleanouts` adds the native aperture,
glass-backing and retained upper-fit stock queries.
`--joint-review <review.json> --joint-band-y 197 218` identifies intentional
changes within the current M5 joint band while preserving the separate
nonjoint mounting-stock and display-fit comparisons.
`verify_main_joint_rebase.py` binds the landed joint review, compares its
top/front-bottom native material with the original path inputs, and checks
the complete swept domains affected by those additions.
`extract_native_subset.py <aggregate.step> <cache-index.json> --out <subset.step>
--report <receipt.json>` retains selected AP214 geometry and ancestor placement
records for the final named-body comparison. `verify_export_lineage.py` checks
viewer source headers and the six shown retainer-hardware stations using only
the frozen export metadata.

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
