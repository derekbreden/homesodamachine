# Strut Joining Technique: Tapered Dovetail Slide with Snap Detent

## Problem

The cartridge mechanism includes two separate flat plates, each with their own struts extending from the rear face. These plates must connect to each other via their struts. Printing both plates as a single monolithic part is significantly harder than printing each plate flat on the bed and joining the struts afterward.

The struts are the joining interface between the two plates.

## Constraints

- **No adhesive, no solvent welding.** Assembly must be purely mechanical — glue adds drying time and assembly pain that is not justified.
- **Permanent assembly.** The joint does not need to come apart for servicing.
- **Strut cross-section is flexible.** There is no requirement for cylindrical struts. Rectangular cross-sections are acceptable and preferred for joint geometry.
- **Material: PETG.** Adequate elongation at break (20-30%) for snap features, low shrinkage (~0.4%), excellent layer adhesion.

## Recommended Technique: Rectangular Struts with Tapered Dovetail + Snap Detent

### Cross-section change: cylindrical to rectangular

Rectangular struts unlock flat-face joinery techniques that are impossible with round cross-sections. A round strut limits options to socket fits and cross-pins. A rectangular strut (8-10 mm wide, 5-8 mm thick) supports dovetails, tongue-and-groove, and snap features — all of which print cleanly as side geometry with no overhangs or supports.

### Joint geometry

One strut ends in a **male dovetail tongue** (trapezoidal cross-section). The mating strut has a **female dovetail channel** that receives it.

```
Male strut (end view):          Female strut (end view):

    ┌────────┐                    ┌──┐      ┌──┐
   ╱          ╲                   │  ╲      ╱  │
  ╱            ╲                  │   ╲    ╱   │
 ╱              ╲                 │    ╲  ╱    │
 │              │                 │     ╲╱     │
 └──────────────┘                 └────────────┘
```

**Key features:**

1. **1-2 degree taper along the sliding axis.** The male tongue is very slightly narrower at the entry end and widens toward its base. This means the joint slides together easily at first, then progressively tightens as it seats — no hammer tap, no force fitting, just a smooth push that firms up at the end.

2. **Snap detent at full insertion.** A small bump on one wall of the male tongue (0.3-0.5 mm proud, ramped on the entry side, steep on the retention side) clicks into a matching pocket in the female channel wall. This locks the sliding axis. Once clicked, the joint cannot back out without destructive force — effectively permanent.

3. **Dovetail angle locks all other axes.** The trapezoidal profile prevents separation perpendicular to the slide direction and prevents rotation. Combined with the snap detent, all six degrees of freedom are constrained.

### Recommended dimensions

These are starting points — print a tolerance test before committing to the real parts.

| Parameter | Value | Notes |
|---|---|---|
| Strut cross-section (rectangular) | 8-10 mm wide, 5-8 mm thick | Beefy enough for reliable dovetail features |
| Dovetail tongue width (narrow end) | 6-8 mm | Well above the 3 mm FDM minimum |
| Dovetail angle | 10-15 degrees per side | Enough interlock without excessive overhang |
| Taper along slide axis | 1-2 degrees | Progressive friction lock over the engagement length |
| Engagement length (overlap) | 15-25 mm | Longer = more taper range = smoother assembly |
| Snap bump height | 0.3-0.5 mm | Enough for an audible click; within PETG strain limits |
| Snap bump ramp angle (entry) | 30-45 degrees | Controls insertion force |
| Snap bump retention angle (rear) | 80-90 degrees | Near-vertical = permanent retention |
| Clearance (per side) | 0.15-0.25 mm | Snug friction fit; calibrate on your printer |
| Leading edge chamfer | 0.5-1.0 mm | Guides insertion, compensates for slight misalignment |

### Print orientation

Both plates print face-down on the build plate. The struts extend vertically (Z direction) from the plate body. The dovetail profile is in the XY plane — this means:

- The dovetail faces are vertical walls (no overhangs, no supports needed)
- Layer lines run along the strut length — maximum strength in the tension direction
- The snap bump is a small horizontal protrusion on a vertical wall — prints cleanly

### Why this beats alternatives

| Alternative | Why not |
|---|---|
| Cylindrical socket joint | Self-aligning in only one axis; can rotate; no snap retention without a cross-pin (additional part) |
| External sleeve | Third part; does not self-align plates to each other; requires glue or screws for retention |
| Scarf joint | Requires adhesive for strength — violates the no-glue constraint |
| Threaded connection | 5-8 mm diameter is below the M8 practical minimum for FDM threads; threads strip with plastic-on-plastic |
| Press fit alone | Risk of cracking the female part; no positive retention; can work loose over time |

### Tolerance calibration

Before printing the real parts, print a single test piece: one male tongue and one female channel, each 25 mm long, at the intended dimensions. Slide them together. The joint should:

- Slide freely for the first 10 mm
- Begin to firm up noticeably over the next 10 mm
- Click (snap detent engages) at full insertion
- Not back out when pulled

If too tight: increase clearance by 0.05 mm per side and reprint. If too loose: decrease clearance. The dovetail tolerance calibration model on Thingiverse (thing:3579313) can also help characterize your printer's behavior before designing the final joint.
