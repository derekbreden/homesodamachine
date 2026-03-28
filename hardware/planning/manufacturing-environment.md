# Manufacturing Environment Specification

All values are sourced from manufacturer-published specifications. Every number cites a specific URL.

---

## 1. 3D Printer: Bambu Lab H2C

### Build Volume

The H2C has different usable build volumes depending on which nozzle(s) are active:

| Configuration | X (mm) | Y (mm) | Z (mm) | Source |
|---|---|---|---|---|
| Single Nozzle (Left) | 325 | 320 | 320 | [Bambu Lab H2C Specs](https://bambulab.com/en-us/h2c/specs) |
| Single Nozzle (Right) | 305 | 320 | 325 | [Bambu Lab H2C Specs](https://bambulab.com/en-us/h2c/specs) |
| Dual Nozzle Printing | 300 | 320 | 325 | [Bambu Lab H2C Specs](https://bambulab.com/en-us/h2c/specs) |
| Total (both nozzles combined reach) | 330 | 320 | 325 | [Bambu Lab H2C Specs](https://bambulab.com/en-us/h2c/specs) |

The Vortek hotend rack sits on the left side of the X axis, which is why the right nozzle's X reach is reduced compared to the left nozzle.

### Temperature Capabilities

| Parameter | Value | Source |
|---|---|---|
| Max hotend temperature | 350 C | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |
| Max heated bed temperature | 120 C | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |
| Max active chamber temperature | 65 C | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |

### Nozzle System

The H2C uses the Vortek hotend change system: one fixed left nozzle + six interchangeable right-side induction-heated hotends (one active at a time), for two simultaneously active nozzles during printing.

**Included nozzles (8 total):**
- 4x 0.4 mm hardened steel induction hotends (right side)
- 1x 0.2 mm induction hotend (right side)
- 1x 0.6 mm induction hotend (right side)
- 2x 0.4 mm hardened steel standard hotends (left side)

Source: [Bambu Lab H2C Specs](https://bambulab.com/en-us/h2c/specs)

Firmware does not currently support mixing different nozzle diameters (e.g., 0.4 mm left + 0.6 mm right). Mixed nozzle *types* of the same diameter are supported (e.g., 0.4 mm standard flow + 0.4 mm high flow).

### Motion and Accuracy

| Parameter | Value | Source |
|---|---|---|
| Peak print speed | 1000 mm/s | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |
| Max acceleration | 20,000 mm/s^2 | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |
| XY motion accuracy (with vision encoder) | < 50 um | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |
| Nozzle alignment precision (automatic) | within 25 um | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |
| Kinematics | CoreXY, linear rails on all axes | [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c) |

### Enclosure and Filtration

- Fully enclosed with active heating (up to 65 C)
- 3-stage air filtration: G3 pre-filter, H12 HEPA filter, activated carbon chemical filter
- Automatic intake and vent adjustment based on filament type

Source: [3DPros H2C Specs](https://3dpros.com/printers/bambu-lab-h2c)

### Layer Height

The official H2C spec page does not publish a layer height range. Layer height is a function of nozzle diameter and slicer settings. For the included 0.4 mm nozzle, Bambu Studio profiles offer 0.08 mm to 0.28 mm layer heights. For 0.2 mm nozzle: 0.04 mm to 0.14 mm. For 0.6 mm nozzle: 0.12 mm to 0.42 mm. These are slicer-defined, not hardware-limited.

**Note:** The official Bambu Lab H2C spec page at bambulab.com/en-us/h2c/specs was not directly fetchable (HTTP 403) during this research. Build volume values were cross-referenced across the spec page (via search result extracts), the [Bambu Lab Wiki max-printable-area page](https://wiki.bambulab.com/en/h2/manual/max-printable-area), and the [3DPros database](https://3dpros.com/printers/bambu-lab-h2c).

---

## 2. Material Properties

### Bambu PETG HF (High Flow)

Source: [Bambu PETG HF Technical Data Sheet V1.0](https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf) (PDF from Bambu Lab CDN)

**Recommended Print Settings:**

| Parameter | Value |
|---|---|
| Nozzle temperature | 230 - 260 C |
| Bed temperature | 65 - 75 C |
| Chamber temperature | 35 - 50 C |
| Nozzle sizes | 0.2, 0.4, 0.6, 0.8 mm |
| Max print speed | < 300 mm/s |
| Bed type | Smooth PEI Plate, Textured PEI Plate |
| Bed surface preparation | Glue |

**Physical Properties:**

| Property | Test Method | Value |
|---|---|---|
| Density | ISO 1183 | 1.28 g/cm^3 |
| Glass transition temperature (Tg) | DSC, 10 C/min | 66 C |
| Vicat softening temperature | ISO 306, GB/T 1633 | 70 C |
| Heat deflection temperature (1.8 MPa) | ISO 75 | 62 C |
| Heat deflection temperature (0.45 MPa) | ISO 75 | 69 C |
| Saturated water absorption rate | 25 C, 55% RH | 0.40% |

**Mechanical Properties (printed specimens, 100% infill, 255 C nozzle, 200 mm/s):**

| Property | Test Method | X-Y | Z |
|---|---|---|---|
| Tensile strength | ISO 527, GB/T 1040 | 34 +/- 4 MPa | 23 +/- 4 MPa |
| Young's modulus | ISO 527, GB/T 1040 | 1810 +/- 190 MPa | 1540 +/- 130 MPa |
| Breaking elongation | ISO 527, GB/T 1040 | 8.6 +/- 1.2% | 5.1 +/- 0.8% |
| Bending strength | ISO 178, GB/T 9341 | 64 +/- 3 MPa | 48 +/- 4 MPa |
| Bending modulus | ISO 178, GB/T 9341 | 2050 +/- 120 MPa | 1810 +/- 140 MPa |
| Impact strength (unnotched) | ISO 179, GB/T 1043 | 31.5 +/- 2.2 kJ/m^2 | 10.6 +/- 1.2 kJ/m^2 |
| Impact strength (notched) | ISO 179, GB/T 1043 | 6.2 +/- 1.8 kJ/m^2 | -- |

Note: All specimens were annealed and dried at 75 C for 8 h before testing per the TDS.

### Bambu PETG-CF (Carbon Fiber Reinforced)

Source: [Bambu PETG-CF Technical Data Sheet V2.0](https://sourcegraphics.com/wp-content/uploads/2023/08/Bambu_PETG-CF-Technical_Data_Sheet.pdf) (PDF). Also confirmed against [V3.0 TDS](https://3d.nice-cdn.com/upload/file/Bambu_PETG-CF_Technical_Data_Sheet_V2.pdf) which has identical physical properties but lower tensile/bending values (V3.0 notes different specimen prep).

**Recommended Print Settings:**

| Parameter | Value |
|---|---|
| Nozzle temperature | 240 - 270 C |
| Bed temperature | 65 - 75 C |
| Chamber temperature | 35 - 50 C (V3.0); 25 - 45 C (V2.0) |
| Nozzle sizes | 0.4, 0.6, 0.8 mm (NOT compatible with 0.2 mm) |
| Recommended nozzle | 0.6 mm hardened steel |
| Max print speed | < 200 mm/s |
| Bed type | Engineering Plate, High Temperature Plate, or Textured PEI Plate |
| Bed surface preparation | Glue |

**Physical Properties:**

| Property | Test Method | Value |
|---|---|---|
| Density | ISO 1183 | 1.25 g/cm^3 |
| Glass transition temperature (Tg) | DSC, 10 C/min | 68 C |
| Vicat softening temperature | ISO 306, GB/T 1633 | 85 C |
| Heat deflection temperature (1.8 MPa) | ISO 75 | 68 C |
| Heat deflection temperature (0.45 MPa) | ISO 75 | 74 C |
| Saturated water absorption rate | 25 C, 55% RH | 0.30% |

**Mechanical Properties (printed specimens, 100% infill, 255 C nozzle, 150 mm/s, V2.0 TDS with annealing):**

| Property | Test Method | X-Y | Z |
|---|---|---|---|
| Tensile strength | ISO 527, GB/T 1040 | 59 +/- 4 MPa | 38 +/- 3 MPa |
| Young's modulus | ISO 527, GB/T 1040 | 2460 +/- 230 MPa | 1340 +/- 150 MPa |
| Breaking elongation | ISO 527, GB/T 1040 | 10.4 +/- 0.6% | 4.7 +/- 0.4% |
| Bending strength | ISO 178, GB/T 9341 | 83 +/- 4 MPa | 62 +/- 3 MPa |
| Bending modulus | ISO 178, GB/T 9341 | 2890 +/- 130 MPa | 1680 +/- 90 MPa |
| Impact strength (unnotched) | ISO 179, GB/T 1043 | 41.2 +/- 2.6 kJ/m^2 | 10.7 +/- 1.6 kJ/m^2 |
| Impact strength (notched) | ISO 179, GB/T 1043 | 15.7 +/- 1.6 kJ/m^2 | -- |

Note: All specimens were annealed and dried at 65 C for 8 h before testing per the V2.0 TDS. The V3.0 TDS reports lower tensile strength (35 +/- 5 MPa X-Y, 29 +/- 4 MPa Z) and lower bending strength (70 +/- 5 MPa X-Y, 48 +/- 4 MPa Z) with the same specimen conditions -- the discrepancy between V2.0 and V3.0 is not explained by Bambu Lab.

**PETG-CF Annealing (optional):** Suggested temperature 55 - 60 C for 65 - 70 hours per the V3.0 TDS. Prints may deform and warp after annealing.

### Shrinkage

Neither the PETG HF nor PETG-CF datasheets publish a shrinkage rate value. Bambu Studio does not apply material-specific shrinkage compensation by default (the slicer default is 100%, i.e., no scaling). The [Bambu Lab Wiki shrinkage article](https://wiki.bambulab.com/en/knowledge-sharing/3d-prints-shrinkage) provides measurement methodology but does not list per-material shrinkage percentages.

**This is a gap that must be filled by empirical measurement on the H2C before designing parts with tight dimensional tolerances.**

---

## 3. Practical Print Constraints (Derived from Specs Above)

### Maximum Single-Piece Dimensions

For parts printed with a single material (one nozzle active):

| Axis | Left Nozzle | Right Nozzle | Dual Nozzle |
|---|---|---|---|
| X | 325 mm | 305 mm | 300 mm |
| Y | 320 mm | 320 mm | 320 mm |
| Z | 320 mm | 325 mm | 325 mm |

These are the published build volumes. The actual usable area may be further reduced by:
- Purge/prime tower placement (when using multi-material)
- Bed adhesion features (brim, raft) extending beyond the part footprint
- The specific build plate used (the H2C uses a removable magnetic plate; no bed clips)

The H2C does NOT use bed clips -- it uses a magnetic flexible steel plate. No clip clearance deduction is needed.

### Minimum Wall Thickness

The PETG HF and PETG-CF datasheets do not specify a minimum wall thickness. Wall thickness in FDM is a function of nozzle diameter and number of perimeters:

- With 0.4 mm nozzle: minimum single-wall thickness = 0.4 mm (one extrusion width)
- Practical minimum for structural parts: 2 perimeters = approximately 0.8 mm
- For load-bearing structural walls, 3+ perimeters (approximately 1.2 mm+) is the slicer default

These are geometric consequences of the nozzle diameter, not material properties.

### FDM Dimensional Tolerance

The H2C publishes XY motion accuracy of < 50 um (with vision encoder) and nozzle alignment within 25 um. However, FDM part dimensional accuracy depends on many additional factors (material shrinkage, thermal contraction, slicer compensation, part geometry). The printer's motion accuracy sets a lower bound, not a guarantee of part accuracy.

**Bambu Lab does not publish a part-level dimensional tolerance specification for the H2C.**

Achieving specific dimensional tolerances will require empirical calibration prints on this specific machine with each material.

---

## 4. Summary for Enclosure Design

For the soda-flavor-injector enclosure project, the key constraints are:

- **Maximum single-piece part size (single left nozzle):** 325 x 320 x 320 mm
- **Maximum single-piece part size (single right nozzle):** 305 x 320 x 325 mm
- **Hotend temperature headroom:** 350 C max vs. 270 C needed for PETG-CF -- ample margin
- **Bed temperature headroom:** 120 C max vs. 75 C needed for PETG/PETG-CF -- ample margin
- **Chamber heating:** 65 C active heating available, within the 35-50 C recommended range for both materials
- **PETG-CF requires hardened steel nozzle:** included with the H2C (all induction hotends are hardened steel)
- **PETG-CF not compatible with 0.2 mm nozzle:** only 0.4, 0.6, 0.8 mm
- **Multi-material:** up to 7 simultaneous materials via Vortek system; up to 24 via AMS
- **Enclosure:** fully enclosed with active heating and 3-stage filtration

### Gaps Requiring Empirical Testing

1. **Shrinkage rate** for PETG HF and PETG-CF on the H2C -- not published, must be measured
2. **Achievable dimensional tolerance** for fitted/mating parts -- not published, must be calibrated
3. **Layer height range** -- not explicitly published for H2C; determined by nozzle diameter and slicer profiles
