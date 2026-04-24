# Atomizer Nozzle — 316L SS Two-Piece Pressure-Swirl

Custom hollow-cone pressure-swirl atomizer for the carbonator vessel
water-refill spray.  Designed for Xometry CNC production in 316L SS as
an alternative to off-shelf BETE / Lechler nozzles that are quote-only
or require phone orders.

## Parts

| File | Description |
|---|---|
| `atomizer-nozzle-body.step` | Nozzle body (1/2" hex, 1/8"-27 NPT male outlet, 1/4"-28 UNF inlet) |
| `atomizer-nozzle-puck.step` | Swirl distributor insert (press fit into body) |
| `atomizer-nozzle-body-drawing.pdf` | ANSI A drawing: section A—A + outlet face view, tolerance callouts |
| `atomizer-nozzle-puck-drawing.pdf` | ANSI A drawing: front face + side section, slot/feed-hole callouts |
| `generate_step_cadquery.py` | CadQuery source that produces both STEPs |
| `generate_drawing.py` | ReportLab source that produces both PDFs |

To regenerate:
```
tools/cad-venv/bin/python hardware/cut-parts/atomizer-nozzle/generate_step_cadquery.py
tools/cad-venv/bin/python hardware/cut-parts/atomizer-nozzle/generate_drawing.py
```

## Operating point

Sized to match **BETE CW25-H** (catalog hollow-cone atomizer that hits
exactly our spec):

| Parameter | Target | Notes |
|---|---|---|
| Inlet pressure | ~100 psi | Seaflo diaphragm pump |
| Vessel backpressure | 60–70 psi | CO₂ headspace |
| ΔP across nozzle | 30–40 psi | Design point |
| Flow rate | ~0.20 GPM (0.76 L/min) | At design ΔP |
| Spray pattern | Hollow cone | For maximum droplet surface area in CO₂ headspace |
| Cone angle | ~65–75° included | Per Rizk/Lefebvre K-curve at our geometry |
| Droplet size | ~100–150 µm MMD | Lefebvre SMD correlation |

## Critical dimensions

| Feature | Value | Tol. | Source |
|---|---|---|---|
| Orifice diameter | Ø1.10 mm | ±0.025 | BETE CW25-H |
| Orifice land length | 0.70 mm | ±0.05 | L/D = 0.64 (Lefebvre 0.5–1.0) |
| Swirl chamber D | Ø4.00 mm | H7 | D_s/d_o = 3.6 (Rizk 3–5) |
| Swirl chamber L (body) | 3.00 mm | ±0.10 | L_s/D_s = 0.75 |
| Convergent cone | 90° incl. | ±2° | Rusak 2020 ("manufacturable") |
| Puck OD / body seat | Ø6.00 | h7 / H7 | Light press, 0.005–0.010 mm interference |
| Puck length | 2.50 mm | ±0.10 | — |
| Puck central bore | Ø4.00 | H7 | Air-core extension of swirl chamber |
| Tangential slots | 4× (0.50 × 0.40) mm | ±0.05 | Rusak 2020 optimized |
| Slot tangent line | 2.00 mm off-axis | ±0.02 | Fully tangential to Ø4.00 |
| Axial feed holes | 4× Ø0.50 through | ±0.025 | At r=2.50 mm (slot midline) |
| Hex outer | 12.7 mm AF | std | 1/2" wrench |
| NPT outlet | 1/8"-27 NPT male | — | Tap per NPT spec after CNC |
| Inlet bore | Ø6.40 × 8 mm | — | Tap 1/4"-28 UNF after CNC, or use push-in fitting |

## Tolerance / Xometry callouts

Only two features in this part have tight tolerances that affect
performance.  Everything else is loose and can run at shop standard.

### Critical — must enforce on drawing

1. **Orifice (Ø1.10 × 0.70 mm):**
   > "Ø1.10 ± 0.025 mm, drilled + reamed, sharp-edged inlet,
   > NO DEBURR on outlet face, concentric to cone ±0.02 mm TIR."

   Rationale: the orifice edge sharpness controls discharge coefficient
   and cone angle.  Any radius on the outlet face collapses the hollow
   cone to a full cone or solid stream.

2. **Swirl chamber to orifice concentricity:**
   > "Ø4.00 H7 swirl chamber concentric to Ø1.10 orifice within
   > 0.05 mm TIR."

   Rationale: non-concentric swirl chamber skews the cone asymmetrically.

### Secondary — shop-standard tolerances fine

- Slot depth 0.40 ±0.05, width 0.50 ±0.05 (mill with Ø0.40 end mill)
- Puck OD / body bore press fit: Ø6.00 h7 × Ø6.00 H7
- 90° convergent cone ±2°
- Feed hole Ø0.50 ±0.025

### Loose — no call-out needed

- Hex outer dimensions (wrench size is the only constraint)
- NPT thread dimensions (standard tap)
- Overall length, inlet bore depth

## Xometry order notes

- **Material:** 316L SS on both parts.  316L over 316 for better
  corrosion resistance under carbonic acid + intermittent wet/dry.
- **Surface finish:** "As machined" (Ra 3.2 µm / 125 µin).  No
  post-processing needed for food contact at this pressure.
- **Quantity:** Order qty 2–3 per part for a first iteration (room
  for assembly trial-and-error and to have spares).
- **Threading:** Xometry supports 1/8-27 NPT male and 1/4-28 UNF
  female as standard tapping options.  Select both during
  quote configuration — do NOT expect the STEP to show helical
  thread form.
- **Drawing:** Xometry's instant quote will auto-detect features,
  but the orifice and concentricity call-outs above should be
  added as a PDF drawing attachment to the quote for the features
  that matter.

## Assembly sequence

1. Inspect both parts (especially the orifice — check for burrs,
   ovality, concentricity with a bore scope).
2. Align puck front face (slot side) toward the body shoulder.
3. Start puck into the Ø6.00 H7 body bore from the inlet end.
4. Press puck home with a vise and soft-jaw arbor (or a plastic
   mandrel) until its front face bottoms out against the body's
   Ø4.00 shoulder.  The puck is then captive — cannot be removed
   non-destructively.
5. Tap 1/8-27 NPT threads in the outlet (if not done by Xometry).
6. Tap 1/4-28 UNF threads in the inlet (if not done by Xometry) or
   install a push-in fitting.
7. Bench test on the Seaflo pump:  verify spray cone angle, flow
   rate, and absence of asymmetric spray.  Target: 0.20 GPM at
   40 psi ΔP, hollow cone 65–75° included.

## Design flow path

```
   INLET (1/4"-28 UNF)
     │
     ▼
   Ø6.40 inlet bore
     │
     ▼   (puck sits here, press fit)
   Ø6.00 puck seat  ───  PUCK back face
                    ───  4× Ø0.50 feed holes axial through puck
                    ───  PUCK front face (4× tangential slots)
     │                          ↑ slots direct flow tangent to Ø4
     ▼
   Ø4.00 swirl chamber  (water enters tangentially from slots,
                         spirals down, air core forms on axis)
     │
     ▼
   90° convergent cone  (swirl chamber Ø4 → orifice Ø1.1)
     │
     ▼
   Ø1.10 × 0.70 orifice  (sharp-edged inlet, burr-free outlet)
     │
     ▼
   OUTLET (1/8"-27 NPT)  → hollow cone spray into carbonator
                           vessel headspace
```

## Iteration notes

This is **v1**.  Likely first-pass tuning variables if the first build
misses the target:

- **Cone angle too narrow** (< 60°):  Increase slot cross-section
  to raise K = A_p/(D_s·d_o).  Current K = 0.182 → cone ~65–70°.
  Target K = 0.30 → 0.60 × 0.50 slots → cone ~75°.  Edit `SLOT_W`
  and `SLOT_D` in `generate_step_cadquery.py` and regenerate.

- **Flow rate too low:**  Increase orifice diameter in small
  increments (Ø1.10 → Ø1.20).  Flow scales as d_o² × √ΔP.
  Edit `ORIFICE_D`.

- **Cone collapses to full cone or solid stream:**  Usually an
  orifice edge problem (rounded by deburr) rather than a design
  problem.  Re-quote with explicit "no deburr on outlet face".

- **Asymmetric spray:**  Swirl chamber / orifice concentricity
  defect.  Re-quote with tighter TIR call-out or move to EDM'd
  orifice.

## Sources

- BETE CW metric catalog, BETE_CW_hollowcone-metric.pdf (CW25-H row)
- Lefebvre & McDonell, *Atomization and Sprays*, 2nd ed., Routledge
  2017, Ch. 6 (simplex pressure-swirl atomizer design equations)
- Rizk & Lefebvre 1985, "Internal Flow Characteristics of Simplex
  Swirl Atomizers," AIAA J. Propulsion 1(3):193–199
- Rusak et al. 2020, "Improved Atomization via a Mechanical
  Atomizer…," PMC 7345477 (optimized simplex geometry at
  small-orifice scale, source of 0.5×0.4 slot dimensions and
  90° cone angle)
- Chaudhari, Kulshreshtha, Channiwala 2013, IJAET 5(2):76–84 —
  full worked simplex design example
