# Beduan Solenoid Valve (2-Way NC, 1/4" QC) — Caliper-Verified Geometry Description

## Purpose of This Document

This document describes the physical geometry of the Beduan 12V DC normally-closed solenoid valve (Amazon B07NWCQJK9) in enough detail that an agent generating engineering drawings or designing a valve rack can model every surface, mounting zone, and interface — without holding the part.

**Reference photographs:** Caliper photos of the physical valve are in `../raw-images/`. Photo numbers referenced throughout this document (e.g., "photo 03") correspond to numbered files in that directory.

## Overall Form

The valve is a **T-shaped assembly** composed of two distinct sub-bodies:

1. **Valve body (white plastic, fluid section):** Contains the diaphragm/poppet mechanism. Has two tube ports (inlet and outlet) with built-in push-to-connect (quick-connect) fittings for 1/4" OD tubing. The white body is **square in cross-section (32.71mm x 32.71mm)** when the collets and push-connect port stubs are excluded. This is the horizontal bar of the T.
2. **Solenoid coil (metal/black-cased, electrical section):** Electromagnetic coil mounted perpendicular to the valve body, rising vertically from the **center** of the white body. This is the vertical stroke of the T. Has two blade-style spade connector terminals protruding from the top. A Chinese product label on the valve body reads "DC12V 0.02-0.8MPa".

The valve has a **2x2 grid of mounting holes** on one face of the white body. The mounting hole grid outer edge-to-edge dimension is **31.41mm** (photo 04).

## Axis and Orientation Convention

Oriented for typical rack mounting (solenoid coil on top, tube ports horizontal):

- **X (width):** Across the valve body, perpendicular to tube flow direction
- **Y (depth):** Along the tube flow direction (port-to-port axis)
- **Z (height):** Vertical — from mounting surface of white body up through solenoid coil to spade connector tips

## Dimensional Profile

```
FRONT VIEW (X-Z plane, looking along tube flow axis Y):

              ╥ ╥  ← spade connectors
        ┌─────╨─╨─────┐
        │    black     │  ← spades protrude 31.41mm
        │    coil      │    from one edge of black body
        │   housing    │
        │              │
   ┌────┴──────────────┴────┐
   │    white valve body     │ ← 32.71mm x 32.71mm square
   │   (2x2 mounting holes) │    (excluding collets/ports)
   └────────────────────────┘

   ▲ 56.04mm from mounting surface to furthest black body edge

SIDE VIEW (Y-Z plane, looking along width axis X):

         ┌───────┐
         │ black │  spade connectors
         │ coil  │  extend this way →  ╤═╤
         │       │                     │ │
    ┌────┴───────┴────┐
    │  white body      │
    ○──────────────────○ ← tube ports (Y axis)

    ◄── 56.00mm collet to collet (Y) ──►
```

### White Valve Body (Fluid Section)
- **Cross-section: 32.71mm x 32.71mm square** (caliper-verified, photo 03; user confirmed square)
- **Collet-to-collet distance (Y): 56.00mm** (caliper-verified, photo 01)
- The top face of the white body has a **raised circular diaphragm boss** — this is where the diaphragm chamber sits internally
- Two cylindrical QC port stubs with collets extend from opposite ends along the Y axis
- **2x2 mounting hole grid** on one face of the white body, with outer edge-to-edge dimension of **31.41mm** (caliper-verified, photo 04)

### Metal/Black Solenoid Coil Housing (Electrical Section)
- Rectangular case containing the electromagnetic coil
- Mounted on top of the valve body at its **center** (creating the T-shape)
- **Distance from white body mounting surface to furthest edge of black body: 56.04mm** (caliper-verified, photo 02)
- **Spade connector terminals:** Two blade-type electrical contacts protruding from the top of the housing. Spade protrusion measured from one edge of the black body to spade tips: **31.41mm** (caliper-verified, photo 05).

### Overall Assembly Envelope
- **Collet-to-collet (Y): 56.00mm** (caliper-verified, photo 01)
- **Mounting surface to black body edge (Z): 56.04mm** (caliper-verified, photo 02)
- **White body edge-to-edge (X and Y cross-section): 32.71mm square** (caliper-verified, photo 03)

## Caliper Measurements Summary

| Photo | Reading | What's Being Measured | Confidence |
|-------|---------|----------------------|------------|
| 01 | 56.00mm | Collet-to-collet distance along tube flow axis (Y) | HIGH (user-verified) |
| 02 | 56.04mm | Mounting surface on white body to furthest edge of black body (Z) | HIGH (user-verified) |
| 03 | 32.71mm | White body edge-to-edge, square cross-section, excluding collets/push-connects | HIGH (user-verified) |
| 04 | 31.41mm | 2x2 mounting hole grid, outermost edge-to-edge | HIGH (user-verified) |
| 05 | 31.41mm | Spade protrusion: one edge of black body to spade tips | HIGH (user-verified) |

## Comparison with Previous Estimates

| Dimension | Previous Estimate | Caliper-Verified | Notes |
|-----------|-------------------|------------------|-------|
| Width (X) | 34.0mm | **32.71mm** (white body, square) | Narrower than estimated; body is square |
| Depth (Y, collet-to-collet) | 63.5mm | **56.00mm** | Significantly shorter than estimated |
| Height (Z, mounting surface to black body edge) | 58.4mm | **56.04mm** | Close to estimate, slightly shorter |

## Mounting Considerations for Valve Rack Design

### 2x2 Mounting Hole Grid
The white valve body has a **2x2 grid of mounting holes** with an outer edge-to-edge dimension of **31.41mm** (photo 04). This provides a direct screw-mounting option.

### T-Shape Profile
The metal solenoid coil is centered on the white body, creating a symmetric T-profile from the front. A cradle must:
1. Support the white valve body from below and on the sides
2. Leave clearance above for the centered solenoid coil to rise vertically
3. Not interfere with tube ports (Y axis access) or spade connectors (top)

### Controlling Dimensions for Rack Slot Sizing
- **Slot width (X):** Must clear 32.71mm white body. Use ~34mm for light clearance.
- **Slot depth (Y):** Must accommodate 56mm collet-to-collet span, plus any additional port stub protrusion.
- **Slot height (Z):** 56.04mm from mounting surface to top of black body, plus spade protrusion above that.

### Port and Electrical Access
- **Tube ports:** Both ends of the Y axis must be accessible for push-to-connect tubing insertion/removal.
- **Spade connectors:** Top of assembly. Protrude 31.41mm from one edge of the black body.

## Geometry for 3D Modeling Agents

When modeling a valve rack cradle:

1. **The valve is T-shaped, not rectangular.** The white body is 32.71mm square (excluding ports/collets).
2. **White body is the primary mounting surface.** It has a 2x2 mounting hole grid (31.41mm edge-to-edge). Design around screw mounting or saddle clamping of the 32.71mm square body.
3. **Solenoid coil protrudes upward from the center** of the white body. 56.04mm from mounting surface to top of black body.
4. **Port stubs with collets protrude along Y.** Collet-to-collet is 56.00mm; port stubs may add length beyond this.
5. **Spade connectors protrude 31.41mm** from one edge of the black body.
6. **The T-profile is symmetric in X.** The valve can be cradled with a centered saddle.

## Remaining Unknowns

1. **Tube port stub OD and protrusion length** — not measured. Needed for tube routing clearance.
2. **Port center axis height** — distance from bottom of white body to the center of the tube ports. Needed for aligning tubes.
3. **Solenoid coil housing exact width and depth** — separate from overall envelope.
4. **Spade connector spacing** — needed for wiring harness design.
5. **Whether the ports are truly inline (coaxial)** — or slightly offset from each other.
6. **Mounting hole diameter and center-to-center spacing** — only edge-to-edge (31.41mm) measured so far.
7. **Diaphragm boss diameter** — visible from top but not measured.
