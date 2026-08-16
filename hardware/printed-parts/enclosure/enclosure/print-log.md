# enclosure print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in
committed `.3mf` snapshots.

Geometry: the four-piece box from
[`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py), one piece per
plate — sizes in [README.md](README.md), which the generator writes.

## PET-GF15 print of the front-top (settings per [`enclosure-front-top-petgf.3mf`](enclosure-front-top-petgf.3mf))

**Running as this is written, 2026-08-15.** The first print of an enclosure piece in
Polymaker Fiberon PET-GF15, the finish candidate standing against the Bambu PETG Basic the
box prints in now ([bom.md §7](/hardware/ledger/bom.md)).

Derek, ~6 h in: *"working a treat so far"* — and on the result so far, *"very beautiful
wall surface."*

**Filament path.** The 3 kg PET-GF15 spool feeds from a Polymaker PolyDryer Box XL, not
from the SUNLU E2. A 3 kg spool turns too stiffly in the E2's chamber to feed a print;
the box carries it on a centre axle and it turns freely
([tools.md](/hardware/ledger/tools.md) "What dries where").

Settings:
- Printer: Bambu Lab H2C, 0.8 mm nozzle; profile `0.40mm Standard @BBL H2C 0.8 nozzle`
- Filament preset `Polymaker PET-GF`, one slot, textured PEI plate
- `layer_height` 0.4 mm (initial 0.4); `line_width` 0.82 mm
- `wall_loops` 2; top/bottom shells 4/3; `sparse_infill_density` 15 % grid
- `nozzle_temperature` **290 °C** (initial 290); `hot_plate_temp` / `textured_plate_temp`
  100 °C; `chamber_temperatures` 50 °C
- `filament_flow_ratio` 1.0; `filament_max_volumetric_speed` 5 mm³/s
- Fan **off** — min/max/overhang all 0 %, `close_fan_the_first_x_layers` 3
- Supports tree(auto); `brim_type` auto_brim, `brim_width` 5 mm; `seam_position` aligned,
  `filament_scarf_seam_type` none
- `filament_retraction_length` nil
- Slicer 02.07.01.62; first-layer time 1124 s

### What the material swap changed, and only that

The same object sliced in PETG is committed beside it as
[`enclosure-front-top.3mf`](enclosure-front-top.3mf). Every geometric and print-profile
setting is identical between the two — layer height, line width, wall count, shells,
infill, supports, brim, seam. The whole diff is the filament:

| | PETG (`Bambu PETG Basic High Temp`) | PET-GF15 (`Polymaker PET-GF`) |
|---|---|---|
| Nozzle | 250 °C (initial 245) | **290 °C** (initial 290) |
| Bed, textured | 85 °C | **100 °C** |
| Chamber | 0 (passive) | **50 °C** |
| Fan min / max / overhang | 20 / 40 / 90 % | **0 / 0 / 0 %** |
| Max volumetric speed | 21 mm³/s | **5 mm³/s** |
| Flow ratio | 0.97 | **1.0** |
| Retraction length | 0.4 mm | **nil** |

### Two things carried in from the PET-CF preset, unchanged

- **No PET-GF-specific flow calibration.** `enable_pressure_advance` is 0 with a dormant
  inherited `pressure_advance` of 0.02, so the slicer injects no PA and the run depends on
  whatever K the printer associates with the filament at send time. This is the same
  arrangement that produced the seam-clustered under-extrusion on PET-CF
  ([touch-flo-shell/print-log.md](/hardware/printed-parts/faucet/touch-flo-shell/print-log.md)
  attempt 18), where a measured K of 0.013 replaced the 0.02.
- **The preset's own `filament_type` reads `PET-CF`**, and `filament_vendor` reads
  `Bambu Lab`, because it was cloned from the PET-CF preset and those fields were not
  changed. The slot is named `Polymaker PET-GF`; the type the slicer reasons about is
  PET-CF.

Both are inherited state, not observations of this print. Neither has produced a defect
here so far.
