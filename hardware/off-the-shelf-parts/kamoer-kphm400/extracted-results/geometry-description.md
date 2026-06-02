# Kamoer KPHM400-SW3B25 Peristaltic Pump — Geometry Description

Geometry of the Kamoer KPHM400-SW3B25 peristaltic pump: every mounting surface, clearance zone, and interface needed to model the part or design a tray/cartridge that holds it.

## Overall Form

The pump is a two-body assembly: a black plastic pump head housing (roughly square cross-section when viewed from front) attached to a silver cylindrical DC motor via a white plastic adapter plate. The motor shaft enters the pump head from the rear, driving an internal 3-roller peristaltic mechanism.

Viewed from the front (tube connector face), the pump head is nearly square with rounded corners. The motor protrudes behind it, creating an elongated overall profile. A black stamped-metal mounting bracket sits at the junction between the pump head and motor. The bracket face — the flat surface where the pump head and motor meet — carries 4 mounting holes in a square pattern, with screws oriented parallel to the motor cylinder axis.

## Axis and Orientation Convention

- **X (width):** Horizontal in normal operating orientation.
- **Y (depth):** From front face (tube connectors) toward rear (motor terminals). The longest dimension.
- **Z (height):** Vertical. The pump head is roughly symmetric about the XY midplane.
- **Front face:** Carries the Kamoer branding label, yellow priming cap, 4 corner screws, and the tube connector exits.
- **Rear:** Motor terminal end.

## Major Sections Along the Y (Depth) Axis

### Section 1: Pump Head Front Face (Y = 0)
- Nearly square head-on: ~62.6mm wide x ~62.6mm tall
- 4x Phillips head screws at corners, holding the front cover plate on
- Yellow priming cap at center, ~10mm diameter, press-fit
- "Kamoer KPHM" branding label (black with yellow accent)
- Two tube connector exits protrude from this face:
  - White plastic barbed connectors for BPT tubing (4.8mm ID / 8.0mm OD)
  - Offset from center — one above center, one below (or left/right depending on orientation)
  - Barb protrusion from bracket surface: 34.54mm — the barbs extend 34.54mm forward of the mounting bracket face, within the 48.88mm full pump head depth
  - Tubing fit: 1/4" OD LLDPE routes through the BPT barbs and zip-ties tight — fits directly, no silicone adapter

### Section 2: Pump Head Body (Y = 0 to ~48mm)
- Black plastic housing containing the peristaltic roller mechanism
- Cross-section roughly square with rounded corners, ~62.6mm x ~62.6mm
- Pump head body depth: 48.88mm

### Section 3: Mounting Bracket (Y ≈ 48mm)
- Black stamped metal bracket plate at the junction face between pump head and motor
- The bracket face is perpendicular to the motor cylinder axis, parallel to the pump head's rear face
- Bracket width: ~68.6mm — ~3mm per side wider than the 62.6mm pump head
- Mounting holes:
  - 4x M3 through-holes in a square pattern on the bracket face, hole diameter 3.13mm
  - Center-to-center spacing: 50mm x 50mm square (±0.1mm)
  - The 4 holes surround the motor cylinder — screws pass through the bracket face parallel to the motor axis, threading into the pump head
  - This is the face where the pump mounts to a surface. The mounting surface is a flat plate with a bore for the motor cylinder to pass through, surrounded by 4 screw holes on the 50mm square pattern.
- Bracket thickness: ~1.5–2mm

### Section 4: Motor Adapter Plate (Y ≈ 48–52mm)
- White plastic disc/plate between bracket and motor
- Transitions from the square pump head bolt pattern to the round motor housing

### Section 5: DC Motor Body (Y ≈ 52mm to end)
- Silver cylindrical motor housing (standard 3xx-series DC motor form factor)
- Motor diameter: 35.73mm
- Flat on one side (anti-rotation feature)
- QR code, RoHS label, and Kamoer product label on motor body
- Motor shaft nub: a small protrusion from the center of the motor end cap (the non-drive end), 5.05mm long
- Motor terminal end: two solder tabs at the very rear

## Total Length

| Measurement | Value | What It Includes |
|-------------|-------|-----------------|
| Total length with motor nub | 116.48mm | Front face to end of motor shaft nub |
| Total length without motor nub | 111.43mm | Front face to motor end cap, excluding nub |
| Motor shaft nub protrusion | 5.05mm | 116.48 − 111.43 |

## Additional Dimensions

| Feature | Value |
|---------|-------|
| Pump head width | 62.61mm |
| Mounting hole edge-to-edge spacing (one axis of 4-hole square) | 47.88mm |
| Mounting hole diameter | 3.13mm |
| Pump head depth including front cover | 68.74mm |
| Pump body height/depth | 65.15mm |
| Pump head height | 61.19mm |
| Pump head dimension across bracket | 51.68mm |
| Pump head depth, side view | 48.88mm |
| Barb protrusion from bracket surface | 34.54mm |
| Motor body diameter | 35.73mm |
| Height across tube connectors / partial assembly span | 82.82mm |

## Datasheet Dimensions

Datasheet bounding box: 68.6W x 115.6D x 62.7H mm.

| Dimension | Datasheet | Part |
|-----------|-----------|------|
| Width (X) | 68.6mm | 62.61mm head; ~68.6mm across bracket (~3mm per side beyond the head) |
| Depth (Y) | 115.6mm | 116.48mm with nub, 111.43mm without (datasheet measures to motor end cap) |
| Height (Z) | 62.7mm | 62.51–62.61mm; pump head nearly square |

## Mounting Hole Pattern

The mounting holes are on the junction face between the pump head and motor — the flat face where the black cube meets the metal cylinder. Screws pass through this face parallel to the motor cylinder axis.

```
VIEW OF THE JUNCTION FACE (looking at the pump from the motor side):

              ◄── 50mm c-c ──►

         ○─────────────────────○
         │                     │  ▲
         │    ╱ ‾ ‾ ‾ ‾ ╲     │  │
         │   │  35.73mm     │    │  50mm c-c
         │   │  motor     │    │  │
         │    ╲ _ _ _ _ ╱      │  ▼
         │                     │
         ○─────────────────────○

    ◄──────── ~68.6mm bracket ────────►
    ◄───── 62.6mm pump head ─────►
```

- **Hole count:** 4 (square pattern)
- **Hole diameter:** 3.13mm (accepts M3 screws with ~0.13mm clearance)
- **Pattern:** 50mm x 50mm square, center-to-center
- **Hole positions:** On the bracket face surrounding the motor cylinder, symmetric about the pump center axis
- **Orientation:** Screws parallel to the motor/cylinder axis — they thread into the pump head from the motor side
- **Mounting surface:** A flat plate with a bore (~37mm+) for the 35.73mm motor cylinder to pass through, surrounded by 4 screw holes on the 50mm square pattern

## Clearance Zones

1. **Pump head envelope:** 62.6mm x 62.6mm square (rounded corners), ~48mm deep
2. **Bracket/mounting face:** Junction face between pump head and motor, 4x M3 holes on a 50mm square. Bracket ~68.6mm wide. Mounting surface needs a bore for the 35.73mm motor cylinder surrounded by 4 screw holes on the 50mm square pattern.
3. **Motor protrusion behind bracket:** ~63–68mm cylindrical body (35.73mm diameter) with a 5mm nub at the very end. Total behind bracket: ~68mm.
4. **Tube exit clearance in front:** ~30–50mm of BPT tube stubs protrude forward.
5. **Wiring clearance at rear:** Motor terminals at the back need ~5mm for solder connections.
6. **Total depth budget:** 116mm from front face to motor nub tip, plus tube stubs in front.
7. **Motor nub:** 5mm protrusion at center of motor end — clears any tray surface.

## Unspecified

1. **Tube connector exit positions:** Exact X/Z positions of the two tube stubs on the front face.
2. **Bracket-to-pump-head attachment:** Whether the bracket separates from the pump head or is fixed.
