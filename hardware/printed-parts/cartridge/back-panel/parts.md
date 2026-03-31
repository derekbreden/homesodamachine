# Back Panel — Parts Specification

## Purpose

Flat panel that closes the back of the pump cartridge. Slides down into the back-panel
rail channels on the left and right walls. Four holes pass tube stubs from outside the
cartridge to the John Guest quick-connect couplers mounted in the coupler tray inside.

## Scope

Flat panel with 4 holes. No detent geometry, no retention features.

---

## Coordinate System

This part is specified and modeled in the **assembly frame** (same frame used by the
left-wall and coupler-tray scripts):

```
Origin: cartridge interior bottom-left-front corner (X=0, Y=0, Z=0)
X: left-to-right across interior width, 0..140.0mm
Y: front-to-back, 0..133.0mm
Z: bottom-to-top, 0..79.0mm
```

---

## Dimensions

| Parameter      | Value   | Source                                                                         |
|----------------|---------|--------------------------------------------------------------------------------|
| Width (X)      | 140.0mm | Interior X span between left and right wall interior faces                     |
| Thickness (Y)  | 3.0mm   | Back panel rail channel is 3.4mm wide; 0.2mm clearance each side (3.4 - 0.4)  |
| Height (Z)     | 79.0mm  | Full wall height (same as left/right walls, slides in from above)              |

### Installed position

- Back face: Y = 133.0mm (flush with wall back edge)
- Front face: Y = 130.0mm (inside rail channel)
- Panel occupies Y = 130.0mm..133.0mm

The back panel rail channel on the left and right walls is Y = 127.6..131.0mm (3.4mm
wide). The panel thickness (3.0mm) fits with 0.2mm clearance each side:
  channel inner edge = Y=127.6mm (interior lip face)
  panel front face   = Y=130.0mm  (127.6 + 0.2 + 2.0 lip = layout check below)

Wait — the channel is between the two lips. Lip A inner face is at Y=127.6mm
(lip A runs Y=125.6..127.6, so inner face = Y=127.6). Lip B inner face is at Y=131.0mm
(lip B runs Y=131.0..133.0, so inner face = Y=131.0). Channel width = 131.0 - 127.6 =
3.4mm. Panel thickness 3.0mm: clearance = (3.4 - 3.0) / 2 = 0.2mm per side.

Panel front face: Y = 127.6 + 0.2 = 127.8mm
Panel back face:  Y = 127.8 + 3.0 = 130.8mm

The panel is modeled with its front face at Y=127.8mm and back face at Y=130.8mm.
Height Z=0..79.0mm (full wall height), width X=0..140.0mm.

---

## Features

### Feature 1 — Panel body

Rectangular solid.

| Parameter  | Value          |
|------------|----------------|
| X          | 0..140.0mm     |
| Y          | 127.8..130.8mm |
| Z          | 0..79.0mm      |

Print orientation: front face (Y=127.8mm) down on build plate. This is a flat panel
with 4 simple through-holes. No overhangs, no supports required.

### Features 2–5 — Tube stub holes (H1, H2, H3, H4)

Four circular through-holes passing through the full panel thickness (3.0mm in Y).
These pass the tube stubs (1/4" John Guest push-connect fittings) from outside the
cartridge into the coupler tray inside.

**Coupler center positions** (from coupler-tray boss half script, assembly frame):
- H1: X = 43.1mm, Z = 34.3mm
- H2: X = 60.1mm, Z = 34.3mm
- H3: X = 77.1mm, Z = 34.3mm
- H4: X = 94.1mm, Z = 34.3mm

The coupler tray boss half sits at Y=0..12.08mm (front face of tray). The back panel is
at Y≈130mm — these holes do not intersect the tray geometry. The holes align the tube
stubs with the coupler X and Z centers so tubing runs straight in.

**Hole diameter:**
The John Guest PP0408W fitting body end (collet housing) is 15.10mm OD. The tube stub
passes through from outside — the relevant cross-section passing through the wall is
the tube itself (1/4" OD nominal = 6.35mm, caliper 6.30mm). However, the fitting may
be inserted body-end-first or the collet sleeve (9.57mm OD) must fit through during
assembly. Using the collet OD (9.57mm) + 0.2mm FDM loose-fit tolerance = 9.77mm →
round to 10.0mm nominal.

**Hole diameter: 10.0mm** (passes 9.57mm collet OD with 0.43mm total diametric
clearance; adequate for tube stub threading).

| Hole | X (mm) | Y center (mm) | Z (mm) | Diameter (mm) |
|------|--------|---------------|--------|---------------|
| H1   | 43.1   | 129.3         | 34.3   | 10.0          |
| H2   | 60.1   | 129.3         | 34.3   | 10.0          |
| H3   | 77.1   | 129.3         | 34.3   | 10.0          |
| H4   | 94.1   | 129.3         | 34.3   | 10.0          |

Y center = (127.8 + 130.8) / 2 = 129.3mm

Holes are through-holes (full Y span, Y=127.8..130.8mm).

---

## Interfaces

| Interface                  | Description                                                         |
|---------------------------|---------------------------------------------------------------------|
| Left wall back channel    | Panel slides into Y=127.6..131.0 channel, full Z height            |
| Right wall back channel   | Identical channel on right wall (mirror of left)                   |
| John Guest tube stubs     | H1–H4 pass 1/4" OD tubing to coupler tray couplers                 |

---

## Manufacturing Notes

- Print orientation: front face down (flat on build plate)
- No overhangs; all holes are vertical (Z-axis) through a flat plate → no bridging issues
- FDM hole tolerance: holes designed at 10.0mm; actual printed diameter will be ~9.8mm
  (holes print small). Increase to 10.2mm if measured fit is too tight.
- No supports required.

---

## Cross-References

- Left wall rail channel geometry: `hardware/printed-parts/cartridge/left-wall/generate_step_cadquery.py`
- Coupler X/Z center positions: `hardware/printed-parts/cartridge/coupler-tray/generate_step_cadquery_boss_half.py`
- John Guest fitting geometry: `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
- FDM constraints: `hardware/requirements.md`
- CadQuery standards: `hardware/pipeline/steps/6-step-generation.md`
