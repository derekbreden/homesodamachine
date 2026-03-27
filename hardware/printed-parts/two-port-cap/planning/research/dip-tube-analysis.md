# Dip Tube Analysis — Two-Port Cap Architecture

How the two-port cap design (main fluid port + dip tube air bleed port) enables filling, dispensing, and priming of the Platypus 2L bags in the soda flavor injector system. This document supersedes all previous single-tube-through-cap analysis.

---

## Table of Contents

1. [Two-Port Cap Design](#1-two-port-cap-design)
2. [Fluid Operations](#2-fluid-operations)
3. [Air Management and Priming](#3-air-management-and-priming)
4. [Why Two Ports Are Necessary](#4-why-two-ports-are-necessary)
5. [Dip Tube and Tip Piece](#5-dip-tube-and-tip-piece)
6. [Bag Collapse Behavior](#6-bag-collapse-behavior)
7. [Hydrostatic Pressure and Seal Integrity](#7-hydrostatic-pressure-and-seal-integrity)
8. [John Guest Bulkhead Fittings](#8-john-guest-bulkhead-fittings)
9. [Flow Dynamics](#9-flow-dynamics)
10. [Clean Cycle](#10-clean-cycle)
11. [Bill of Materials Impact](#11-bill-of-materials-impact)
12. [Conclusions](#12-conclusions)

---

## 1. Two-Port Cap Design

### 1a. Architecture Overview

Each Platypus 2L bag uses a modified 28mm threaded cap that holds two 1/4" John Guest quick-connect bulkhead fittings. The two ports serve distinct functions:

```
    CAP CROSS-SECTION (viewed from inside the bag):

              28mm threaded cap
         ┌──────────────────────┐
         │                      │
         │   ┌──┐      ┌──┐    │
         │   │P1│      │P2│    │
         │   │  │      │  │    │
         │   └──┘      └──┘    │
         │  bottom    dip tube  │
         │  port      port      │
         └──────────────────────┘

    P1 = Bottom port (main fluid line)
    P2 = Dip tube port (air bleed line)

    Both are 1/4" John Guest quick-connect bulkhead unions
    (part number PP1208W or equivalent)
```

### 1b. Port Functions

| Port | Name | Internal Geometry | External Connection | Primary Function |
|---|---|---|---|---|
| P1 (bottom) | Main fluid port | Short stub or flush with cap interior | Connects to pump inlet (dispense) or pump outlet (fill) via valve routing | Liquid in/out |
| P2 (dip tube) | Air bleed port | 1/4" hard tube runs full length of bag to sealed end | Connects to pump for air evacuation during prime | Air removal |

### 1c. Why the Bottom Port Is Flush or Short

The bottom port (P1) does not need a long tube into the bag. The bag is mounted at a 35-degree diagonal with the connector end at the lowest point. Liquid naturally pools at this low point due to gravity. A short stub (5-10mm) or a flush-mounted fitting provides direct access to the deepest liquid pool.

```
    SIDE VIEW: Bag on 35-degree diagonal

    back wall
    │
    │   sealed end (pinned to wall, highest point)
    │  ╱═══════════════════════════╲
    │ ╱                             ╲
    │╱      LIQUID pools here        ╲
    │       at the low point ──────→  ╲
    │                                  ╲
         ╚════════════════════╤══╤═════╝
                              │P1│P2│  ← cap at bottom-front
                              └──┴──┘
                                │  │
                           to valves/pump
```

Liquid always collects at P1. No dip tube needed on this port.

### 1d. Why the Dip Tube Runs to the Top

Air rises. In a bag mounted at 35 degrees, air migrates to the highest point -- the sealed end pinned to the back wall. The dip tube (P2) extends from the cap all the way up to this apex so the pump can reach and evacuate trapped air during the prime cycle.

---

## 2. Fluid Operations

### 2a. Dispensing (Bag to Faucet)

During normal dispensing, the peristaltic pump pulls concentrate from the bag through the bottom port (P1) and pushes it to the faucet dispensing line. The dip tube port (P2) is isolated (its solenoid valve is closed).

```
    DISPENSE MODE:

    Valve state:
      P1 line: bag-to-pump valve OPEN, pump-to-faucet valve OPEN
      P2 line: CLOSED (air bleed not needed)

    Flow path:
      Bag interior (liquid at bottom)
        → P1 (bottom port, flush with cap)
          → 1/4" tubing to valve manifold
            → peristaltic pump
              → dispensing line to faucet

    Bag behavior:
      As liquid is removed, the bag collapses.
      Atmospheric pressure pushes the flexible bag walls inward.
      No air enters the bag -- the system is sealed.
      The bag behaves like a bag-in-box wine container.
```

The bottom port is ideal for dispensing because liquid gravity-pools at the connector. The pump draws from the deepest point, achieving near-complete evacuation. The only liquid that cannot be dispensed is whatever thin film remains on the bag walls after collapse -- estimated at 5-15 ml on a 2L bag (~0.5% loss).

### 2b. Filling (Hopper to Bag)

During filling, the pump pulls concentrate from the hopper funnel and pushes it into the bag through the bottom port (P1). The dip tube port (P2) may be opened to vent displaced air (see Section 3).

```
    FILL MODE:

    Valve state:
      P1 line: hopper-to-pump valve OPEN, pump-to-bag valve OPEN
      P2 line: OPEN (to vent displaced air) or CLOSED (to trap air)

    Flow path:
      Hopper funnel
        → hopper solenoid valve
          → peristaltic pump (forward)
            → 1/4" tubing
              → P1 (bottom port)
                → bag interior

    Inside the bag:
      Liquid enters at the lowest point.
      Liquid level rises from bottom to top as the bag fills.
      Air is displaced upward (toward sealed end).
```

With the bottom port as the fill entry, liquid enters at the lowest point and rises naturally. This is the optimal fill geometry -- no counter-flow problem. Air is displaced upward away from the incoming liquid rather than fighting through the same port.

### 2c. Filling Air Displacement

As concentrate enters through P1, air is pushed upward and collects at the sealed end (highest point). Two strategies for dealing with this air:

**Strategy A: Vent through dip tube (P2) during fill**

Open the P2 valve during filling. As air is displaced upward, it reaches the dip tube tip piece at the top of the bag and can exit through the dip tube, through the P2 valve, and out to atmosphere (or into a catch container). This allows the bag to fill completely with minimal trapped air.

```
    AIR VENTING DURING FILL:

    ╔════════════════════════════╗
    ║   air ──→ tip piece ──→   ║  ← air exits through
    ║          [═══◉═══]        ║     dip tube (P2)
    ║            │              ║
    ║            │ dip tube     ║
    ║            │              ║
    ║  LIQUID  ←─── rising ──→  ║
    ║              level        ║
    ║                           ║
    ╚════╤══╤═══════════════════╝
         │P1│P2│
         └──┴──┘
          ↑   ↓
        fill  air out
```

**Strategy B: Accept trapped air, prime after fill**

Fill with P2 closed. Some air remains trapped at the top. After filling, run a prime cycle (Section 3) to evacuate the remaining air. This is simpler (fewer simultaneous valve operations) but wastes a small amount of concentrate during the prime-to-waste step.

**Recommended: Strategy A** -- vent through P2 during fill. This takes full advantage of the two-port architecture and minimizes post-fill priming.

---

## 3. Air Management and Priming

### 3a. The Air Problem

After initial bag installation (or after a fill cycle), air is trapped inside the bag. Air at the top of the bag is harmless during dispensing (the pump draws liquid from the bottom port). But air anywhere in the tubing lines between the bag and the faucet causes sputtering and inconsistent flavor dosing.

The prime cycle evacuates air from:
1. The tubing between the bag and the pump
2. The tubing between the pump and the faucet
3. Any air pockets inside the bag that could migrate to the bottom port

### 3b. Prime Cycle — Air Evacuation Through the Dip Tube

The prime cycle uses the dip tube (P2) to suck air out of the bag from the highest point:

```
    PRIME CYCLE:

    Step 1: Evacuate air from the bag via dip tube

    Valve state:
      P2 line: dip-tube-to-pump valve OPEN
      P1 line: CLOSED (isolate main fluid path)
      Pump waste valve: OPEN (to drain/waste container)

    Flow:
      Pump creates suction on P2 line
        → suction propagates through dip tube
          → dip tube tip piece collects air at bag apex
            → air is pulled DOWN through dip tube
              → through pump → to waste

    What exits:
      First: air (the target)
      Then: a small amount of concentrate (indicating air is cleared)

    ╔════════════════════════════╗
    ║   AIR pocket at top       ║
    ║          [═══◉═══]        ║  ← tip piece collects air
    ║            │ ↓            ║     from across bag width
    ║            │ ↓ air pulled ║
    ║            │ ↓ down tube  ║
    ║                           ║
    ║        LIQUID             ║
    ╚════╤══╤═══════════════════╝
         │P1│P2│
         └──┘ │
              ↓ air + small amount of liquid to waste


    Step 2: Prime the dispensing line

    Valve state:
      P1 line: bag-to-pump OPEN, pump-to-faucet OPEN
      P2 line: CLOSED

    Flow:
      Pump pulls concentrate from bag through P1
        → pushes through dispensing line to faucet
        → air in the dispensing line is pushed out the faucet end

    After step 2, the entire fluid path from bag to faucet
    is filled with concentrate. System is primed.
```

### 3c. Why This Works

The dip tube tip piece (see [dip-tube-tip-design.md](dip-tube-tip-design.md)) spans the full width of the bag at the highest point. Its surface ribs create air channels that prevent the bag film from sealing flat against the bar. Air from anywhere across the bag width can migrate laterally along these channels to the central tube socket, where it enters the dip tube bore and gets pulled down to the pump.

After the prime cycle, the air pocket at the top of the bag is reduced to a thin residual layer -- the amount that cannot be pulled past the liquid meniscus at the tip piece. This residual air is harmless: it stays at the top of the bag, never reaches the bottom port during dispensing, and slightly reduces effective bag volume by a few milliliters.

### 3d. Air Volume Estimates

| Source | Volume | Notes |
|---|---|---|
| Air in empty bag (initial install) | ~2000 ml | Full bag volume; mostly displaced during fill |
| Residual air after filling (P2 vented) | ~20-50 ml | Thin pocket at apex that did not reach tip piece |
| Residual air after filling (P2 closed) | ~100-200 ml | Compressed air at apex |
| Air in dip tube (P2, unfilled) | ~5 ml | 6.35mm bore x ~160mm active length |
| Air in P1 tubing (unfilled) | ~4 ml | Tubing from cap to pump |
| Air in dispensing line | ~3 ml | Tubing from pump to faucet |
| **Total air to prime (worst case)** | **~210 ml** | New bag install, P2-closed fill |
| **Total air to prime (best case)** | **~30 ml** | P2-vented fill, only line air |

At 400 ml/min pump rate, priming the worst case takes ~30 seconds. Best case takes ~5 seconds. The pump is less efficient with air than liquid (peristaltic pumps compress air rather than displacing it cleanly), so actual times are roughly 2x these estimates.

### 3e. Freshness and Sealed System

Between uses, all valves are closed (NC solenoids de-energize to closed state). The bag interior is completely isolated from atmosphere:

- No air exchange through P1 (valve closed)
- No air exchange through P2 (valve closed)
- The bag film is impermeable (nylon/PE laminate)
- Concentrate is never exposed to ambient oxygen

This sealed-vessel behavior preserves concentrate freshness for weeks -- comparable to bag-in-box wine or commercial syrup bag systems.

---

## 4. Why Two Ports Are Necessary

### 4a. The Single-Port Problem

With only one port (P1 at the bottom), priming is fundamentally limited:

```
    SINGLE PORT — CANNOT REACH AIR:

    ╔════════════════════════════╗
    ║   AIR trapped here        ║  ← air at top
    ║                           ║     no way to reach it
    ║                           ║
    ║                           ║
    ║        LIQUID             ║  ← liquid at bottom
    ║                           ║
    ╚═══════════╤══╤════════════╝
                │P1│  ← single port at bottom
                └──┘
                 │
            pump can only suck liquid from here
```

The pump connected to P1 can only access what is at the bottom of the bag -- which is liquid. The air is trapped at the top with no path to the pump. The pump would need to remove ALL the liquid before it could reach the air, which defeats the purpose.

Inverting the bag (connector at top) would put the air at the port, but then liquid pools at the bottom away from the port -- the pump cannot efficiently dispense.

A single port cannot optimize for both dispensing (port at bottom) and air removal (port at top). The two-port design solves this by putting one port at each location.

### 4b. The Two-Port Solution

```
    TWO PORTS — EACH OPTIMIZED FOR ITS FUNCTION:

    ╔════════════════════════════╗
    ║   AIR ──→ [tip piece] ──→ ║  ← P2 reaches air at top
    ║            │              ║
    ║            │ dip tube     ║
    ║            │              ║
    ║        LIQUID             ║  ← P1 reaches liquid at bottom
    ║                           ║
    ╚════╤══╤═══════════════════╝
         │P1│P2│
         └──┴──┘
          │   │
     liquid  air
     out     out

    P1 at bottom: optimized for liquid (dispensing + filling)
    P2 at top (via dip tube): optimized for air (priming)
```

Each port serves one job:
- **P1**: All liquid operations (dispense, fill). Positioned at the gravity low point. Short path, high flow rate.
- **P2**: Air evacuation only (prime cycle, fill venting). Positioned at the gravity high point via the dip tube. Used briefly during prime, then closed.

### 4c. Comparison

| Capability | Single Port | Two Port |
|---|---|---|
| Dispense from bottom | Yes | Yes (P1) |
| Fill from bottom | Yes | Yes (P1) |
| Remove air from top | No | Yes (P2 + dip tube) |
| Vent air during fill | No | Yes (P2 open during fill) |
| Full prime (no trapped air) | Impossible without draining bag | Yes (prime through P2) |
| Sealed idle state | Yes (1 valve) | Yes (2 valves, both NC) |
| Additional valves needed | 0 | 2 (for P2 routing) |
| Additional parts in cap | 0 | 1 bulkhead fitting + dip tube + tip piece |

The two additional valves per bag (for P2 routing) bring the total valve count from 4 per pump to 6 per pump, 12 total for the two-line system. This is the main cost of the two-port architecture. However, the Beduan 12V NC solenoid valves are $8.99 each, so the incremental cost is ~$36 for all four additional valves.

---

## 5. Dip Tube and Tip Piece

### 5a. Dip Tube Construction

The dip tube is a length of 1/4" (6.35mm OD) hard polyethylene or polyurethane tube. It is NOT the Platypus Drink Tube Kit -- that product is no longer needed. The dip tube is simply a cut length of the same hard tube stock used elsewhere in the system for John Guest push-to-connect plumbing.

| Parameter | Value |
|---|---|
| Material | Hard polyethylene or polyurethane |
| Outer diameter | 6.35mm (1/4") |
| Inner diameter | ~4.0-4.3mm (standard wall) |
| Length | Cut to reach from cap bulkhead to bag apex (~280-320mm depending on bag mount geometry) |
| Bottom end | Inserts into P2 John Guest bulkhead fitting (push-to-connect) |
| Top end | Inserts into tip piece central socket (friction or barb fit) |

### 5b. Tip Piece

The 3D-printed tip piece is detailed in [dip-tube-tip-design.md](dip-tube-tip-design.md). Summary:

- Spans full bag width (~185mm)
- Assembled through 28mm opening via ship-in-a-bottle technique (insert lengthwise, rotate 90 degrees)
- Central socket grips 6.35mm OD tube
- Air channel ribs on top and bottom faces prevent bag film seal-off
- Wedges between side seams to prevent lateral movement
- Material: PETG (FDM prototype) or PA12 nylon (SLS production), with food-safe coating
- Only fluid-contact 3D-printed part in the system

### 5c. Internal Assembly

```
    INSIDE THE BAG (longitudinal section):

    sealed end (top, pinned to back wall)
    ┌──────────────────────────────────┐
    │  rib  rib  [◉ socket]  rib  rib │  ← tip piece (185mm wide)
    │              │                   │
    │              │  1/4" hard tube   │
    │              │  (dip tube)       │
    │              │                   │
    │              │                   │
    │              │                   │
    │              │                   │
    └──────────────┤──╤────────────────┘
                   │P2│  ← bulkhead fitting in cap
                   └──┘
    connector end (bottom-front)
```

The tube runs straight from the P2 bulkhead fitting up to the tip piece. The tip piece's socket grips the tube. The bag's diagonal mount keeps the tube under light tension (the tip piece is at the high end, the cap is at the low end). The cradle supports the bag from underneath, and the sealed end is pinned to the back wall, so there is no significant force trying to pull the tube out of the socket.

---

## 6. Bag Collapse Behavior

### 6a. During Dispensing

As liquid is pulled from the bag through P1, the bag volume decreases. Since the system is sealed (both valves closed except the active dispense path), atmospheric pressure pushes the bag walls inward. The bag collapses progressively:

1. The bag film first separates from the cradle support surfaces (sides and top)
2. Film drapes inward toward the remaining liquid pool at the bottom
3. The dip tube and tip piece provide internal structure that prevents complete collapse in the top region
4. The tip piece ribs maintain air channels even as the film contacts the bar
5. As the bag empties, the film may wrap around the dip tube, but the tube's rigidity (6.35mm OD hard PE) maintains an open channel along its length

### 6b. Dip Tube as Internal Spine

The 6.35mm hard tube running the full length of the bag acts as a structural spine:

```
    CROSS-SECTION: Collapsed bag around dip tube

    ───────────────────────────────
    │            bag wall         │
    │     ┌──── dip tube ────┐   │
    │     │   (6.35mm OD,    │   │  ← tube prevents
    │     │    rigid PE)     │   │     complete pinch
    │     └──────────────────┘   │     at this location
    │            bag wall         │
    ───────────────────────────────
```

Even when the bag is nearly empty, the tube holds the bag walls ~6.35mm apart along its length. This is significant: it creates a guaranteed minimum flow channel from the liquid pool (bottom) to the tip piece (top), ensuring the prime cycle can always reach trapped air.

### 6c. Tip Piece at Collapse

When the bag is very empty, the film collapses onto the tip piece. The ribs (1.5mm tall, see dip-tube-tip-design.md Section 6) hold the film off the bar surface, maintaining air channels. The film tension across the ribs depends on:

- How much residual liquid weight is pressing the film down (very little at the top of the incline)
- Atmospheric pressure differential (only relevant during active pumping; at rest, pressure equalizes)
- Film stiffness (Platypus nylon/PE laminate is moderately stiff)

With the sealed end pinned to the back wall and supported by the cradle, the film pressure against the tip piece is minimal. The 1.5mm ribs are more than adequate to maintain air channels.

### 6d. Failure Mode: Film Occlusion of P1

The bottom port (P1) is flush with the cap interior or has a very short stub. When the bag is nearly empty, the collapsed film can drape over and seal the port opening. This is the same "bag pinch" phenomenon described in earlier research.

Mitigation:
- The short stub (5-10mm) on P1 holds the film away from the actual port bore
- The film must conform to the cap interior geometry, which includes two protruding bulkhead fittings; the complex surface prevents a clean seal
- If occlusion occurs, it is intermittent (pump suction briefly lifts the film, draws a slug of liquid, film re-seals, pump pulls again -- pulsating but functional)
- At very low bag volume (<5%), some sputtering is expected and acceptable; the system warns the user to refill

---

## 7. Hydrostatic Pressure and Seal Integrity

### 7a. Pressure at the Cap

The bag is mounted at 35 degrees with the cap at the lowest point. The hydrostatic pressure at the cap depends on the liquid column height above it.

For a full 2L bag on a 35-degree incline:
- Bag length along the incline: ~350mm
- Vertical height of liquid column: 350mm x sin(35 deg) = ~200mm
- Liquid density: ~1050 kg/m^3 (sugar syrup)
- Hydrostatic pressure: 200mm x 1050 x 9.81 = 2.06 kPa = **0.30 PSI**

This is trivially low. The John Guest bulkhead fittings are rated for 150 PSI. The O-ring seals in the bulkhead fittings are not challenged by 0.3 PSI.

### 7b. Pressure During Pump Operations

The Kamoer peristaltic pump generates:
- Suction (dispensing): ~3-5 PSI vacuum at the bag port
- Pressure (filling): ~3-5 PSI positive at the bag port

Both are well within the 150 PSI rating of the John Guest fittings. The modified cap itself (polypropylene with two drilled holes for the bulkhead fittings) must withstand these pressures, but at 3-5 PSI the stresses are negligible for a solid PP cap.

### 7c. Cap Seal to Bag

The Platypus 2L bag uses a 28mm threaded opening. The cap threads onto this opening with a gasket or O-ring seal. This seal is designed for the original Platypus system (hydration use) and is rated for the mild pressures of sucking through a bite valve.

With the two-port modification, the cap is the original Platypus cap (or a custom replacement) with two holes drilled for the bulkhead fittings. The cap-to-bag thread seal is unchanged and remains adequate -- the 0.3 PSI hydrostatic head and 3-5 PSI pump pressure are within the original design envelope.

### 7d. Bulkhead-to-Cap Seal

Each John Guest PP1208W bulkhead fitting requires a 5/8" (15.9mm) mounting hole. The fitting passes through the hole and is secured with a locknut on the other side. An O-ring on the bulkhead body seals against the cap material.

Two 15.9mm holes in a 28mm cap leaves limited material between the holes and between the holes and the cap thread. The minimum wall thickness between the two holes and from each hole to the cap edge must be assessed:

```
    CAP FACE (28mm thread OD, ~24mm usable diameter inside thread):

         24mm usable
    ┌────────────────────┐
    │                    │
    │   (P1)     (P2)   │   Two 15.9mm holes
    │   15.9mm   15.9mm │   in a ~24mm diameter
    │                    │
    └────────────────────┘

    Problem: 15.9 + 15.9 = 31.8mm > 24mm
    Two full-size bulkhead holes DO NOT FIT side by side
    in a standard 28mm Platypus cap.
```

**This is a critical dimensional conflict.** Two PP1208W bulkhead fittings (each requiring a 15.9mm hole) cannot both fit within the ~24mm usable diameter of a standard 28mm Platypus cap. The combined hole requirement (31.8mm) exceeds the available space.

### 7e. Resolution: Custom Cap

The 28mm Platypus cap cannot accommodate two standard John Guest bulkhead fittings. Solutions:

**Option A: Custom 3D-printed cap with smaller bulkhead penetrations**

Design a custom cap with a 28mm thread that has a taller body, allowing the two fittings to be stacked vertically (axially offset along the cap height) rather than side by side. Each fitting gets its own cross-section of the cap wall.

```
    CUSTOM CAP (side view):

    ┌────────────────┐
    │  P2 bulkhead   │  ← upper fitting
    │  ┌──┐          │
    ├──┤  ├──────────┤  ← wall between fittings
    │  └──┘          │
    │  P1 bulkhead   │  ← lower fitting
    │  ┌──┐          │
    └──┤  ├──────────┘
       └──┘
    ───28mm thread───
```

**Option B: Smaller fittings**

Use smaller push-to-connect fittings that require a smaller mounting hole. Some brands offer 1/4" tube fittings with a 3/8" (9.5mm) or 7/16" (11.1mm) panel hole. Two 9.5mm holes side by side = 19mm, which fits within the 24mm usable diameter with 2.5mm of wall between them and 2.5mm to each edge.

**Option C: Custom cap with barb fittings instead of John Guest**

Instead of push-to-connect bulkheads, use simple barb fittings molded or epoxied into the cap. A barb fitting for 1/4" tube has a ~7-8mm OD shank. Two barbs side by side need ~16mm, which fits within 24mm.

**Option D: One bulkhead + one barb**

Use a John Guest bulkhead for P1 (the main fluid port, where tool-free tube disconnection is valuable for bag changes) and a permanently installed barb fitting for P2 (the dip tube port, which is internal and rarely disconnected).

**Recommended: Option D** for Phase 1. The P1 port benefits from quick-connect for bag changes. The P2 port connects to an internal dip tube that is assembled once per bag and does not need to be disconnected frequently. A barb fitting with a small footprint for P2 keeps the cap dimensions workable while preserving quick-connect convenience on the main fluid line.

If a fully custom cap is pursued (Option A), the cap can be 3D printed in food-safe PETG or PP with the 28mm thread and whatever internal geometry is needed to hold both fittings.

---

## 8. John Guest Bulkhead Fittings

### 8a. Part Numbers

| Part Number | Description | Tube Size | Material | Hole Size | Max Pressure | Standards |
|---|---|---|---|---|---|---|
| PP1208W | Bulkhead union, polypropylene, white | 1/4" OD | Polypropylene body, nitrile O-ring | 5/8" (15.9mm) | 150 PSI | NSF/ANSI 51, NSF/ANSI 61 |
| PI1208S | Bulkhead union, acetal, grey | 1/4" OD | Acetal body, nitrile O-ring | 5/8" (15.9mm) | 150 PSI | NSF/ANSI 51, NSF/ANSI 61 |
| PP121208W | Reducing bulkhead, 3/8" to 1/4" | 3/8" x 1/4" OD | Polypropylene | -- | 150 PSI | NSF/ANSI 51, NSF/ANSI 61 |

### 8b. PP1208W Specifications

- Push-to-connect on both sides (tube pushes in, collet grips, O-ring seals)
- Panel/wall thickness range: approximately 1.5-6mm (determined by thread engagement and locknut reach)
- Both NSF/ANSI 51 (food equipment materials) and NSF/ANSI 61 (drinking water components) certified
- Operating temperature: up to 150F (65C) -- well above the 15-25C operating range
- Nitrile O-rings are compatible with sugar syrups and weak acids (pH 3-4)

### 8c. Availability and Cost

| Source | Part | Price | Notes |
|---|---|---|---|
| Amazon (10-pack) | PP1208W | ~$20-25 for 10 | B003YKF1SY |
| Home Depot (10-pack) | PP1208W-US | ~$20-25 | SKU 335236458 |
| Zoro / McMaster | PP1208W | ~$3-5 each | Single units available |
| US Water Systems | PP1208W | ~$3-4 each | Specializes in water filtration fittings |

For two bags x one bulkhead each (P1 only, with barb for P2) = 2 fittings needed. A 10-pack provides spares for future bags.

---

## 9. Flow Dynamics

### 9a. Dispensing Flow Path

```
    Bag interior → P1 (flush port) → 1/4" tube → valve → pump → valve → dispensing line → faucet
```

| Segment | ID | Length | Cross-Section | Flow Resistance (relative) |
|---|---|---|---|---|
| P1 bulkhead bore | ~6mm | 15mm | 28.3 mm^2 | Negligible |
| 1/4" tube (bag to valve) | ~4mm | ~200mm | 12.6 mm^2 | Low |
| Solenoid valve bore | ~4mm | ~20mm | 12.6 mm^2 | Low |
| Pump tubing (peristaltic) | 3.175mm | ~100mm | 7.9 mm^2 | Moderate (bottleneck) |
| Dispensing line | 3.175mm | ~1000mm | 7.9 mm^2 | Highest |

The peristaltic pump tubing (silicone, 1/8" ID) and the dispensing line are the flow bottlenecks. The bag port and connecting tubing contribute minimal resistance. The pump rate (400 ml/min) is the governing flow rate, not the plumbing resistance.

### 9b. Filling Flow Path

```
    Hopper → valve → pump → valve → 1/4" tube → P1 (flush port) → bag interior
```

Same tubing diameters and resistances as dispensing, but flow direction is reversed through the pump. The peristaltic pump is bidirectional (L298N H-bridge). Fill rate is limited by the pump rate (~400 ml/min) and the hopper drainage rate (gravity-limited if the hopper runs dry before the pump).

Fill time for 2L at 400 ml/min: **~5 minutes** (pump-limited). This is a significant improvement over the gravity-fill estimates in previous research (8-30 minutes) because the pump provides positive pressure.

### 9c. Dead Volume

| Segment | Volume | Notes |
|---|---|---|
| P1 bulkhead + short stub | ~0.5 ml | Negligible |
| Tubing between bag and pump | ~3 ml | ~200mm of 1/4" tube |
| Dip tube (P2, inside bag) | ~5 ml | ~280mm of 1/4" tube |
| P2 external tubing | ~2 ml | ~150mm of 1/4" tube |
| **Total dead volume** | **~10.5 ml** | 0.5% of 2L bag capacity |

Dead volume is liquid that remains in the plumbing after operations complete. It is negligible relative to bag capacity. During cleaning, 2-3 flush cycles dilute dead-volume residue to immeasurable levels.

---

## 10. Clean Cycle

### 10a. Clean Fill

The clean cycle pushes clean water through the bag to flush residual concentrate. With the two-port architecture:

```
    CLEAN FILL:

    Water source → pump (or house pressure via needle valve)
      → P1 (into bag at bottom)
        → water rises in bag, dissolving residual syrup
          → P2 open: air exits through dip tube as water fills

    The bottom-entry fill ensures water contacts the entire
    bag interior surface as it rises from bottom to top.
```

### 10b. Clean Flush

After filling with water, the pump pulls the rinse water out:

```
    CLEAN FLUSH (via P1):

    Bag interior (rinse water + dissolved syrup)
      → P1 → pump → to waste/drain

    This pulls the dirtiest water (concentrated at the bottom
    where syrup residue is heaviest) out first.
```

Optionally, also flush through P2:

```
    CLEAN FLUSH (via P2):

    Bag interior (top region, near tip piece)
      → dip tube → P2 → pump → to waste

    This flushes the top of the bag where the tip piece sits,
    cleaning the 3D-printed part.
```

### 10c. Cycle Count

Three fill-flush cycles reduce syrup concentration by ~1000x (assuming 10ml dead volume mixing with 2000ml clean water each cycle). After 3 cycles, residual syrup is undetectable by taste.

---

## 11. Bill of Materials Impact

### 11a. Parts No Longer Needed

| Part | Reason Removed |
|---|---|
| Platypus Hydration Drink Tube Kit (B07N1T6LNW, $24.95) | The dip tube is now a cut length of 1/4" hard tube, not the Platypus drink tube product. No bite valve, no blue PU tube, no sleeve joints. |

### 11b. New Parts

| Part | Qty per Bag | Qty Total (2 bags) | Est. Cost Each | Est. Total |
|---|---|---|---|---|
| John Guest PP1208W bulkhead (for P1) | 1 | 2 | ~$3 | ~$6 |
| Barb fitting for P2 (1/4" tube, ~8mm shank) | 1 | 2 | ~$2 | ~$4 |
| 1/4" hard PE tube (dip tube, ~300mm per bag) | 1 | 2 | ~$1 | ~$2 |
| 3D-printed tip piece | 1 | 2 | ~$2 (FDM+coating) | ~$4 |
| Additional NC solenoid valves (P2 routing) | 2 | 4 | ~$9 | ~$36 |
| Food-safe epoxy coating (shared) | -- | 1 bottle | ~$15 | ~$15 |
| Custom cap (3D printed or modified) | 1 | 2 | ~$3 | ~$6 |

### 11c. Net Cost Change

| Item | Change |
|---|---|
| Removed: Platypus Drink Tube Kit x2 | -$49.90 |
| Added: Bulkheads, barbs, tube, tips, valves, caps, epoxy | +$73.00 |
| **Net increase** | **+$23.10** |

The main cost driver is the four additional solenoid valves ($36). All other new parts total ~$37. The Drink Tube Kit elimination saves ~$50. Net increase is modest and well worth the priming capability.

---

## 12. Conclusions

### 12a. What the Two-Port Architecture Enables

1. **True air evacuation**: The dip tube reaches trapped air at the bag apex, allowing complete priming without draining the bag.

2. **Efficient filling**: Pump-assisted fill through the bottom port (P1) at 400 ml/min. Air vents through the dip tube (P2) during fill. Fill time for 2L: ~5 minutes.

3. **Optimal dispensing**: Bottom port (P1) at the gravity low point gives near-complete bag evacuation with no dip tube in the dispensing path.

4. **Sealed freshness**: Both ports sealed by NC solenoid valves between uses. No atmospheric exposure.

5. **Effective cleaning**: Bottom-entry water fill rises through the entire bag. Flush from both ports cleans all regions including the tip piece.

### 12b. Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Cap modification | One JG bulkhead (P1) + one barb fitting (P2) | Two full bulkheads do not fit in 28mm cap |
| Dip tube material | 1/4" hard PE tube (not Platypus kit) | Simpler, cheaper, compatible with JG fittings |
| Tip piece | 3D-printed air collection bar, 185mm span | See dip-tube-tip-design.md |
| Fill strategy | Pump-assisted through P1, air vents through P2 | Fast (~5 min for 2L), no counter-flow problem |
| Prime strategy | Pump suction on P2 dip tube, then pump through P1 to faucet | Two-step prime clears all air from all paths |
| Valve count | 6 per pump line (4 for P1 routing + 2 for P2 routing) | 12 total for 2-line system |

### 12c. Open Issues

1. **Custom cap design**: The standard Platypus cap cannot hold two PP1208W bulkheads. A custom cap (3D printed or machined) with one bulkhead + one barb is needed. Detailed cap design is a follow-on task.

2. **Valve routing for P2**: The existing valve architecture (valve-architecture.md) describes 4 valves per pump line for P1 routing. Two additional valves per line are needed for P2 (one to connect P2 to pump suction during prime, one to vent P2 to atmosphere during fill). The valve architecture document needs updating.

3. **Tip piece validation**: The tip piece design (dip-tube-tip-design.md) needs physical prototyping to validate air channel effectiveness, tube socket grip, and ship-in-a-bottle assembly feasibility.

4. **Dip tube length per bag**: The exact tube length from cap bulkhead to tip piece socket depends on the final mount geometry. Measure on the actual diagonal mount and cut to fit with ~5mm excess (the excess inserts deeper into the socket).
