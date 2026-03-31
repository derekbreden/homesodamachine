# Front Panel — Parts Specification

Season 2, Phase 7, Item 18 of the pump cartridge build sequence.

## Purpose

Flat panel that closes the front face of the cartridge. Slides into the front panel
rail channels on the left and right walls. Contains a rectangular hole in the lower
half to allow the user's fingers to reach the lever pull surface.

## Interfaces

- **Left wall front panel channel:** Y=2.0..5.4mm (3.4mm wide in Y), slides in from
  above (-Z direction). Panel back face at Y=3.0mm, front face at Y=0mm (flush with
  wall front edge).
- **Right wall front panel channel:** same geometry, mirrored — panel spans the
  interior X gap between the two walls.
- **Lever pull surface:** Lever plate front face is at Y=0mm (coincident with panel
  front face plane). The rectangular hole provides finger clearance to contact the
  lever pull surface. Lever dimensions from
  `hardware/printed-parts/cartridge/lever/generate_step_cadquery.py`:
  140mm wide (X), 68.6mm tall (Z), with front face at Y=0.

## Coordinate System

```
Origin: front-panel bottom-left-front corner (X=0, Y=0, Z=0)
X: width axis, left to right; range [0, 140.0] mm
Y: thickness axis, front face (Y=0) to back face (Y=3.0); range [0, 3.0] mm
Z: height axis, bottom to top; range [0, 79.0] mm
Envelope: 140.0 (X) x 3.0 (Y) x 79.0 (Z) mm
```

## Dimensions

| Property          | Value   | Source                                      |
|-------------------|---------|---------------------------------------------|
| Width (X)         | 140.0mm | Interior X span between left and right walls |
| Thickness (Y)     | 3.0mm   | 3.4mm channel – 0.2mm clearance each side   |
| Height (Z)        | 79.0mm  | Full wall height                            |

## Features

### Feature 1 — Panel Body

Flat rectangular panel forming the full front face of the cartridge.

- Operation: Add (extrusion)
- Shape: Box
- Dimensions: 140.0mm (X) × 3.0mm (Y) × 79.0mm (Z)
- Position: X:[0, 140], Y:[0, 3], Z:[0, 79]

### Feature 2 — Finger Access Hole

Rectangular through-hole in the lower half of the panel. Allows the user's fingers to
reach the lever pull surface (lever plate front face at Y=0). Sized to the lever's XZ
footprint with generous clearance for comfortable finger access.

Phase 8 will refine the exact dimensions. For Phase 7, baseline dimensions are derived
from the lever XZ footprint:

- Lever X range: [0, 140mm], centered at X=70mm
- Lever Z range: [0, 68.6mm], centered at Z=34.3mm

Hole dimensions (Phase 7 baseline):
- Width (X): 100mm — centered at X=70mm → X:[20, 120]
- Height (Z): 30mm — centered at Z=27mm → Z:[12, 42]
  - Z center = 27mm < 39.5mm (half of 79mm) → satisfies "lower half" requirement
- Depth (Y): full thickness, 3.0mm (through-hole)

- Operation: Remove (cut-through)
- Shape: Box
- Dimensions: 100.0mm (X) × 3.0mm (Y) × 30.0mm (Z)
- Position: X:[20, 120], Y:[0, 3], Z:[12, 42]

## Print Orientation

Print with the front face (Y=0) on the build plate — the front face is the user-visible
surface and benefits from the flat, smooth bed finish. The panel is 3mm thick in Y,
140mm wide in X, and 79mm tall in Z; it prints flat with no unsupported overhangs.

The rectangular hole is a simple through-hole along Y — no support needed.

## FDM Compliance

- Minimum wall thickness: 3.0mm body (compliant; 7.5× minimum)
- Hole edges: no overhangs — the hole is a box cut through a flat panel
- No unsupported geometry
- No bridging required

## Assembly Notes

Panel slides into the front panel channels on the left and right walls from above
(-Z direction). Front face is flush with the wall front edges (Y=0). The lever pull
surface is behind this panel; the finger hole gives direct access to it.
