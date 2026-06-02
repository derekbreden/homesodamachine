# John Guest PP1208E / PI1208S / CI1208W 1/4" Bulkhead Union — Geometry

The John Guest 1/4" bulkhead union family — PP1208E (black PP), PI1208S (gray acetal), CI1208W (white acetal): same body, different material/color. A symmetric push-to-connect bulkhead union with a 1/4" (6.35 mm OD) tube collet at each end, for panel-mount through a 0.67" / 17.0 mm hole.

Cert: NSF 51 + NSF 61, FDA-compliant. Max operating pressure 150 psi @ 70 °F.

## Overall Form

A single PP / acetal body with identical push-to-connect collets at each end and a threaded central body between two hex flanges. A separate locknut is supplied loose; it threads onto the central threading and clamps the panel against one flange.

Viewed from the side, the profile is a double barbell: two wider hex flanges (one at each end, ø22.9 mm across the flats) with smaller collet bodies and release rings beyond, connected by a narrower threaded shaft in the middle.

The panel sits between the locknut and one flange. The flange face on the panel side carries an O-ring and forms the seal. Because the body is symmetric, the two ends are interchangeable; which is "wet" (syrup side) and which is "dry" (outside) is an install-orientation choice, not a part-geometry distinction.

## Axis Convention

- **Long axis (L):** Axis of tube flow, running through the centers of both collets and the threaded central body. All length / z dimensions are along this axis.
- **Radial (R):** Perpendicular to L. The body is rotationally symmetric about L — every feature described as a diameter is a circle concentric to L.

## Dimensional Profile — Zones Along the Long Axis

```
   ┌────┐   ┌─────────┐                            ┌─────────┐  ┌────┐
   │REL.│   │  HEX    │   ┌────────────────────┐   │  HEX    │  │REL.│
   │RING│ ─ │ FLANGE  │ ─ │     THREADING      │ ─ │ FLANGE  │ ─│RING│
   │ ø10│   │  ø22.9  │   │       ø ≤ 17       │   │  ø22.9  │  │ ø10│
   │3.5 │   │  8.5    │   │        10          │   │  8.5    │  │3.5 │
   └────┘   └─────────┘   └────────────────────┘   └─────────┘  └────┘
   ◄──────────────────── 34.5 mm overall ──────────────────────────►
```

The body has three unique zones (release ring, hex flange, threading), mirrored about the center. Overall length 34.5 mm.

### Zone 1 & 5: Release Ring (each end)
- **OD: 9.57 mm.**
- **Length: 3.5 mm.**
- Houses the push-to-release sleeve and the spring-steel gripper teeth that retain a 1/4" OD tube.
- The end face is the tube push-in port, ø6.35 mm (1/4" tube OD).

### Zone 2 & 4: Hex Flange (each end)
- **OD: 22.9 mm** across the wrench flats of the hex (the hex is faceted, not circular).
- **Length: 8.5 mm.**
- The face toward the threading is the panel-seating face, carrying an O-ring that provides the seal.
- Wrench flats let an installer hold the body while torquing the locknut.

### Zone 3: Threading (middle)
- **OD: ≤ 17 mm** — threading major diameter, matching the 0.67" / 17.0 mm mounting hole.
- **Length: 10 mm** — the span between the two flanges.
- The locknut threads on this section from the dry side; the panel sits on this threading on the wet side of the locknut.

## Locknut (Separate Piece, Shipped Loose)

- **OD: ~18 mm** — between the 17 mm threading and the 22.9 mm flange.
- **Thickness: ~5 mm.**
- Hex-faceted. Material varies by SKU (PP on some, plated metal on others). Its position along the threading depends on panel thickness.

## Dimension Table

The values below correspond to the constants in `hardware/printed-parts/cold-core/reservoir/reservoir.py`.

| Constant | Value (mm) | Feature |
|----------|-----------|---------|
| `bulkhead_pocket_diameter` | 23.0 | ø22.9 flange + 0.1 mm clearance |
| `bulkhead_panel_hole_diameter` | 17.0 | Mounting hole (0.67") |
| `bulkhead_total_length` | 34.5 | Overall length (1.36") |
| `bulkhead_wet_chamber_length` | 12.0 | Wet collet section |
| `bulkhead_flange_length` | 8.5 | Hex flange |
| `bulkhead_release_ring_length` | 3.5 | Release ring |
| `bulkhead_panel_thickness` | 5.0 | PETG panel; threading is 10 mm, panel takes ≤ ~9 mm to leave threading for the locknut |
| `bulkhead_threading_length` | 10.0 | Body section between the two flanges; supports the locknut |
| `bulkhead_dry_chamber_length` | 17.0 | Locknut (~5 mm) + dry collet section (~12 mm) |
| `bulkhead_locknut_diameter` | 18.0 | Locknut OD |
| `bulkhead_locknut_thickness` | 5.0 | Locknut thickness |
| `bulkhead_release_ring_diameter` | 9.57 | Release ring OD |

## Catalog Cross-Reference

| Dimension | Value |
|---|---|
| Overall length | 1.36" / 34.5 mm |
| Flange / envelope max OD | 0.90" / 22.9 mm |
| Mounting hole | 0.67" / 17.0 mm |
| Tube OD | 1/4" / 6.35 mm |
| Max operating pressure | 150 psi @ 70 °F |
| Cert | NSF 51 + NSF 61, FDA-compliant |
