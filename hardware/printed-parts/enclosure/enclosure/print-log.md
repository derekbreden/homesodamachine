# enclosure print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in `.3mf`
snapshots retained only in Git history. The explicit `git:<revision>:<path>` references below
are evidence for these printed plates, not current slicer deliverables.

Geometry: the six-piece box from
[`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) — four quadrants,
the lower pump cradle and its top clamp, one piece per plate — sizes in
[README.md](README.md), which the generator writes.

## The PETG exterior profile (settings per history-only `git:aef8f43c0eb3eef9c6525ecaa0a1ca52c5b8c71a:hardware/printed-parts/enclosure/enclosure/enclosure-front-top-0.4mm-16hours.3mf`)

The geometry every exterior piece is cut to, sliced in PETG — the four quadrants, the pump
lower pump cradle, and its top clamp. The front-top, the largest of them, takes **16
hours** on it. That figure is the slice's own, carried in the file's name; the archive holds
no g-code to read it back off, and it is the one measured print rate
[machine-time.md](/hardware/ledger/machine-time.md) §1 stands the exterior on. The stock the
pieces ship in is the section below. Against the front-top's geometry mass in [bom.md](/hardware/ledger/bom.md)
§7, it is the hours-per-kg [machine-time.md](/hardware/ledger/machine-time.md) §1 prices
the whole exterior at.

Settings:
- Printer: Bambu Lab H2C, 0.4 mm nozzle, **High Flow** hotend on the left extruder;
  printer profile `Bambu Lab H2C 0.4 nozzle`, print profile `0.24mm Standard @BBL H2C`
- Filament `Bambu PETG Basic @BBL H2C 0.4 nozzle`, textured PEI plate
- `layer_height` 0.24 mm (initial 0.2)
- Line widths: outer wall **0.42 mm**, inner wall 0.45, top surface 0.45, sparse infill
  0.45, internal solid infill 0.42, initial layer 0.5, support 0.42
- `wall_loops` 2, `wall_generator` classic — **0.87 mm of shell per face** (0.42 + 0.45),
  so the box's 3 mm wall is four loops totalling 1.74 mm with 1.26 mm of fill between them
- top/bottom shells 4/3; `sparse_infill_density` 15 % grid
- `nozzle_temperature` 250 °C (initial 245); `hot_plate_temp` / `textured_plate_temp`
  70 °C; `chamber_temperatures` 0 (passive)
- `filament_flow_ratio` 0.97; `filament_max_volumetric_speed` **21 mm³/s** — the High Flow
  variant's cap, and what sets the wall speed the profile actually reaches
- `filament_retraction_length` 0.4 mm
- Fan min/max 20 / 30 %, overhang 50 %, `close_fan_the_first_x_layers` 3
- `outer_wall_speed` 200, `inner_wall_speed` 300, `travel_speed` 1000 mm/s
- Supports tree(auto), `support_threshold_angle` 35°, top/bottom Z distance 0.2 mm, XY
  0.35 mm
- `brim_type` auto_brim, `brim_width` 5 mm; `elefant_foot_compensation` 0.15 mm;
  `seam_position` aligned; `fuzzy_skin` none
- Slicer 02.08.02.60; first-layer time 1153 s

The model sits on the plate at scale 1.0 and identity rotation, so the piece stands in the
box's own frame with +Z up — the orientation [README.md](README.md) "Print orientation +
corner relief" strikes every 45° relief on.

## The PET-GF15 exterior (settings per history-only `git:aef8f43c0eb3eef9c6525ecaa0a1ca52c5b8c71a:hardware/printed-parts/enclosure/enclosure/enclosure-front-top-petgf.3mf`)

What the first PET-GF15 front-top printed on: Polymaker Fiberon PET-GF15 on the Bambu 0.4 mm tungsten
carbide hotend, left side ([tools.md](/hardware/ledger/tools.md), [bom.md
§7](/hardware/ledger/bom.md)).

Derek, ~6 h into the front-top: *"working a treat so far"* — and on the wall it came off with,
*"very beautiful wall surface."*

**Filament path.** The 3 kg PET-GF15 spool feeds from a Polymaker PolyDryer Box XL, not
from the SUNLU E2. A 3 kg spool turns too stiffly in the E2's chamber to feed a print;
the box carries it on a centre axle and it turns freely
([tools.md](/hardware/ledger/tools.md) "What dries where").

Settings:
- Printer: Bambu Lab H2C, **0.4 mm nozzle**; printer profile `Bambu Lab H2C 0.4 nozzle`,
  print profile `0.20mm Standard @BBL H2C`
- Filament preset `Polymaker PET-GF @BBL H2C`, one slot, textured PEI plate
- `layer_height` 0.2 mm (initial 0.2); `line_width` 0.42 mm, inner wall 0.45
- `wall_loops` 2; top/bottom shells **5**/3; `sparse_infill_density` 15 % grid
- `nozzle_temperature` **290 °C** (initial 290); `hot_plate_temp` / `textured_plate_temp`
  100 °C; `chamber_temperatures` 50 °C
- `filament_flow_ratio` 0.9555; `filament_max_volumetric_speed` **18 mm³/s**
- Fan **off** — min/max/overhang all 0 %
- `support_threshold_angle` 30°; `brim_type` auto_brim, `brim_width` 5 mm;
  `seam_position` aligned, `filament_scarf_seam_type` none
- `filament_retraction_length` nil

### What the PET-GF15 slice asks for

Wall count, infill, support style, brim and seam are the PETG exterior profile's above; top
shells are 5 against 4 and `support_threshold_angle` is 30° against 35°. What the filament
moves, read off the two history snapshots:

| | PETG (`Bambu PETG Basic`) | PET-GF15 (`Polymaker PET-GF`) |
|---|---|---|
| Nozzle | 250 °C (initial 245) | **290 °C** (initial 290) |
| Bed, textured | 70 °C | **100 °C** |
| Chamber | 0 (passive) | **50 °C** |
| Fan min / max / overhang | 20 / 30 / 50 % | **0 / 0 / 0 %** |
| Max volumetric speed | 21 mm³/s | **18 mm³/s** |
| Flow ratio | 0.97 | **0.9555** |
| Retraction length | 0.4 mm | **nil** |
| Layer / outer wall | 0.24 / 0.42 mm | **0.20** / 0.42 mm |

The volumetric cap is the row that costs time. It and the stock's density are what
[machine-time.md](/hardware/ledger/machine-time.md) §1 carries the measured PETG rate across
on: a nozzle lays grams at (cap × density), so 18 mm³/s of 1.43 g/cm³ stock is 9.5 h/kg
against PETG's 9.1.

### Three things the slot carries from the PET-CF preset it was cloned from

- **No PET-GF-specific flow calibration.** `enable_pressure_advance` is 0 with a dormant
  inherited `pressure_advance` of 0.02, so the slicer injects no PA and the run depends on
  whatever K the printer associates with the filament at send time. This is the same
  arrangement that produced the seam-clustered under-extrusion on PET-CF
  ([faucet-shell/print-log.md](/hardware/printed-parts/faucet/faucet-shell/print-log.md)
  attempt 18), where a measured K of 0.013 replaced the 0.02.
- **`filament_type` reads `PET-CF`**, `filament_vendor` reads `Bambu Lab`, and
  `filament_ids` reads `GFT01` — Bambu PET-CF's id. The slot is named `Polymaker PET-GF`;
  the type the slicer reasons about is PET-CF.
- **`filament_density` reads 1.29 and `filament_cost` 44.99**, which are Bambu PET-CF's
  figures. PET-GF15 is 1.43 g/cm³ at $25.02/kg ([bom.md §7](/hardware/ledger/bom.md)), so
  the grams and the dollars Bambu Studio prints for these plates are its own, not this
  spool's.

Polymaker publishes a `Fiberon PET-GF15 @BBL H2C` preset of their own — filament id PMPE08,
`filament_density` 1.43, `required_nozzle_HRC` 40, `compatible_printers` `Bambu Lab H2C 0.4
nozzle`, and 310 °C / bed 70 / chamber 0 / 8 mm³/s / fan 0-10-40. The slot on this machine is
the cloned one, at the settings above.

### What the front-top plate measures

The front-top sliced on the PET-GF slot at `0.24mm Standard @BBL H2C` — the 0.24 layer of the
PETG profile above rather than this section's 0.20, top/bottom shells 4/3, everything else as
listed — with tree supports and a 5 mm auto brim:

**213.06 m / 20 h 23 m, 813 layers to 195.08 mm.**

Metres, not grams, is the figure to carry. The slot's `filament_density` is 1.29 (above), so
the 661.09 g Bambu Studio prints for this plate is PET-CF's number and not this spool's:
213.06 m of 1.75 mm filament is **512.5 cm³**, which at PET-GF15's 1.43 g/cm³ is **733 g**.

Two ledgers stand on it. [bom.md §7](/hardware/ledger/bom.md) bills the piece at 456 cm³ —
shell plus 15 % grid off the solid's own volume and area
([`_bom_masses.py`](/hardware/scripts/_bom_masses.py) `PROFILES`) — and the 56 cm³ between
that and the plate is the supports and the brim, which §7 does not bill.
[machine-time.md](/hardware/ledger/machine-time.md) §1 carries the 20 h 23 m against §7's
0.653 kg as the exterior's measured **31.2 h/kg**, so the supports are back in the hours even
though they are out of the mass.

## The back-top plate (settings per history-only `git:366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf`)

The back-top on the same Polymaker Fiberon PET-GF15 stock as the section above, sliced on the
faucet's profile rather than the exterior's: `0.24mm PET-GF faucet`, 265 °C with the fan on
over a 70 °C plate. One object on plate 1 at scale 1.0, turned a half turn about X, so the piece
stands on its ceiling's outer face with the box's −Z up (`enclosure.print_up`). That
show face is the first layer, on the textured plate, and the profile's 5 mm auto brim
and 0.15 mm elephant-foot compensation act on its edge: the brim comes off that edge after
the print, and the face carries the plate's texture.

Derek, a few hours in: *"it looks great so far."* Off the plate: *"that turned out
beautiful."*

Those two remarks are about the mouth-down plate this section carried when it was printed. The
ceiling-down plate in this project was not sent; the ceiling-down back-top that printed on H2C
from 2026-09-22 is its own entry below. Its first layer is the ceiling's whole show face,
about 215 × 252 mm with a 934 mm outer loop, and the project carries this section's own 265 °C /
70 °C / +0.02 mm first layer. [z-trim.md](/hardware/printed-parts/z-trim.md) records the PET-GF
working profile's first layer at 280 °C and +0.17 mm after two long-loop first layers failed at
265 °C; `petgf.3mf` itself holds a 265 °C first layer on its `04 first layer by agent` preset. The
project also keeps its 2 wall loops and 15 % grid infill through the new 12 mm slab; what the
plate is sliced with is a decision made at the printer, not here.

Settings:
- Printer: Bambu Lab H2C, **0.4 mm nozzle**, `required_nozzle_HRC` 40; printer profile
  `Bambu Lab H2C 0.4 nozzle`, print profile **`0.24mm PET-GF faucet`**
- Filament preset `Polymaker PET-GF @BBL H2C`, one slot, textured PEI plate
- `layer_height` **0.24 mm** (initial 0.2); `line_width` 0.42 mm
- `wall_loops` 2, `wall_generator` classic; top/bottom shells **4**/3;
  `sparse_infill_density` 15 % grid
- `nozzle_temperature` **265 °C** (initial 265), `nozzle_temperature_range_high` 300
- `hot_plate_temp` / `textured_plate_temp` **70 °C**; `chamber_temperatures` 50 °C
- Fan min/max **20 / 60 %**, overhang 60 % at a 0 % threshold,
  `close_fan_the_first_x_layers` 3
- `filament_flow_ratio` 0.9555; `filament_max_volumetric_speed` 18 mm³/s;
  `filament_retraction_length` nil
- Supports tree(auto), `support_threshold_angle` **35°**
- `brim_type` auto_brim, `brim_width` 5 mm; `elefant_foot_compensation` 0.15 mm;
  `seam_position` aligned; `fuzzy_skin` none
- Slicer 02.08.02.61. The project's plate metadata carries the first-layer time of a mouth-down
  slice, not a reading of this plate.

### Support-removal audit

The current fluted back-top STL, substituted into a temporary copy of the ceiling-down production
project above and sliced by BambuStudio 02.08.02.61, has **12 connected support bodies** reaching
**35 interface islands**: 5 start on the plate around the bedded piece — fore of
its mouth, behind its rear face, through the funnel's opening — and
7 on the piece itself, the ceiling slab's interior face and the backing over each rib's tie channel. Their shortest
base-to-first-interface build-up is **1.20 mm**; 5 bodies are under 5 mm, the stubs inside the five ribs' 3 mm tie channels under their 3.5 mm crown strips, 0 in 5–10, 1 in 10–15 and 6 at 15 or more. The hashed toolpath reading is
[`enclosure-back-top.support-audit.json`](enclosure-back-top.support-audit.json). The reading is this project's: tree(auto) supports at a 35° threshold, 0.4 mm top and bottom Z
distances, 0.6 mm from the object in XY and two interface layers, all carried in the reading's
 `slicer_settings`; a plate sliced with other support settings is audited again against that project.

The snapshot carries the **+0.02 mm first-layer z-trim**
([z-trim.md](/hardware/printed-parts/z-trim.md)) — `G29.1 Z{0.0}` on this plate and nozzle
against Bambu's stock `Z{-0.02}`. The run above is the stock compensation.

The plate stands 215 × 267 mm — the ceiling's own footprint — and the mesh is 1,131,658 faces,
`mesh_stat` all zeros — no edges fixed, no degenerate facets, none removed and none reversed.

**No time or length to carry.** The archive holds the project and no g-code, so unlike the
front-top plate above there is no metre or hour figure to read back off it, and
[machine-time.md](/hardware/ledger/machine-time.md) §1 stands on the front-top's 20 h 23 m
alone.

### Where the faucet profile differs from the exterior PET-GF slice

Same stock, same nozzle, and the same volumetric cap, flow ratio and retraction. What the
faucet profile moves:

| | exterior (history-only `enclosure-front-top-petgf.3mf`) | back-top (this plate) |
|---|---|---|
| Print profile | `0.20mm Standard @BBL H2C` | **`0.24mm PET-GF faucet`** |
| Layer height | 0.20 mm | **0.24 mm** |
| Nozzle | 290 °C | **265 °C** |
| Plate, textured | 100 °C | **70 °C** |
| Chamber | 50 °C | 50 °C |
| Fan min / max / overhang | 0 / 0 / 0 % | **20 / 60 / 60 %** |
| Top shells | 5 | **4** |
| Support threshold | 30° | **35°** |

The three things the slot carries from the PET-CF preset it was cloned from it carries here
unchanged: `enable_pressure_advance` 0 over a dormant `pressure_advance` of 0.02,
`filament_type` `PET-CF` with `filament_ids` `GFT01`, and `filament_density` 1.29 at
`filament_cost` 44.99 — so the grams and the dollars Bambu Studio prints for this plate are
PET-CF's and not this spool's.

## The lower pump cradle and its top clamp (2026-09-11)

`enclosure-pump-cartridge` and `enclosure-pump-cap` in PET-GF15 on the left hotend, a
standard-flow 0.4 mm tungsten carbide ([tools.md](/hardware/ledger/tools.md)). The two pieces'
committed projects — [`enclosure-pump-cap-petgf.3mf`](enclosure-pump-cap-petgf.3mf) beside this
log and history-only
`git:62311012c79857590fe41895f29c67158eea74b3:hardware/printed-parts/enclosure/enclosure/enclosure-pump-cartridge-petgf.3mf`
— both carry the PET-GF15 exterior settings above: `Bambu Lab H2C 0.4 nozzle`, `0.20mm Standard
@BBL H2C`, `Polymaker PET-GF @BBL H2C` at 290 °C over a 100 °C plate and a 50 °C chamber, fan
off, 18 mm³/s, tree supports at 30°, the clamp turned onto its crown (`1 0 0 0 -1 0 0 0 -1`).
The plate that was printed is not in the tree; what it was sliced from, and at what first layer,
was decided at the printer ([z-trim.md](/hardware/printed-parts/z-trim.md)).

Derek said:
- "During the recent print of the pump cradle/cap, the H2C errored/paused with 'extruder motor
  overheating'. After waiting, and cleaning/clearing the exterior of the hotend, and trying to
  resume, it went back to 'extruder motor overheating' pretty quickly."
- "I swapped the hotend for the other (non-highflow) 0.4 mm Tungsten we have, and resumed, and
  it finished the print fine and is working on another fine."
- "I haven't cold pulled the potentially clogged hotend yet, but I plan to."

The resume after the swap ran the same job to the end. The hotend that paused is off the
printer, suspected clogged and not yet cold-pulled; the second standard-flow 0.4 TC is on the
left extruder and printing ([tools.md](/hardware/ledger/tools.md) "Hotend stock", which also
names where a replacement is bought). The same day Derek ordered three DUROZZLE 0.4 mm Diamond PCD
hotends for that extruder, one arriving 2026-09-12 ([purchases.md §13](/hardware/ledger/purchases.md)):
*"So far, the diamond PCD has been the toughest and most reliable, in other sizes."*

Bambu's guide for the H2 series' extruder-motor error
([Extruder Motor Overload Error Troubleshooting Guide](https://wiki.bambulab.com/en/h2/troubleshooting/extruder-motor-overload),
`HMS_0300_0900_0002_0001`): *"During printing, the extruder motor inside the toolhead
continuously monitors extrusion force in real time. When abnormal resistance is detected, the
printer triggers an error and pauses the print job."* Its step 6 is the swap Derek made —
*"using a spare new hotend ... to determine if the issue is caused by a clogged hotend"* — and
its step 3 names the one slicer-side cause, a volumetric cap meant for a high-flow hotend run on
a standard one; the PET-GF slot's cap is 18 mm³/s, under the 24 mm³/s Bambu rates the standard
0.4 TC at on PETG. The H2C cold-pull page lists *"Frequent Extruder Motor Overload Errors"* as
the sign of *"excessive nozzle resistance"*.

The cold pull is the printer's own routine, Settings › Toolbox › Nozzle Cold Pull Maintenance
([H2C Nozzle Cold Pull Maintenance and Cleaning](https://wiki.bambulab.com/en/h2c/maintenance/nozzle-cold-pull-maintenance-and-cleaning)),
run on the hotend installed on the left extruder: PLA or PETG as the pull filament, in a colour
lighter than the black PET-GF15 so residue shows, flushing at 290 °C for PET-class residue,
repeated until the tip comes out clean. A hotend that will not pass PLA or PETG at 250 °C is
fully clogged and goes through the
[unclogging procedure](https://wiki.bambulab.com/en/h2/troubleshooting/unclogging) first — its
hot-hex-wrench method works on a hotend off the printer.

## 2026-09-15 — front-bottom on Mark2

The clearance-adjusted `enclosure-front-bottom` was submitted through Bambu Connect.
Mark2 reported `RUNNING`, layer 0 of 754, with no print error at
2026-09-16T01:11:48.730399+00:00.

- Profile: `hardware/printed-parts/petgf.3mf`; support settings from specimen 10:
  tree(auto), default style, 0.45 mm requested top gap, two interface layers,
  0.5 mm interface spacing, automatic pattern, interface loops off, 0.4 mm XY gap,
  zero support expansion.
- Left 0.4 mm Standard nozzle; PET-GF on the external spool, mapped as PET-CF.
- Textured PEI; 0.24 mm layers, 0.20 mm first layer; 265 °C first nozzle temperature,
  280 °C thereafter; 80 °C bed.
- Requested Z trim +0.04 mm. Stock textured-plate compensation −0.02 mm gives
  the emitted `G29.1 Z0.02`.
- Bed leveling on, timelapse off, flow and nozzle-offset calibration Auto.
- Slicer estimate: 17 h 37 min, 561.04 g, 754 layers.

The source mesh, profile, sliced archive and G-code hashes are recorded in
[print-jobs.json](print-jobs.json).

## 2026-09-16 — front-top on Mark2

The aft-travel-adjusted `enclosure-front-top` was submitted through Bambu Connect.
Mark2 reported `RUNNING`, layer 0 of 813, with no print error at
2026-09-16T19:13:31.666348+00:00.

- Profile: `hardware/printed-parts/petgf.3mf`; support settings from specimen 10:
  tree(auto), default style, 0.45 mm requested top gap, two interface layers,
  0.5 mm interface spacing, automatic pattern, interface loops off, 0.4 mm XY gap,
  zero support expansion.
- Left 0.4 mm Standard nozzle; PET-GF on the external spool, mapped as PET-CF.
- Textured PEI; 0.24 mm layers, 0.20 mm first layer; 265 °C first nozzle temperature,
  280 °C thereafter; 80 °C bed.
- Requested Z trim +0.04 mm. Stock textured-plate compensation −0.02 mm gives
  the emitted `G29.1 Z0.02`.
- Bed leveling on, timelapse off, flow and nozzle-offset calibration Auto.
- Slicer estimate: 19 h 50 min, 685.54 g, 813 layers.

The source mesh, profile, sliced archive and G-code hashes are recorded in
[print-jobs.json](print-jobs.json).

## 2026-09-17 — tee-carrier pair on Mark2

The current left and right tee-carrier halves, including their service tabs, were
submitted together through Bambu Connect.
Mark2 reported `RUNNING`, layer 0 of 258, with no print error at
2026-09-17T16:05:37.595754+00:00.

- Profile: `hardware/printed-parts/petgf.3mf`; support settings from specimen 10:
  tree(auto), default style, 0.45 mm requested top gap, two interface layers,
  0.5 mm interface spacing, automatic pattern, interface loops off, 0.4 mm XY gap,
  zero support expansion.
- Left 0.4 mm Standard nozzle; PET-GF on the external spool, mapped as PET-CF.
- Textured PEI; 0.24 mm layers, 0.20 mm first layer; 265 °C first nozzle temperature,
  280 °C thereafter; 80 °C bed.
- Requested Z trim +0.04 mm. Stock textured-plate compensation −0.02 mm gives
  the emitted `G29.1 Z0.02`.
- Bed leveling on, timelapse off, flow and nozzle-offset calibration Auto.
- Slicer estimate: 1 h 42 min, 53.72 g, 258 layers.

The source mesh, profile, sliced archive and G-code hashes are recorded in
[print-jobs.json](print-jobs.json).

## 2026-09-20 — front-top on H2C

The `enclosure-front-top-petgf-z018-h2c.gcode.3mf` job was submitted through Bambu Connect, driven by
`tools/bambu-ax` with the screen borrowed for one second. H2C reported `RUNNING`,
layer 0 of 813, with no print error at 2026-09-20T18:49:48.281882+00:00.

- Profile: `hardware/printed-parts/petgf.3mf`; support settings from specimen 10:
  tree(auto), default style, 0.45 mm requested top gap, two interface layers,
  0.5 mm interface spacing, automatic pattern, interface loops off, 0.4 mm XY gap,
  zero support expansion.
- Left 0.4 mm nozzle, sliced as Standard; the head carries the 0.4 mm diamond PCD.
  PET-GF on the left external spool, mapped as PET-CF.
- Textured PEI; 0.24 mm layers, 0.20 mm first layer; 265 °C first nozzle temperature,
  280 °C thereafter; 80 °C bed.
- Requested Z trim +0.18 mm. Stock textured-plate compensation −0.02 mm gives
  the emitted `G29.1 Z0.16`.
- Bed leveling on, timelapse on, flow and nozzle-offset calibration Auto.
- Slicer estimate: 24 h 9 min, 807.36 g, 813 layers.

The STL in the tree hashes differently from the sliced copy; both hashes are in
[print-jobs.json](print-jobs.json), with the profile, archive and G-code hashes.

The job is **cancelled**, confirmed by Bambu Connect and printer status at
2026-09-20T21:34:13.528173+00:00, after the last observed running layer 51/813.
The sliced valve-tray region is 2 mm above the corrected model. Both heater targets
are zero.

## 2026-09-21 — complete front-top on H2C

The current full `enclosure-front-top` and one reusable carrier spring pusher started
on H2C at 2026-09-21T06:24:35.628199+00:00. The job is **cancelled**, confirmed by Bambu Connect and MQTT at
2026-09-21T07:20:31.779542+00:00. The last observed running layer was 3/813.
The actual cold-core shell intersects the printed aft tray by 3.29 mm in Y; the
front-top requires correction. Both heater targets are zero. Derek resumed the
brief design-review pause before cancellation and instructs agents to keep potentially
productive prints running or cancel and replace them, never pause for design analysis.

- Black PET-GF on the left external spool, mapped as PET-CF; fixed left 0.4 mm nozzle.
- Saved `petgf.3mf` process and support settings; this prepared plate uses `no_brim`,
  with zero emitted brim paths. The saved default for future projects is `auto_brim`.
- Requested Z trim +0.18 mm; emitted textured-plate trim +0.16 mm.
- Timelapse and bed leveling On; flow and nozzle-offset calibration Auto.
- Estimate: 24 h 16 min 20 s, 818.17 g at the saved 1.29 g/cm³ density,
  approximately 906.96 g at the PET-GF accounting density of 1.43 g/cm³.
- Actual object/support paths retain at least 20.851 mm bed-edge distance and
  12.639 mm mutual separation. Support-removal lanes are recorded for every body.

The [print job](print-jobs.json) binds the source, project, archive and G-code hashes.
The [release report](../tee-readiness/full-enclosure-print/2026-09-21-enclosure-front-top-h2c-v3.json)
carries the native slice and support review. Spring feel, retention, rigidity and physical
support removal remain readings of the complete enclosure trial.

## 2026-09-21 — full cartridge and raised cap on H2C

The full pump cartridge and raised, open motor-end cap printed on H2C.
MQTT confirmed `RUNNING`, layer 0/496, no error, at 2026-09-21T07:47:46.755410+00:00, and
`FINISH` at 496/496 with no error at 2026-09-21T19:22:46.620569+00:00
([completion record](../tee-readiness/full-enclosure-print/h2c-pump-cartridge-cap-completion.json)).
Derek confirmed the plate clear before submission.

- Black PET-GF on left external 254, mapped as PET-CF; fixed left 0.4 mm diamond PCD.
- Saved process/support profile and `auto_brim`; the actual slice emits zero brim paths.
- Requested Z trim +0.18 mm, emitted textured-plate trim +0.16 mm.
- Timelapse and bed leveling On; flow and nozzle-offset calibration Auto.
- Estimate: 10 h 9 min 12 s, 419.94 g at saved density, 465.51 g at PET-GF accounting density.
- Six support bodies have accessible removal lanes before hardware installation.
- Native current-source reconstruction preserves both parts and their fitted mating surfaces.

The [launch record](../tee-readiness/full-enclosure-print/h2c-pump-cartridge-cap-launch.json)
binds the accepted archive and local mating proof.

## 2026-09-21 — front-top v4 on H2C

`enclosure-front-top-black-z018-h2c-v4.gcode.3mf` printed on H2C and was reported finished and
removed ([launch](../tee-readiness/full-enclosure-print/h2c-front-top-v4-launch.json),
[completion](../tee-readiness/full-enclosure-print/h2c-front-top-v4-completion.json)). Derek's
readings of the part: the R18 above the display steps about 2 mm at its top layer, and supports
stood trapped behind the display skirt-pocket surrounds.

## 2026-09-21 — front-bottom v2 on Mark2

`enclosure-front-bottom-black-z004-mark2-v2.gcode.3mf` printed on Mark2 and was reported finished
and removed ([launch](../tee-readiness/full-enclosure-print/mark2-front-bottom-v2-launch.json),
[completion](../tee-readiness/full-enclosure-print/mark2-front-bottom-v2-completion.json)).

## 2026-09-22 — display covers v3 and v4 on Mark2

Both printed face down on Mark2 ([v3 completion](../tee-readiness/full-enclosure-print/mark2-display-cover-v3-completion.json),
[v4 completion](../tee-readiness/full-enclosure-print/mark2-display-cover-v4-completion.json)).

## 2026-09-22 — back-top v2 on H2C

`enclosure-back-top-black-z018-h2c-v2.gcode.3mf`, ceiling down, reported `RUNNING` on H2C at
2026-09-22T19:04:30.084409+00:00 ([launch](../tee-readiness/full-enclosure-print/h2c-back-top-v2-launch.json)).
It was sliced from the 2026-09-21 inputs, uniformly in 0.24 mm layers.

## 2026-09-23 — back-top v2 finished on H2C

H2C reported `FINISH` at 813/813 layers with no error before 16:30 local.

## 2026-09-23 — front-top v12 on H2C

`enclosure-front-top-black-z018-h2c-v12.gcode.3mf` reported `RUNNING` on H2C at
2026-09-23T21:55:53Z, black PET-GF on the left external spool
([launch](../tee-readiness/full-enclosure-print/h2c-front-top-v12-launch.json)). Its top 2.6 mm
print in 0.08 mm layers. The support audit reads 4 bed-rooted trees and 9 contacts.

## 2026-09-23 — TAP and FLAVOR bulkhead rings on Mark2

`bulkhead-rings-tap-flavor-black-white-z004-mark2-v1.gcode.3mf` reported `RUNNING` on Mark2 at
2026-09-23T23:00:17Z: the TAP chip in white with its word in black, both FLAVOR chips in black
with their words in white, face up in 0.20 mm layers, black on the left hotend and white on the
right ([launch](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-23-bulkhead-rings-tap-flavor-mark2-v1/mark2-launch.json)).

## 2026-09-23 — front-top v12 cancelled on H2C

Cancelled on Derek's word at layer 51 of 1326 (H2C `FAILED`, heaters off). Its 0.08 mm band
covered only the last 2.6 mm of the R18 above the display and the R6 roof side edges. Derek's
rule is 0.08 mm through the entire curve.

## 2026-09-24 — front-top v13 on H2C

`enclosure-front-top-black-z018-h2c-v13.gcode.3mf` reported `RUNNING` on H2C at
2026-09-24T00:16:36Z, black PET-GF on the left external spool. It prints 0.08 mm layers
through the whole of every roof curve, from print z 187.0 to 195.0, and 0.24 mm elsewhere
([launch](../tee-readiness/full-enclosure-print/h2c-front-top-v13-launch.json)).

## 2026-09-24 — bulkhead rings v2 on Mark2

The v1 rings, face up in 0.20 mm layers, turned out badly in Derek's reading. v2 prints the
same three chips in 0.08 mm layers throughout, 25 of them, and reported `RUNNING` on Mark2 at
2026-09-24T00:35:45Z ([launch](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-23-bulkhead-rings-tap-flavor-mark2-v2/mark2-launch.json)).

## 2026-09-24 — face-down bulkhead rings v3 on Mark2

Derek found v2's 0.08 mm lettering better than v1 but less sharp than the face-down nameplate.
The same TAP and two FLAVOR chips print with their lettered faces against the bed, all 25 layers
at 0.08 mm. The requested Mark2 trim is +0.04 mm (+0.02 mm emitted on Textured PEI). Mark2
reported `RUNNING` at 2026-09-24T02:01:44Z, task 1277448913, with black on external 254 and
white on external 255, no printer error
([launch](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-23-bulkhead-rings-tap-flavor-mark2-v3/mark2-launch.json)).

## 2026-09-24 — bulkhead rings v4 on Mark2

The 0.08 mm face-down v3 was stopped on Derek's word. v4 prints the three chips face down on
the nameplate's own PET-GF settings (0.20 mm first layer, 0.24 mm after), and reported `RUNNING`
on Mark2 at 2026-09-24T02:55:11Z ([launch](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-bulkhead-rings-tap-flavor-mark2-v4/mark2-launch.json)).

## Tee carrier — Mark2, 2026-09-24 UTC

Task `1277634817` reports RUNNING with `tee-carrier-plate-black-z004-mark2-v10.gcode.3mf`.
The bed contains one smooth tee carrier. Black PET-GF feeds the left nozzle from external spool 254.
Requested Z trim is +0.04 mm; Textured PEI compensation emits `G29.1 Z0.02`.

The 189 emitted model layers are 0.08 mm from print Z 0 to 6.08, 0.24 mm from 6.08 to 14.96,
and 0.08 mm from 14.96 to 21.04. The exposed R6 rounds occupy Z 0–6 and 15.054–21.054.
The first layer is 0.08 mm. Two short bed-rooted support slivers lie under the aft rounds.

[Slice and launch record](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v10/manifest.json).

## Tee carrier without supports — Mark2, 2026-09-24 UTC

Task `1277839952` completed at 189/189 layers with `tee-carrier-plate-black-z004-mark2-v11-no-supports.gcode.3mf`. The bed contains one smooth tee carrier, using black PET-GF on left external spool 254. Supports are disabled; the native slice contains zero support paths and zero support bodies.

The geometry, placement and all other settings match the successful v10 print. All 189 model layer heights match: 0.08 mm from print Z 0 to 6.08, 0.24 mm from 6.08 to 14.96, and 0.08 mm from 14.96 to 21.04. Requested Z trim is +0.04 mm; the textured-plate command is `G29.1 Z0.02`. Timelapse and bed leveling are On; flow and nozzle offset calibration are Auto.

Derek reports that many things turned out well in v10. Its supports got in the way and were too small to help at this layer height beside the corbels. He cleared the plate and requested this repeat with supports removed.

Derek's finished v11 surface has a clean upper curve and localized lower-curve curling.
The first approximately 20 layers are clean; lifting around layers 20–30 causes nozzle drag
and 3–6 disturbed layers, then recovery within the 0.08 mm band as the curve steepens.
The cause remains unconfirmed. Unsupported visible 0.08 mm rounds remain his direction,
including enclosure back-top, with their thermal performance under evaluation.
[Physical observation and photos](../tee-carrier/physical-observations/2026-09-24-v11/README.md).

[Slice comparison and launch record](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v11/manifest.json).

## Tee carrier with part cooling off — Mark2, 2026-09-24 UTC

Task `1278660260` completed at 189/189 layers with
`tee-carrier-plate-black-z004-mark2-v12-fan-off.gcode.3mf`. One carrier, black PET-GF on left external 254,
no supports. All 189 layer heights, geometry and placement match v11. Requested Mark2
Z trim is +0.04 mm; Textured PEI emits +0.02 mm.

The trial turns part cooling off, including the overhang override, to test whether forced
cooling contributes to the lower curve's lifting. Temperatures remain 265°C on the first
layer, 280°C thereafter, 80°C bed and no active chamber heat. Derek rejects the physical result:
“That turned out worse. Exploded basically.” Deposited edges retreat inward around layers
20–30 and leave subsequent perimeters printing in air; the intact interior recovers outward
as the curve steepens. The exact thermal cause remains unconfirmed.
Part cooling off is rejected as a remedy for this carrier at these settings.
Native estimate: 2 h 5 m 46 s, 44.93 g. Timelapse and bed leveling On; flow and nozzle-offset
calibration Auto. The exact archive was accepted after a fresh import and a 20-second
settling wait following an invalid-3MF rejection.

[Slice, hypothesis and launch record](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v12/README.md).

## Tee carrier with steady part cooling — Mark2, 2026-09-24 UTC

Task `1279237907` reports RUNNING with
`tee-carrier-plate-black-z004-mark2-v13-steady-cooling.gcode.3mf`. One carrier, black PET-GF on left external 254,
no supports. Geometry, placement and all 189 layer heights match v11. Requested Mark2
Z trim is +0.04 mm; Textured PEI emits +0.02 mm.

Part cooling is 55% on every model extrusion from layer 4 through layer 189, including
bridges and overhangs. The first three layers retain zero part cooling; the auxiliary fan
stays off. This tests whether steady cooling preserves the expanding edge and its overlap
with the next perimeter. The v11 fan-off interval at layer 26 is a clue, not an established
cause. Temperatures remain 265°C first layer, 280°C thereafter, 80°C bed and no active chamber
heat. Physical outcome is pending.

Native estimate: 2 h 5 m 48 s, 44.93 g. Timelapse and bed leveling On; flow and nozzle-offset
calibration Auto. A fresh import with a 20-second settling wait was accepted on the first
send attempt.

[Slice, hypothesis and launch record](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v13/README.md).
