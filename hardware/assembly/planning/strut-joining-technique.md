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

2. **Snap detent at full insertion.** Locks the sliding axis so the joint cannot back out. See the Detent Mechanism section below for the specific approach.

3. **Dovetail angle locks all other axes.** The trapezoidal profile prevents separation perpendicular to the slide direction and prevents rotation. Combined with the snap detent, all six degrees of freedom are constrained.

## Detent Mechanism: How to Lock the Slide

The detent — the "last click" — is the part most 3D printing designers skip or solve with a screw through the side. PrusaSlicer's dovetail cut mode, for example, generates a pure friction-fit slide with no locking feature at all. This section documents what the community actually does and what we should use.

### What others do (community survey)

**1. Integrated cantilever flex arm with barb (most mechanically sound).** One wall of the female dovetail channel includes a short cantilever beam that protrudes slightly into the channel. The beam has a barb/hook at its tip. As the male tongue slides in, the barb rides up a shallow ramp on the tongue, deflects outward, then snaps into a matching recess or behind a ledge at end of travel. This is the most robust approach for FDM.

**2. Bump detent (simplest).** A small raised bump on the male tongue rides against the channel wall. The channel wall or the tongue itself flexes just enough for the bump to pass, then the bump seats behind a ridge or in a pocket. The sliding part IS the flex element. Common for thin sliding lids, less reliable for thick rigid struts unless there is enough wall flex.

**3. Prong-and-blind-recess barbs (permanent lock).** Two small prongs with triangular barbs that snap into blind pockets at end of travel. Cannot be released without breaking or external tool access. This is a one-way insertion — appropriate for our permanent assembly constraint.

**4. Compliant detent beam.** A flexible beam running parallel to the slide direction, pressing against notches in the rail. Good for multi-position stops but overkill for a single end-of-travel lock.

**5. openscad-slide-n-snap library.** A parametric OpenSCAD module specifically for this problem (github.com/benjamin-edward-morgan/openscad-slide-n-snap). The female part has a living spring and latch that snaps the male part at full insertion. Parameters include thickness, width, gap, clearance, length, height, spring dimension, and angle. Worth studying as a reference for dimensioning.

### Recommended approach for this project: prong barbs into blind recesses

Given our constraints (permanent, no glue, PETG, beefy struts), prong-and-blind-recess barbs are the best fit:

- **Permanent by geometry.** The barbs snap into blind pockets that have no external access — the joint physically cannot release without breaking material. This matches our "never needs to come apart" constraint.
- **No sustained deflection.** Unlike a bump detent where the flex element is always slightly loaded (leading to creep over time), the barbs snap fully into their recesses and sit at rest with zero stored strain. No creep, no relaxation, no loss of retention over time.
- **Simple print geometry.** Two small prongs on the male tongue, two blind pockets in the female channel wall. The prongs print as vertical features (layers along their length). The pockets are simple rectangular voids.

```
Side view of detent engagement (sliding direction is horizontal):

Before:                          After (locked):

  Male tongue sliding →            Male tongue seated
  ┌──────────╱╲──────┐            ┌──────────┐┌──────┐
  │          ╱  ╲    │            │          ││ barb │
  │    barb ╱    ╲   │            │          ││ in   │
  └────────╱──────╲──┘            └──────────┘│pocket│
           ╱        ╲                         └──────┘
  ────────╱──────────╲────        ────────────┘
  Female channel wall             Female channel wall
  (pocket behind wall)            (barb seated in pocket)
```

### Detent design parameters

| Parameter | Value | Notes |
|---|---|---|
| Prong count | 2 (one per side of tongue) | Symmetric loading; redundancy |
| Prong width | 2-3 mm | Wide enough to print cleanly; narrow enough to flex |
| Prong length (cantilever) | 6-10 mm | Longer = less strain at root = more durable |
| Prong thickness | 1.0-1.5 mm | Must flex ~0.3-0.5 mm without cracking |
| Barb height (protrusion) | 0.3-0.5 mm | Controls insertion force and retention strength |
| Barb entry ramp angle | 30-40 degrees | Shallow ramp = lower insertion force |
| Barb retention face angle | 90 degrees (vertical) | Permanent retention — cannot climb back over |
| Blind pocket depth | barb height + 0.2 mm clearance | Barb must seat fully with no residual strain |
| Blind pocket width | prong width + 0.3 mm clearance | Must not bind on pocket walls |
| Fillet at prong root | 0.5-0.75 mm radius minimum | Prevents crack initiation at the stress riser |

### Critical print orientation for flex prongs

The prongs MUST be printed so deflection occurs within layers (XY plane), not across layer boundaries. If the prongs deflect across layers, they will delaminate on the first insertion — sudden, catastrophic failure. For our geometry (struts extending vertically from the plate, dovetail profile in XY), the prongs are vertical features with their flex direction in XY. This is correct — layers run along the prong length, flex is in-plane.

### Failure modes to watch for

| Failure Mode | Cause | Prevention |
|---|---|---|
| Crack at prong root | Missing fillet, sharp corner | Fillet >= 0.5x prong base thickness |
| Layer delamination | Flex across layer lines | Orient flex in XY plane, never Z |
| Creep / loss of retention | Barb held in deflected state | Use blind recess so barb seats fully at rest |
| Permanent lock unintended | Elephant's foot or ooze on barb | Test piece first; slight chamfer on barb tip |
| Tolerance stack-up | Slide too tight + detent friction | Tune slide clearance and detent independently |

### Key sources

- Fictiv: "How to Design Snap-Fit Components" — strain formulas, taper guidance, fillet rules
- Core77: "How to Design Snap-Fit Components" — entry vs. retention angle, permanent vs. releasable
- Hubs/Protolabs: "Interlocking Joints" — prong-and-recess barb geometry
- openscad-slide-n-snap (GitHub: benjamin-edward-morgan) — parametric reference implementation
- Printables model 261593: sliding lid box with bump detent — practical FDM example

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
