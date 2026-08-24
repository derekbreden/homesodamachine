# enclosure print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in
committed `.3mf` snapshots.

Geometry: the six-piece box from
[`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) — four quadrants,
the pump cartridge and the cap screwed under it, one piece per plate — sizes in
[README.md](README.md), which the generator writes.

## The PETG exterior profile (settings per [`enclosure-front-top-0.4mm-16hours.3mf`](enclosure-front-top-0.4mm-16hours.3mf))

The geometry every exterior piece is cut to, sliced in PETG — the four quadrants, the pump
cartridge, and the cap screwed under it. The front-top, the largest of them, takes **16
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

## The PET-GF15 exterior (settings per [`enclosure-front-top-petgf.3mf`](enclosure-front-top-petgf.3mf))

What every exterior piece ships on: Polymaker Fiberon PET-GF15 on the Bambu 0.4 mm tungsten
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
moves, read off the two committed slices:

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
