# Spatial Resolution: Sub-A Box Shell

## Trivial Case

Sub-A is a simple prismatic open-top box. It has no angled mounting, no physics-dependent profiles, and no cross-frame spatial relationships to resolve. The tray sits level inside the enclosure. The box shell's own reference frame is the tray reference frame — there is no transform.

All dimensions below are stated for completeness and to satisfy the quality gate, but no derivation or coordinate transformation was required to produce them.

---

## 1. System-Level Placement

```
Mechanism: Pump Cartridge Tray
Parent: Enclosure interior (front-bottom zone)
Position: slides in on T-rails from the front of the enclosure
Orientation: level (no rotation). Tray axes align with enclosure axes.
```

The tray is at the bottom-front of the enclosure. It slides along the Y axis (rear = dock side, front = user side). Once seated, the tray's coordinate frame aligns with the enclosure's local axes — no rotation in any plane.

---

## 2. Part Reference Frame

```
Part: Box Shell (Sub-A)
  Origin: rear-left-bottom corner (dock side)
  X: width, 0..160 mm (left to right when facing the front)
  Y: depth, 0..155 mm (0 at rear/dock wall, 155 at front/user side)
  Z: height, 0..72 mm (0 at floor bottom, 72 at top of side walls)
  Print orientation: open top facing up, XY plane on build plate
  Installed orientation: identical to print orientation (no rotation)
```

The part frame IS the tray frame. Downstream sub-components (B through J) all reference this same frame.

---

## 3. Derived Geometry

**No derived geometry is required.** The box shell is a rectangular prismatic solid with uniform wall thicknesses. There are no physics-dependent profiles, no angled interfaces, and no cross-frame transforms to resolve.

For reference, the concrete dimensions in the part's own frame:

### Outer envelope
- X: 0 to 160 mm
- Y: 0 to 155 mm
- Z: 0 to 72 mm

### Wall thicknesses
- Left wall: X = 0 to 5 mm (5 mm thick)
- Right wall: X = 155 to 160 mm (5 mm thick)
- Floor: Z = 0 to 3 mm (3 mm thick)
- Rear wall: Y = 0 to 8.5 mm (8.5 mm thick, dock side)
- Top: open (no ceiling)
- Front: open at Y = 155 mm (no front wall; bezel attaches separately)

### Interior pocket
- X: 5 to 155 mm (150 mm wide)
- Y: 8.5 to 155 mm (146.5 mm deep)
- Z: 3 to 72 mm (69 mm tall)

### Interface surfaces (for downstream sub-components)

| Interface | Surface location (part frame) | Mating sub-component |
|-----------|-------------------------------|----------------------|
| Left wall exterior | X = 0 plane, Y = 0..155, Z = 0..72 | Sub-B (left T-rail tongue) |
| Right wall exterior | X = 160 plane, Y = 0..155, Z = 0..72 | Sub-B (right T-rail tongue) |
| Interior floor | Z = 3 plane, X = 5..155, Y = 8.5..155 | Sub-C (pump bosses), Sub-F (tube channels) |
| Rear wall interior | Y = 8.5 plane, X = 5..155, Z = 3..72 | Sub-D (fitting bores, from exterior), Sub-E (guide posts) |
| Rear wall exterior | Y = 0 plane, X = 0..160, Z = 0..72 | Sub-D (fitting bore entries/funnels), Sub-J (electrical pads) |
| Left wall interior | X = 5 plane, Y = 8.5..155, Z = 3..72 | Sub-G (linkage slot), Sub-H (lid snap ridges) |
| Right wall interior | X = 155 plane, Y = 8.5..155, Z = 3..72 | Sub-G (linkage slot), Sub-H (lid snap ridges) |
| Front edges | Y = 155 plane, all wall/floor cross-sections | Sub-I (bezel receiving features) |
| Top edges | Z = 72 plane, wall cross-sections only | Sub-H (lid snap ridges, near top) |

---

## 4. Transform Summary

```
Part frame = Tray frame = System frame (no rotation, no translation offset within the tray assembly)

Part-local (0, 0, 0) = tray origin (rear-left-bottom) = system position of cartridge rear-left-bottom
Part-local X-axis = system X-axis (width)
Part-local Y-axis = system Y-axis (depth, rear to front)
Part-local Z-axis = system Z-axis (height, up)

No rotation. Identity transform.
```

### Verification (trivial)
- Part-local (0, 0, 0) maps to tray (0, 0, 0) -- rear-left-bottom corner
- Part-local (160, 155, 72) maps to tray (160, 155, 72) -- front-right-top corner
- Part-local (80, 0, 36) maps to tray (80, 0, 36) -- center of rear wall exterior face

All correct by identity.
