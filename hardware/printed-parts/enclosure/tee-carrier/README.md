# Tee carrier

One moving PET-GF carrier behind the four pump-barb tees, with two separately installed service
tabs and two top-drop tab locks. The fixed tee wall journals each tee's branch collar in X and
Z; the carrier couples the four tees in Y. The fore and aft valve trays, both valve rows, the
collet plate, and the pump cartridge remain fixed.

## Frame and motion

Every builder returns installed geometry in the enclosure assembly frame. +Y is aft and is the
only operating motion; +Z is the print and top-entry axis. The squeeze datum bottoms all four
cartridge tubes in their tee ports.

| state | carrier Y offset | stop/contact |
|---|---:|---|
| full release | -3.15 mm | fore stop; 1.5 mm rest gap plus 1.65 mm sleeve stroke |
| squeeze / tube bottom | 0 mm | held by the two service tabs |
| connected / first grip | +1.50 mm | floating under spring load |
| parked / first resistance | +3.00 mm | aft stop |

The offsets come from the measured PP0208E depths in `tee_connector.py`. The complete guide
span is 6.15 mm. `interface()` exposes every state, stop face, part envelope, and installation
path.

## Lowerable carrier

The web spans X -94..+94, Y 109.718..112.218, and Z 171.245..209.245 mm at squeeze: 188 × 2.5
× 38 mm. Its guide ears span X ±94..±98.35, use the web's exact Y section, and occupy Z
184.245..196.245 between the two tie paths. The carrier therefore leaves 0.15 mm radial slip in
the front-top cavity at X ±98.5 in every feature stage.

The fixed guide pockets are open at the top. Their side faces guide X, and their fore and aft
faces stop Y. At the parked +3 mm state, the web's aft face is Y 115.218, leaving 1.742 mm to the
aft valve coils' fore envelope at Y 116.960.

Only the 1 mm zip-tie strap passes behind the web, in a 1.2 mm-deep channel. No tie head is
permitted behind the carrier.

## Tee ties

Each tee gets two black 4-inch, 18-pound nylon zip ties, one around each straight run arm: eight
ties total. Their bands are at Z 178.245 and 202.245 mm, 12 mm either side of the tee's Z
190.245 centre.

Each tie passes through two 1.5 × 3.5 mm slots at `tee_x ± 8.5 mm`, crosses the aft recess,
returns around the tee arm on the fore side, and closes with its head clocked away from X=0.
The outer heads reach |X| 89.478 and remain clear of the service tongues beginning at |X| 94.15.
Flush-cut every tail.

The tee-wall branch journals remain the precision guide. The ties close the tees against the
flat bearing web and make their Y motion common; the carrier carries no second set of close-fit
tee saddles.

## Springs

The spring axes are X ±49.945, Z 190.245 mm, in the gaps between the aft valve coils. Each seat
is a 6.4 mm-wide tangent teardrop, 2 mm deep in a 12.4 mm spring rail. The 5 mm rail carries its
semicircular crown to the web's bed edge, and its roof rises at 45 degrees.

The seat accepts the 5.99 mm OD dimensional candidate. Spring rate and free length remain bench
inputs from the complete four-stub, four-hairpin, eight-tie mechanism.

## Separate service tabs

The two handed tab parts are short transverse pieces in the carrier's own Y band. Each service
pad occupies only the flank thickness: at squeeze it spans |X| 98.65..107.2, Y 109.718..112.218,
and Z 197..209 mm. It is recessed 0.3 mm from the exterior and has 0.15 mm running clearance to
the front-top's X 98.5 inner flank. Across the named states, the pad sweeps Y 106.568..115.218.

The carrier owns the female half of each joint. Its block grows directly from the web and the
guide ear, and its triangular socket opens toward the exterior. The tab owns the matching male
tongue:

| feature | positive-X installed envelope | mirrored at -X |
|---|---|---|
| carrier receiver | X 93.5..98.35, Y 109.718..112.218, Z 196.245..209.245 | yes |
| female socket | X 94..98.5, Y 110.168..111.768, Z 202.55..207.35 | yes |
| male tongue | X 94.15..98.65, Y 110.318..111.618, Z 202.7..207.2 | yes |
| exterior pad | X 98.65..107.2, Y 109.718..112.218, Z 197..209 | yes |

The tongue has 0.15 mm slip inside the socket. Its lower face rises 4.5 mm over its 4.5 mm
inboard reach, so it prints from the pad at 45 degrees without support. The receiver remains
inside the carrier's |X| 98.35 lowering envelope in every feature stage.

## Top-drop tab locks

One rigid PET-GF key prevents each tongue from withdrawing from its socket. The key centre is
X ±97.5, Y 110.968. Its 1.2 × 1 mm shaft spans Z 204.8..207.5; its 2 × 2 × 0.7 mm head spans
Z 207.3..208.0. A 0.15 mm-clearance bore passes through the receiver and male tongue.

The key starts with its bottom at Z 209.395, 0.15 mm above the receiver. Its 4.595 mm drop seats
it at Z 204.8; its entry top is Z 212.595, leaving 1.608 mm beneath the service opening's
Z 214.203 gable. The joint uses no PET-GF deflection during installation.

## Assembly path

1. Lower the carrier, without service tabs, through the X ±98.5 front-top cavity and into its
   open-top guide pockets.
2. Hold the carrier at squeeze. Start each tab outside its flank at final Y and Z: the right
   part spans X 107.65..120.7 and the left spans X -120.7..-107.65. Each begins with 0.15 mm
   clearance beyond the X ±107.5 exterior wall.
3. Slide the tab 13.5 mm inward through its flank slot. The male tongue enters the carrier's
   outboard-open socket while the exterior pad stops at its recessed X ±107.2 face.
4. Drop the handed tab lock 4.595 mm through the aligned top-entry bore.

The required flank opening is X 98.35..108.5 on the right and mirrored on the left, Y
106.418..115.368 across the complete operating sweep, and Z 196.85..209.15 beneath the gable.
It cuts only flank stock; it does not extend into the tee-journal band. The selftest samples the
complete inward entry against a representative wall with exactly that opening, the lock drop,
and all four locked operating states.

## Feature stages

`build_carrier(spec, features)` keeps the machine steps independently generatable without
changing a datum:

| feature set | web, ties, guide ears | spring rails and seats | separate-tab receivers |
|---|---|---|---|
| `STEP4_FEATURES` | yes | no | no |
| `STEP5_FEATURES` | yes | yes | no |
| `STEP6_FEATURES` | yes | yes | yes |

`DEFAULT_FEATURES` is `STEP6_FEATURES`. Service tabs and tab locks are always separate parts,
including Step 6, so every carrier stage remains lowerable.

## Print

Print all five pieces upright in their assembly orientation, translated onto the bed. The
complete Step 6 carrier occupies 196.7 × 5 mm on the H2C's 325 × 320 mm bed and stands 38 mm
high. Each tab occupies 13.05 × 2.5 mm and stands 12 mm high. Each tab lock is 2 × 2 × 3.2
mm; print spares with a brim.

The spring rails and female receivers are bed-rooted. Each male tongue grows from its pad on a
45-degree lower face, and the receiver socket's 1.6 mm roof is a short bridge open to the
outboard face, so no support is trapped in a joint.

## Source, builders, and artifacts

- `build_carrier()` / `build()` — the one-body moving carrier for the selected feature stage
- `build_service_tab(side=-1|1)` / `build_tab()` — one installed handed pad and male tongue
- `build_tab_lock(side=-1|1)` / `build_lock_key()` — one installed handed top-drop tab lock
- `tab_joint_sites()` — receiver, socket, tongue, lock, and outboard-entry datums
- `interface()` — states, stops, service sweeps, installation path, and printed-part names
- `enclosure-tee-carrier.step` / `.stl` — complete Step 6 carrier
- `enclosure-tee-carrier-tab-left.step` / `.stl` — left service tab
- `enclosure-tee-carrier-tab-right.step` / `.stl` — right service tab
- `enclosure-tee-carrier-tab-lock-left.step` / `.stl` — left tab lock
- `enclosure-tee-carrier-tab-lock-right.step` / `.stl` — right tab lock

Run:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py selftest
```
