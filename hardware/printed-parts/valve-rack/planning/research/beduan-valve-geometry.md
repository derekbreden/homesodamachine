# Beduan 12V 1/4" NC Solenoid Valve -- Detailed Geometry

Source: Beduan B07NWCQJK9 (Amazon), product images examined 2026-03-26.
Cross-referenced with caliper-verified dimensions in parts.md and panel-closeup.jpg.

## Coordinate System

Matches parts.md convention:
- **X** = width (left-right when viewing valve from front)
- **Y** = depth (port-to-port / tube flow axis)
- **Z** = height (white body at bottom, spade connectors at top)

## Assembly Overview

T-shaped profile in the Y-Z plane:
- Bottom: white plastic valve body (fluid path), wider in Y due to tube port stubs
- Top: metal solenoid coil housing (gold/zinc-plated steel) rising vertically from center of body
- Very top: black plastic connector housing with 2 spade terminals

## Spade Connector Details

1. **Count**: 2 terminals (+ and - for DC solenoid coil; no polarity requirement per listing)
2. **Terminal type**: Standard 1/4" (6.35mm) male spade / quick-disconnect tabs (accepts standard female spade crimp connectors)
3. **Protrusion direction**: Spade tabs protrude upward (+Z) and slightly toward one Y end, emerging from a black plastic insulator housing at the top of the coil
4. **Tab flat-face orientation**: The flat faces of both spade blades are parallel to the X-Z plane. In other words, the blade width dimension spans the X direction (left-right), and you would slide female spade connectors on/off along the Y axis (the tube flow axis). This is confirmed in Amazon product image 5 (front view showing both tabs edge-on) and image 4 (side view showing tab flat face).
5. **Spacing**: The two tabs are spaced approximately 8-10mm apart in the X direction (center-to-center), side by side. Not yet caliper-verified.
6. **Height**: Black insulator housing sits at top of metal coil; spade tips are at Z ~56mm (total bounding box top). Metal body to spade tips: 36.63mm (caliper-verified, from parts.md).

### Wiring Implication for Valve Rack

Female spade connectors slide on/off along the **Y axis** (front-to-back). In the 5x2 valve rack, this means:
- Wiring access is from the front or rear of the rack (same direction as tubing)
- The ~32.71mm X-pitch between valves does NOT need extra clearance for spade connectors (tabs don't extend in X)
- The 37mm valve pitch (32.71mm body + 4.29mm gap) is adequate for the spade terminal width

## QC Fitting Direction

- Both 1/4" quick-connect tube ports extend along the **Y axis** (depth / front-back)
- One port has a **blue collet ring** (inlet side), the other is plain white (outlet side)
- Port stub OD: standard 1/4" QC for RO tubing (~6.35mm OD tube)
- Tube port stub protrusion: not yet measured (noted as open in parts.md)

## Coil Orientation Relative to QC Fittings

- The metal coil housing sits **centered** on top of the white valve body, roughly at the Y-midpoint between the two tube ports
- The coil is slightly offset from center in X (noted in parts.md as "not perfectly centered")
- The black connector housing with spade terminals is at the **top** of the coil, offset toward one of the Y ends (toward the inlet/blue-ring side based on product images)
- The coil's long axis is vertical (Z), perpendicular to the tube flow axis (Y)

## Valve Orientation in Rack (as specified in parts.md)

- Long axis (port-to-port, 50.84mm) along Y
- Coil housing on top (+Z)
- QC fittings face front (toward cartridge dock) and rear (toward bags)
- Spade connectors at top, accessible from front/rear (Y direction)

## Dimensions Summary

All caliper-verified values from parts.md, repeated here for reference:

| Dimension | Value | Source |
|-----------|-------|--------|
| White body W (X) | 32.71 mm | caliper |
| White body D (Y, port-to-port) | 50.84 mm | caliper |
| White body H (Z) | ~19.4 mm | caliper |
| Metal coil W (X) | 31.41 mm | caliper |
| Metal-to-spade-tip H (Z) | 36.63 mm | caliper |
| Total bounding box | 32.71W x 50.84D x 56.00H mm | caliper |
| With QC fittings | ~32.71W x 68D x 56.00H mm | caliper |
| Spade tab width | ~6.35 mm (standard 1/4") | visual estimate |
| Spade tab spacing (X, c-t-c) | ~8-10 mm | visual estimate, needs caliper |
| Weight | 113 g | measured |

## Still Unverified (Needs Calipers)

- Spade tab center-to-center spacing in X
- Spade tab thickness
- QC port stub protrusion length beyond white body (affects Y clearance in rack)
- Black insulator housing dimensions (W x D x H)
- Exact Y offset of coil/connector housing from body center
