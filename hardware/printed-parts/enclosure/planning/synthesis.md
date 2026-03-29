# Enclosure Design Execution Plan: Snap-Fit Two-Part Architecture

**Date:** 2026-03-29
**Document Status:** Ready for CAD implementation and test print validation
**Synthesis Scope:** Requirements + Vision + Design Patterns Research + Platypus Bag Profile Research + Snap-Fit Design Research

---

## Executive Summary

The soda flavor injector enclosure is a **220 × 300 × 400 mm consumer appliance** printed in two halves and permanently sealed with snap-fit joinery. The user experiences a unified, rigid, premium product—not a collection of parts. All interior components (bags, pumps, valves, electronics, displays) snap-mount to the two outer halves with no visible fasteners or assembly artifacts.

The seam is visible and intentional. It is refined through:
- **1.2 mm gap width** with **±0.1–0.2 mm tolerance** (consistent, readable as design element)
- **10 snap points** spaced ~100 mm apart (tight cosmetic seam, distributed stress)
- **Matte black finish** (minimizes light reflection, hides gap shadows)
- **2–3 mm edge fillets** on all external edges (premium, safe tactile feel)
- **0.5–1.0 mm recess channel** along the seam (creates intentional shadow line)

The enclosure is oriented with **front-to-back seam running horizontally** at the widest point (300 mm depth), splitting the 400 mm height into two approximately equal halves. This seam placement aligns with the 35-degree bag orientation and creates an optical balance point that feels inevitable rather than arbitrary.

---

## 1. Design Patterns Integration: From Research to Execution

### 1.1 Premium Unified Product — Design Pattern Synthesis

The design-patterns.md research identified three key principles for consumer appliances:

1. **Gap uniformity > absolute gap width** — A perfectly consistent 1.2 mm gap reads more premium than an irregular 0.5 mm gap
2. **Matte finish conceals seams** — Diffuse reflection prevents light concentration at the seam
3. **Seam as intentional design element** — Premium products accept visible seams and refine them rather than attempt to hide them

**Execution approach:**
- Target 1.2 mm seam gap at all 1040 mm of perimeter (±0.1–0.2 mm tolerance)
- Matte black finish post-print (paint or powder coat recommended)
- 0.5–1.0 mm recessed channel along the seam (creates shadow line that reframes gap as deliberate visual break)
- Snap-fit joinery with 10 points distributed around perimeter (controls closure tightness and cosmetic consistency)

### 1.2 Tactile Confirmation — Snap-Fit Feedback

The design-patterns research found that users expect tactile and audible confirmation of permanent closure. Unlike appliances that must appear fully seamless (HomePod), the soda flavor injector benefits from the user feeling and hearing the snap-fit assemble.

**Execution approach:**
- 10 snap points with equilateral triangle or bullnose hook profiles (smooth stress distribution, durable)
- Each snap shall produce audible click (~40–50 N per snap)
- Total assembly force ~400–500 N (distributed; achievable by technician with light hand pressure)
- User perceives permanent, rigid closure through tactile feedback at every snap

---

## 2. Enclosure Geometry and Seam Placement

### 2.1 Overall Dimensions and Seam Location

**Outer envelope:** 220 mm (W) × 300 mm (D) × 400 mm (H)

**Seam placement:** Horizontal centerline at 200 mm height, running around the entire 1040 mm perimeter.

```
                      ← 220 mm →
                    ┌─────────────┐
                    │ TOP HALF    │ ↑
                    │             │ │ 200 mm
         ▲          │─────────────│ ↓
         │          │             │ ← SEAM (1.2mm gap)
       400 mm       │ BOTTOM HALF │ ↑
         │          │             │ │ 200 mm
         ▼          │             │ ↓
                    └─────────────┘
                    ← 300 mm depth →
```

**Rationale:**
- **Horizontal seam at 50% height** creates visual balance and optical centerline (golden ratio principle)
- **Seam at widest perimeter (300 mm depth × 220 mm width = 1040 mm total)** distributes snap loading evenly
- **Seam coincides with the 35-degree bag orientation vector** — bags run diagonally from back-bottom to front-top; the seam at 200 mm height intercepts this plane naturally, making the seam placement feel inevitable rather than arbitrary
- **Front-to-back orientation (not left-right)** allows easier internal component access during assembly and enables clean entry/exit of tubing through back wall

### 2.2 Seam Gap Specification

| Parameter | Specification | Rationale |
|-----------|---|---|
| **Gap width** | 1.2 mm nominal | Premium appliance standard; readable as intentional design line |
| **Gap tolerance** | ±0.1–0.2 mm | Achievable with FDM (Bambu H2C calibrated); <0.2 mm variation imperceptible |
| **Gap uniformity** | Consistent along entire 1040 mm perimeter | Gap consistency more critical than absolute width for premium perception |
| **Seam recess** | 0.5–1.0 mm inset from outer surface | Creates shadow line that reframes seam as design feature; optical break avoids "cheap gap" appearance |
| **Recess channel depth** | 1.0–1.5 mm total | Deep enough to be visually perceived but not so deep as to create sharp internal edges |

### 2.3 Edge Treatment and Surface Finish

**External edges (all exposed edges):**
- **Fillet radius:** 2–3 mm minimum (premium appliance standard; prevents sharp, cheap-feeling edges)
- **Seam corners:** 3–4 mm radius (where horizontal seam meets vertical side walls)
- **Justification:** Research confirms fillets >2 mm improve premium perception; sharp corners read as unfinished

**Surface finish:**
- **Color:** Matte black (20–40% gloss per ASTM D523)
- **Application:** Paint or powder coat post-print (achieves uniform finish across snap-fit seams)
- **Avoid:** Glossy finishes (magnify seam visibility via specular highlights; industry research shows matte outperforms glossy)

**Seam edge profile (external seam line):**
```
     Matte finish
           ↓
    ════════════  ← Outer surface (primary)
    ║   0.5-1.0   ║ ← Recess channel (shadow effect)
    ║    mm       ║
    ║   inset     ║
    ════════════  ← Secondary surface (inside recess)
           ↓
      45° × 0.5mm chamfer (softens visual transition)
```

---

## 3. Internal Architecture: Component Mounting Strategy

All interior components mount to the two outer halves via snap-fit connectors. No screws, glue, or fasteners visible on external surfaces.

### 3.1 Bag Cradles and Constraint Surfaces (Platypus Bag Integration)

**Position in enclosure:**
- Two bags mounted diagonally, one above the other
- Orientation: 35 degrees from horizontal, cap end at back-bottom, top folded flat against front wall
- Vertical envelope: bags occupy top ~60 mm of enclosure (below the seam and displays)

**Cradle geometry (from platypus-bag-profile.md research):**
- **Support cradle (bottom):** Lens-shaped profile, 190 mm wide × 80–100 mm deep (front-to-back), 2 mm minimum thickness, smooth surface
- **Constraint surface (top):** Identical lens-shaped profile, 25–30 mm above cradle, 2–3 mm thickness for rigidity

**Mounting strategy:**
- **Support cradles:** Two separate lens-shaped platforms snap to the **bottom inner surfaces** of both top and bottom halves (one cradle each)
  - Positioned to support the bag's natural lens shape without deformation
  - Snap points (4 per cradle) on the inner walls of the halves

- **Constraint surfaces:** Two identical lens-shaped covers snap to the **front interior frame** (internal web spanning top-to-bottom)
  - Positioned directly above each cradle, 25–30 mm up
  - Snap points (4 per constraint) to internal vertical ribs
  - Constraint surfaces hold bags in 25–30 mm height range across all fill levels (prevents unconstrained rise to 40 mm)

**Height specification (constrained):**
- Fully filled (2.0L): 26–28 mm
- Partially filled (1.0L): 24–26 mm
- Critically low (0.5L): 23–25 mm
- **Total vertical space allocated:** 30 mm (bags + constraint), leaving clearance for interior geometry

**Tolerances:**
- Cradle-to-bag: 0–2 mm clearance (bag rests snugly)
- Constraint-to-bag: 0 mm (direct contact)
- Cradle to constraint (bag height): 25–30 mm

---

### 3.2 Funnel and Liquid Sensing

**Position:** Directly above bags, on top surface of enclosure, front edge

**Description:**
- Funnel geometry receives user's pour of SodaStream syrup
- Capacitive liquid sensor detects presence of liquid in tubing below funnel
- Funnel mounts via snap points (2–3) to internal frame

**Snap mounting points:** 2 snap anchors on top-interior walls

---

### 3.3 Pump Cartridge Mounting

**Position:** Front-bottom of enclosure, below displays and air switch

**Description:**
- Removable pump cartridge (2 peristaltic pumps + quick-connect mechanism + release plate)
- Pumps mount via 4 screws to a flat mounting surface inside the cartridge
- Cartridge docks into a snap-fitted cradle inside the enclosure

**Snap mounting points:** Cradle has 4 snap points (corners) connecting to internal walls; cartridge is hand-removable by squeezing release mechanism (user-facing squeeze surfaces on front of cartridge)

**Thermal and pressure considerations:**
- Mounting surface must be rigid (1.5 mm wall minimum)
- Cartridge pressure from pumps: <1 bar; snap mounting is sufficient
- No hydraulic pressure between cartridge and enclosure (pumps sit on shelf, not compressed against wall)

---

### 3.4 Valve Rack

**Position:** Behind pump cartridge, mid-front of enclosure

**Description:**
- Manifold with 10 solenoid valves (3/4 total: 2 flavor select, 2 water inlet, 2 air inlet, 1 outlet for each flavor, 2 drain)
- Valves control flow paths: funnel-to-bag, bag-to-dispense, clean cycle, air injection
- Mounts to a flat panel via snap points

**Snap mounting points:** 6–8 snap anchors around the valve rack perimeter

---

### 3.5 Displays and Air Switch (Detachable Front Panel)

**Position:** Front face, center, below bags

**Description:**
- **RP2040 small display:** 0.99" round LCD, flush-mounted in front panel
- **S3 large display (optional):** 1.28" rotary display, flush-mounted in front panel
- **KRAUS air switch:** Mechanical momentary switch, flush-mounted
- All three are **snapped into front panel slots and can be removed and remounted**, with retracting 1–2 m Cat6 cable (user-detachable but connected)

**Snap mounting strategy:**
- 3 separate snap-fit frames (one for RP2040, one for S3, one for air switch)
- Each frame provides 4 snap anchors (corners) to the front interior frame
- Frames are removable; cables stored in cable channels along the back interior
- When displays are detached, mounting frames remain in the enclosure (user can mount displays elsewhere)

---

### 3.6 Electronics Mounting

**Position:** Back-top of enclosure

**Description:**
- ESP32 development board (main controller)
- L298N motor driver (pump control)
- Power supply (12V or equivalent)
- Connector pads for tubing quick-connects

**Snap mounting strategy:**
- PCB standoff mounts via snap-fit clips (4 corners)
- No screws visible on external surfaces

---

### 3.7 Back Wall Integration: Inlet/Outlet Ports

**Position:** Rear face of enclosure (back panel)

**Description:**
- **Cold water inlet:** 1/4" barb or quick-connect (from external carbonator: Lillium, Brio)
- **Cold water outlet:** 1/4" barb or quick-connect (to faucet)
- **Tap water inlet (clean cycle):** 1/4" barb or quick-connect
- **Flavor outlet #1:** 1/4" barb or quick-connect (flavor A to faucet)
- **Flavor outlet #2:** 1/4" barb or quick-connect (flavor B to faucet)

**Mounting:** Barbed ports press into 1/4" openings in back panel (wall thickness 1.5 mm min); ports are designed with friction fit or use internal barb/snap to secure.

**Quick-connect standard:** John Guest 1/4" push-to-connect (field-standard in appliances)

---

## 4. Snap-Fit Configuration

### 4.1 Snap Point Distribution

**Total perimeter:** 1040 mm (220 mm × 2 + 300 mm × 2)

**Number of snap points:** 10 (selected from snap-fit-design.md guidance)

**Spacing strategy:**
- **Corner snaps:** 1 snap at each of 4 inside corners (these corners experience stress concentration and benefit from over-constraint)
- **Edge snaps:**
  - 300 mm depth edges (front/back): 2 snaps per edge (1 snap at midpoint = 150 mm from each corner, 150 mm from other corner)
  - 220 mm width edges (left/right): 1 snap per edge (at midpoint = 110 mm from each corner)

**Snap layout (top view of seam perimeter):**
```
      ← 220 mm →
    [Snap] [Snap]            Front face
    ┌───────────┐
    │ S       S │
[S] │           │ [S]  ← 300 mm
    │ S       S │
    └───────────┘
      [Snap]           Back face
    [Snap] [Snap]

Total: 4 corners + 4 edge midpoints + 2 edge single-snaps = 10 snaps
Spacing: ~100 mm nominal (80–150 mm range acceptable)
```

### 4.2 Snap-Fit Hook Geometry

**Hook profile type:** Equilateral triangle or bullnose (smooth stress distribution, best for permanent closure)

**Cantilever beam dimensions:**
| Parameter | Value | Unit |
|---|---|---|
| Beam length | 20 mm | mm |
| Beam thickness (base) | 1.2 mm | mm |
| Beam thickness (tapered toward tip) | 0.8–1.0 mm | mm |
| Beam width | 6–8 mm | mm |
| Hook overhang height | 2.5 mm | mm |
| Hook lead-in angle | 25° | degrees |
| Fillet radius at beam base | 0.8 mm | mm |
| Undercut depth (female half) | 2.8 mm | mm |
| Draft angle on hook | 6° | degrees |

**Why this geometry:**
- 20 mm beam length: achieves 40–50 N per-snap assembly force (comfortable for technician, distributed across 10 snaps)
- 1.2 mm base + 0.8 mm tip taper: reduces stress concentration while maintaining stiffness
- 0.8 mm fillet radius: reduces stress concentration factor from ~2.0 to ~1.3 (critical for permanent closure durability)
- Equilateral triangle profile: symmetrical stress distribution (better fatigue life than asymmetric right-triangle)
- 25° lead-in angle: reduces assembly force and improves tolerance for misalignment

### 4.3 Assembly Force and Seating

**Per-snap assembly force:** 40–50 N (achievable by technician pushing steadily with thumb)

**Total mating force (10 snaps):** 400–500 N (distributed; no single point overloaded)

**Snap seating confirmation:**
- Audible click at each snap engagement
- Tactile feedback (spring resistance) as hook engages undercut
- User presses halves together; as load approaches 400–500 N, all 10 snaps seat simultaneously (or near-simultaneously)

**After assembly:**
- Snap seating resistance: >80 N per snap (prevents accidental disassembly; permanent closure feel)
- No rocking or play between halves (snap undercuts are fully engaged)

---

## 5. Detailed Component Mounting Points

All interior components have **explicit snap anchor points** on the two outer halves.

### 5.1 Mounting Point Inventory

| Component | Snap Anchor Count | Location (Top/Bottom Halves) | Purpose |
|---|---|---|---|
| **Bag Cradle #1** | 4 | Bottom half interior surface | Support bag A |
| **Bag Cradle #2** | 4 | Bottom half interior surface | Support bag B |
| **Constraint #1** | 4 | Front interior vertical frame | Hold bag A height (25–30 mm) |
| **Constraint #2** | 4 | Front interior vertical frame | Hold bag B height (25–30 mm) |
| **Funnel** | 2–3 | Top exterior edge, front | Mount funnel at highest point |
| **Pump cartridge cradle** | 4 | Front interior, lower | Dock removable pump cartridge |
| **Valve manifold** | 6–8 | Front interior, mid | Mount valve rack to frame |
| **Display RP2040 frame** | 4 | Front interior, mid | Mount small display (detachable) |
| **Display S3 frame (optional)** | 4 | Front interior, mid | Mount large display (detachable) |
| **Air switch frame** | 4 | Front interior, mid | Mount air switch (detachable) |
| **PCB standoff #1** | 4 | Top-back interior | Mount main controller |
| **Cable channel clips** | 8–10 | Interior frame edges | Route and secure tubing/cables |

**Total snap mounting anchors:** ~56–64 dedicated snap points (distinct from the 10 permanent-closure snaps at the seam)

---

## 6. Structural Ribs and Internal Framing

To achieve the 1.5 mm enclosure wall thickness while maintaining rigidity across 300 mm spans (front-to-back depth), the interior includes **vertical and horizontal ribs.**

### 6.1 Rib Structure

**Vertical ribs (front-to-back internal walls):**
- Run the full height of the enclosure (400 mm)
- Thickness: 1.0 mm
- Spacing: 100–150 mm apart (distribute bending loads)
- Locations: Behind displays/switches, behind pump cartridge, behind valve manifold, at side edges

**Horizontal ribs (internal shelves):**
- Connect vertical ribs at key heights
- Thickness: 1.0 mm
- Key heights:
  - 25 mm above bottom: bag cradle support level
  - 60 mm above bottom: bag constraint upper edge
  - 100 mm above bottom: pump cartridge mounting surface
  - 150 mm above bottom: valve manifold base
  - 200 mm height: seam plane (no horizontal rib here; this is where the two halves join)
  - 250 mm above bottom: displays/air switch mounting frame base
  - 350 mm above bottom: electronics mounting level

**Rationale:**
- Vertical and horizontal ribs create a **lattice structure** inside the enclosure
- This lattice provides snap anchor points for all components
- Ribs prevent wall deflection under internal stresses (bag weight, liquid pressure, valve operation)
- Ribs remain invisible externally; only smooth outer walls visible

---

## 7. Print Orientation and Support Strategy

### 7.1 Half 1 (Top Portion) — Print Orientation

**Dimensions:** ~220 × 300 × 200 mm (fits within Bambu H2C single-nozzle envelope of 325 × 320 × 320 mm)

**Orientation on build plate:**
- **Seam face:** Horizontal, pointing down toward build plate (Z-axis)
- **Snap arm orientation:** Cantilever beams flex in the XY-plane (parallel to build plate)
- **Rationale:** Snap arms are weakest in the Z-direction (perpendicular to layer lines); printing with flex direction in XY-plane maximizes strength

**Support strategy:**
- Snap hooks (undercut geometry on bottom half of Top portion): Intentional support structure with 0.2 mm interface gap and break-away ribs (0.3 mm wide, spaced 5 mm)
- Snap undercuts (concave features): Break-away ribs or 0.2 mm gap beneath undercut surface
- Internal ribs: No supports (geometry oriented to avoid overhangs)
- Overhang rule: No unsupported faces <45° from horizontal

---

### 7.2 Half 2 (Bottom Portion) — Print Orientation

**Dimensions:** ~220 × 300 × 200 mm

**Orientation on build plate:**
- **Seam face:** Horizontal, pointing down toward build plate (Z-axis)
- **Snap arm orientation:** Cantilever beams flex in the XY-plane
- **Rationale:** Same as Top half; consistency in print orientation

**Support strategy:**
- Identical to Top half
- Snap hooks and undercuts designed with intentional support geometry

---

### 7.3 Support Removal and Post-Print Cleanup

**Break-away ribs:**
- 0.3 mm × 0.8 mm ribs spaced every 5 mm along snap hook perimeter
- Interface gap: 0.2 mm between rib and part surface
- Removal: Hand-snapped by bending the rib away from the part; leaves minimal surface damage (<0.1 mm)

**Snap undercuts:**
- Horizontal snap hooks (if any) print with no supports
- Vertical snap hooks use break-away ribs as above
- Surface finish post-removal: Light sanding (220–400 grit) to smooth any rib traces

---

## 8. Material and Finish Specification

### 8.1 Material Selection

**Primary material:** Nylon (PA12)

**Rationale:**
- Highest fatigue resistance (10,000+ cycles; permanent closure needs margin even though no disassembly cycles expected)
- Excellent moisture stability (kitchen appliance; potential for condensation)
- Superior ductility (handles assembly stresses without brittle failure)
- Food-safe when filled (regulatory alignment for water/syrup contact)

**Secondary material:** PETG (acceptable fallback)

**Rationale:**
- Good all-around properties
- Slightly lower fatigue resistance (500–1000 cycles)
- Excellent chemical resistance
- Lower cost than Nylon
- **Use PETG if Nylon experiences supply issues or print failures**

**Avoid:** PLA
- Brittle at cold temperatures (enclosure may sit in cool environments)
- Poor moisture resistance (kitchen humidity)
- Inadequate fatigue life for snap-fit design

### 8.2 Post-Print Finish Treatment

**Step 1: Support removal**
- Break away ribs by hand or light tool pressure
- Sand any remaining support traces lightly (220 grit)

**Step 2: Surface preparation**
- Wash both halves in warm soapy water (remove dust and residue from printing)
- Dry completely
- Light sanding (220–400 grit) to smooth layer marks and improve finish uniformity

**Step 3: Paint/finish application**
- Apply matte black paint or powder coat (20–40% gloss per ASTM D523)
- Multiple thin coats preferred over single thick coat (reduces run/drip)
- Cure/dry fully before assembly

**Why matte black:**
- Minimizes seam visibility via diffuse reflection (research confirmed)
- Hides minor surface variations from printing
- Premium appliance standard (matches market expectations)
- Visually conceals gap shadows

---

## 9. Dimensional Specifications Summary

### 9.1 Overall Enclosure

| Dimension | Specification | Tolerance |
|---|---|---|
| **Width** | 220 mm | ±1.0 mm |
| **Depth** | 300 mm | ±1.0 mm |
| **Height** | 400 mm | ±1.0 mm |
| **Wall thickness (external)** | 1.5 mm | ±0.1 mm |
| **Seam gap** | 1.2 mm | ±0.1–0.2 mm |
| **Seam recess depth** | 0.75 mm | ±0.25 mm |
| **Edge fillet radius** | 2.5–3.0 mm | — |

### 9.2 Bag Cradle and Constraint Geometry

| Component | Dimension | Specification | Tolerance |
|---|---|---|---|
| **Lens width** | — | 190 mm | ±1.0 mm |
| **Lens depth (front-to-back)** | — | 85–95 mm | ±2.0 mm |
| **Cradle thickness** | — | 2.0 mm | ±0.2 mm |
| **Constraint thickness** | — | 2.5–3.0 mm | ±0.3 mm |
| **Cradle-to-constraint height** | — | 25–30 mm | ±1.0 mm |
| **Constraint surface fillet** | — | R ≥ 10 mm (edges) | — |

### 9.3 Snap-Fit Dimensions (per snap point)

| Parameter | Specification | Tolerance |
|---|---|---|
| **Cantilever length** | 20 mm | ±0.5 mm |
| **Base thickness** | 1.2 mm | ±0.05 mm |
| **Tip thickness** | 0.8 mm | ±0.05 mm |
| **Beam width** | 6–8 mm | ±0.2 mm |
| **Fillet radius (base)** | 0.8 mm | ±0.1 mm |
| **Hook overhang** | 2.5 mm | ±0.1 mm |
| **Lead-in angle** | 25° | ±2° |
| **Undercut depth** | 2.8 mm | ±0.1 mm |

---

## 10. Bill of Materials (Printed Parts Only)

### 10.1 Top Half Enclosure

| Item | Description | Material | Weight Est. | Critical Dims |
|---|---|---|---|---|
| **Top half shell** | Upper half of enclosure (front, back, sides) | Nylon (PA12) | ~350–400 g | 220×300×200 mm |
| **Internal ribs** | Vertical and horizontal lattice for rigidity and snap anchors | Nylon (PA12) | Included above | 1.0 mm walls |
| **Snap hooks** | 5 cantilever beam snap hooks (for seam engagement with bottom half) | Nylon (PA12) | ~10 g | 20×6–8×1.2–0.8 mm each |
| **Mounting frame** | Front interior vertical frame for display/switch/component mounting | Nylon (PA12) | ~50–75 g | ~300×200×2 mm |

**Top half total weight:** ~410–485 g (raw print, pre-paint)

**Paint/finish weight addition:** ~20–30 g (thin matte coat)

### 10.2 Bottom Half Enclosure

| Item | Description | Material | Weight Est. | Critical Dims |
|---|---|---|---|---|
| **Bottom half shell** | Lower half of enclosure (front, back, sides) | Nylon (PA12) | ~350–400 g | 220×300×200 mm |
| **Internal ribs** | Vertical and horizontal lattice | Nylon (PA12) | Included above | 1.0 mm walls |
| **Snap undercuts** | 5 concave undercut features (for seam engagement) | Nylon (PA12) | ~5 g | 2.8 mm deep |
| **Cradle bases** | Two lens-shaped support platforms for bags | Nylon (PA12) | ~30–40 g | 190×85–95×2 mm each |
| **Internal frame elements** | Shelves and ribs for component mounting | Nylon (PA12) | Included above | Various |

**Bottom half total weight:** ~410–485 g (raw print, pre-paint)

**Paint/finish weight addition:** ~20–30 g

### 10.3 Mounted Components (NOT included in enclosure BOM)

The following are **already specified in requirements.md and vision.md** and are mounted via snap points inside the enclosure. They are listed here for reference only:

- Platypus 2L collapsible bottles (2×, provided by user)
- Kamoer peristaltic pumps (2×, in removable cartridge)
- Beduan solenoid valves (10×)
- L298N motor driver (1×)
- ESP32-DevKitC-32E (1×)
- Displays: RP2040 round LCD + S3 rotary (user selects which to mount)
- KRAUS air switch (1×)
- Silicone tubing, quick-connects, mounting hardware (per other BOMs)

---

## 11. Seam Appearance and Premium Feel Validation

### 11.1 Design Decisions Supporting Premium Perception

1. **Seam placement at 50% height:** Creates optical balance and aligns with bag geometry (intentional, not arbitrary)

2. **1.2 mm gap + matte finish:** Gap is visible as thin line; matte prevents light reflection emphasis; research confirms consistency >absolute width

3. **Recess channel (0.5–1.0 mm inset):** Shadow line reframes gap as design element; eliminates "sloppy gap" perception

4. **10 snap points at ~100 mm spacing:** Distributes closure load evenly; prevents bulging or micro-gaps between snaps

5. **2.5–3.0 mm edge fillets:** Premium, safe, never sharp; contrasts with cheap sharp corners

6. **Snap feedback (audible click, tactile resistance):** Users perceive permanence and quality through assembly experience

7. **No visible fasteners or assembly artifacts:** All snaps and mounting points hidden internally

### 11.2 Prototype Validation Checklist

When the first enclosure halves print, verify:

- [ ] **Visual seam at eye level:** Gap reads as thin, uniform line (not sloppy or variable)
- [ ] **Visual seam at 35° angle:** Gap remains consistent in appearance when viewed diagonally
- [ ] **Recess shadow effect:** Shadow line visible and reads as intentional design break
- [ ] **Tactile seam:** Fingertip running along seam feels smooth, consistent step, no sharp edges
- [ ] **Snap engagement:** All 10 snaps click audibly and seat simultaneously (or near-simultaneously)
- [ ] **Snap tightness:** No rocking or play between halves after assembly
- [ ] **Seam gap measurement:** Feeler gauge at 10 points around perimeter; variation <0.2 mm
- [ ] **Enclosure rigidity:** <0.5 mm deflection under 10 N corner load (test with dial indicator)
- [ ] **Interior component fit:** Bags, pumps, valves snap into place without force; alignment perfect

**If any check fails:**
- Gap consistency issue → check printer calibration; adjust part orientation if needed
- Snap weakness → increase engagement depth or beam width (if geometry allows)
- Visual recess poor → apply the 0.5–1 mm recess channel for shadow effect (may require CAD iteration)
- Rigidity insufficient → add internal ribs or increase wall thickness from 1.5 to 1.8 mm

---

## 12. Conflicts, Constraints, and Resolutions

### 12.1 Potential Conflict: Seam Visibility vs. Seamless Appearance

**Conflict statement:** The vision document emphasizes premium "unified" feel, but permanent two-piece closure inherently shows a visible seam.

**Resolution:** Research (design-patterns.md) proves that **visible seams are acceptable** in premium appliances (Instant Pot, refrigerators) when refined through:
- Perfect gap uniformity (1.2 mm ±0.1–0.2 mm)
- Matte finish (diffuse reflection hides gap shadows)
- Intentional design element framing (recess channel, clean geometry)

**No redesign required.** The seam will be visible and intentional; it will read as premium through consistency and refinement, not through attempted concealment.

---

### 12.2 Potential Conflict: Snap Assembly Force vs. Permanent Closure

**Conflict statement:** 400–500 N total mating force is "high" for a consumer appliance; users should not need tools or excessive hand strength.

**Resolution:** The snap force is distributed across 10 points (40–50 N per snap). Assembly requires:
- Two hands (one holding top half, one pushing bottom half)
- Steady pressure (not sudden force)
- Light tool assistance (small rubber mallet) if desired
- Achievable by any adult without risk of injury

**This is acceptable for a permanent closure.** The user assembles once; field technicians can use tools if necessary. No conflict with user experience.

---

### 12.3 Potential Conflict: Bag Height Constraint (25–30 mm) vs. Enclosure Compactness

**Conflict statement:** Platypus bag unconstrained height reaches 40 mm at full fill. Constraint reduces to 25–30 mm. This is a 10–15 mm reduction; adding another bag above doubles the space required (50–60 mm minimum for two bags).

**Resolution:** Vision document already specifies this configuration: **"bags are each supported by their own lens shaped platform and are constrained from above identically, such that they remain at 25mm–30mm"** and "bags are mounted one above the other, diagonally."

The enclosure is 400 mm tall; allocating 60 mm for two constrained bags leaves 340 mm for all other components (pumps, valves, electronics, displays). This is sufficient.

**No conflict. Design is feasible as specified.**

---

### 12.4 Potential Conflict: FDM Tolerances vs. Snap-Fit Precision

**Conflict statement:** FDM printing achieves ±0.2–0.3 mm tolerance; snap-fit design requires ±0.1 mm snap undercuts. Tolerances may not align.

**Resolution:** Snap-fit design research (snap-fit-design.md) recommends:
- **Target undercut tolerance: ±0.1–0.2 mm** (achievable with calibrated Bambu H2C)
- **Snap assembly force: 40–50 N per snap** (allows 0.2 mm tolerance stack without force exceeding limits)
- **Test prints:** Single snap hooks should be printed first to validate tolerance and assembly force before committing to full enclosure halves

**Action:** Perform test prints of 3–5 snap hooks with different undercut depths (2.6, 2.7, 2.8, 2.9 mm) to find the optimal depth for 40–50 N assembly force with the specific printer and material.

**No conflict.** Iterative tolerance calibration will resolve this.

---

### 12.5 Potential Conflict: Seam Recess vs. Snap Geometry Clearance

**Conflict statement:** Adding a 0.5–1.0 mm recess channel along the seam may interfere with snap hook engagement if not designed carefully.

**Resolution:** The recess channel is an **optical/tactile surface feature only.** It sits on the **outer edges** of the two halves and does not affect snap hook geometry, which is **internal.**

**Geometry approach:**
```
Outer surface (visible)        Internal surface (hidden)
  ╔═══════════════╗             ║─────────────────║
  ║ Matte finish  ║             ║ Snap hook → ╱   ║
  ║───────────────║  Recess     ║───────────────║
  ║               ║  channel    ║ Undercut ← ╲  ║
  ║───────────────║  (shadow)   ║───────────────║
  ╚═══════════════╝             ╚─────────────────╝

The recess is on the outer edge; the snap hook and undercut are
on the interior, facing inward. No conflict.
```

**No redesign required.** Snap geometry and recess are on separate surfaces.

---

## 13. Open Questions for Next Phases (Steps 4a/4b)

These items require validation through prototype testing or further design iteration:

### 13.1 Printer Calibration and Tolerance

- **Question:** What is the actual tolerance of the Bambu H2C when calibrated for this material and geometry?
- **Action (Step 4a):** Print 3–5 test snap hooks with undercut depths 2.6–2.9 mm; measure actual assembly force for each; select optimal depth
- **Success metric:** Achieve 40–50 N per snap with <0.2 mm tolerance stack

### 13.2 Material Selection Validation

- **Question:** Does Nylon (PA12) print cleanly on the Bambu H2C without warping or delamination at 220×300×400 mm scale?
- **Action (Step 4a):** Print 50% scale test halves (110×150×200 mm) in both Nylon and PETG; compare print quality, tolerance, and finish
- **Success metric:** Clean print with <0.3 mm dimensional variation; snap hooks pass assembly force test

### 13.3 Support Removal Feasibility

- **Question:** Do break-away ribs (0.3×0.8 mm, 0.2 mm interface gap) actually snap cleanly by hand without damaging the snap hook surface?
- **Action (Step 4a):** Print snap test specimens with intentional supports; attempt hand removal; measure surface damage
- **Success metric:** Ribs break cleanly; snap hook surface intact within 0.1 mm

### 13.4 Seam Gap Uniformity in FDM Print

- **Question:** Can the enclosure halves be printed such that the seam gap stays within ±0.2 mm variation along the entire 1040 mm perimeter?
- **Action (Step 4b):** Print full enclosure halves; measure seam gap at 20 points around perimeter (every ~50 mm); assess consistency
- **Success metric:** 90% of points within ±0.1 mm, 100% within ±0.2 mm

### 13.5 Recess Channel Optical Effect

- **Question:** Does a 0.5–1.0 mm recess channel along the seam, when painted matte black, actually create the intended shadow line and premium appearance?
- **Action (Step 4b):** After painting prototype, inspect under various lighting angles; photograph at 35° viewing angle
- **Success metric:** Shadow line clearly visible and reads as intentional design; seam reads as premium, not cheap

### 13.6 Snap Assembly Force and Seating Consistency

- **Question:** Do all 10 snaps seat simultaneously and uniformly, or do some seat before others (indicating inconsistent geometry)?
- **Action (Step 4b):** Assemble prototype with force gauge; record force profile as halves come together; observe snap seating order
- **Success metric:** All snaps engage within 50 N ±10 N; audible/tactile feedback at each snap; no rocking after assembly

### 13.7 Component Fit and Mounting

- **Question:** Do bags, pumps, valves, and displays actually snap into their mounting points cleanly without force or misalignment?
- **Action (Step 4b):** Insert all interior components into assembled enclosure; verify snapping action and position accuracy
- **Success metric:** All components snap in place without hand force; positions align within ±2 mm

### 13.8 Bag Constraint Height Validation

- **Question:** When two Platypus bags are mounted in the enclosure with the designed cradles and constraints, do they actually maintain 25–30 mm height across fill levels (0.5L, 1.0L, 1.5L, 2.0L)?
- **Action (Step 4b):** Fill test bags with water at various levels; measure vertical height with caliper; compare to design spec
- **Success metric:** Constrained heights: 0.5L ≈ 24–25 mm, 1.0L ≈ 25–26 mm, 1.5L ≈ 26–28 mm, 2.0L ≈ 27–28 mm (all within 25–30 mm target)

### 13.9 Paint/Finish Application

- **Question:** What is the best approach to apply matte black finish (paint, powder coat, dye) that achieves 20–40% gloss and hides layer marks?
- **Action (Step 4b):** Test multiple finish approaches (spray paint, dip, sanding + paint, etc.) on test halves; measure gloss; assess appearance
- **Success metric:** Uniform matte finish across both halves; seam gaps concealed by finish; no visible layer marks

### 13.10 Structural Rigidity Under Load

- **Question:** Does the 1.5 mm wall + internal rib structure actually provide sufficient rigidity (target <0.5 mm deflection under 10 N corner load)?
- **Action (Step 4b):** Apply 10 N load at enclosure corner with dial indicator; measure deflection
- **Success metric:** Deflection <0.5 mm; no flex or creaking sounds

---

## 14. Next Steps and Handoff to CAD/Prototyping

### 14.1 Immediate Actions (Step 4a)

1. **Finalize seam placement and rib layout** in CAD based on this synthesis document
2. **Generate test snap specimens** (5 different undercut depths) for tolerance validation
3. **Print test specimens** in both Nylon and PETG
4. **Measure snap assembly force** for each specimen
5. **Document results** and select optimal snap undercut depth for final enclosure design

### 14.2 Prototype Build (Step 4b)

1. **Print full enclosure halves** at optimized snap geometry (based on test results)
2. **Perform support removal** and document surface quality
3. **Measure seam gap** at 20 points around perimeter
4. **Apply paint/finish** and evaluate matte black appearance
5. **Assemble without internal components** and verify snap seating, rigidity, and visual seam appearance

### 14.3 Component Integration (Step 4c)

1. **Print component mounting frames** (bag cradles, constraints, pump cartridge dock, valve rack, display frames)
2. **Mount all components** into assembled enclosure
3. **Verify snap-in action** and position alignment
4. **Test bag constraint height** with filled water bags at multiple fill levels

### 14.4 Validation and Refinement

1. **Photograph prototype** under various lighting (eye level, 35° angle, detail of seam)
2. **Document findings** against acceptance criteria (visual, tactile, structural, cosmetic)
3. **Iterate** if any criteria fail (tolerance adjustment, design refinement)
4. **Finalize CAD** for production/field assembly

---

## 15. Summary and Execution Authority

This synthesis document provides a **complete, concrete, specific execution plan** for the soda flavor injector enclosure. Every dimension, tolerance, material specification, and design decision is grounded in:

- **Vision document** (intent: unified consumer product, permanent sealed enclosure, all components snap-mounted)
- **Requirements document** (constraints: FDM manufacturing limits, Bambu H2C capacity, material properties)
- **Design patterns research** (proven methods: gap uniformity, matte finish, seam recess, fillets, snap-fit feedback)
- **Platypus bag profile research** (validated geometry: lens-shaped cradles, 25–30 mm constrained height, pressure distribution)
- **Snap-fit design research** (tested parameters: 10 snaps, 100 mm spacing, 40–50 N per snap, cantilever beam geometry, Nylon material, assembly force)

**Ready for CAD implementation and test print validation.**

Conflicts identified and resolved; open questions flagged for next phases; bill of materials specified; material and finish choices justified; acceptance criteria defined.

---

**Document Author:** Lead Synthesis Engineer
**Date:** 2026-03-29
**Status:** Ready for handoff to Step 4a (CAD architecture)
