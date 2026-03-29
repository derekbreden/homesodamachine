# Rail Guidance Research: Cartridge Slide-In/Slide-Out Mechanism

## Question

What rail geometry, clearances, and tolerances produce a smooth, confident slide-in/slide-out action for a 3D-printed (FDM) cartridge module at this scale and weight?

## Context

- **Cartridge weight:** 500-800g (2 Kamoer KPHM400 pumps + housing)
- **Insertion depth:** ~150mm
- **Rails:** On the dock (enclosure interior walls)
- **Grooves:** On the cartridge sides
- **Enclosure interior width:** ~220mm outer, so interior rail span is roughly 200-210mm
- **Printer:** Bambu H2C, 0.4mm nozzle, 0.1-0.3mm layer height
- **Supported materials:** PLA, PETG, ABS, ASA, PA, PC, and fiber-reinforced variants
- **Manufacturing constraints:** 0.2mm minimum clearance for sliding fits, 0.8mm minimum wall, 45-degree overhang limit

---

## 1. Rail Cross-Section Geometry

### Profiles Evaluated

**Simple rectangular tongue-and-groove (recommended):**
A rectangular rail on the dock wall slides into a rectangular channel on the cartridge side. This is the simplest geometry to design, print, and tune. No angled surfaces means no overhang concerns regardless of print orientation. The rail resists pull-out in one axis (perpendicular to insertion) and permits free sliding along the insertion axis.

- Rail (tongue) cross-section: **4mm wide x 4mm tall**
- Groove (channel) cross-section: **4.5mm wide x 4.5mm tall** (includes 0.25mm clearance per side)
- Minimum wall behind groove: 1.2mm (3 perimeters at 0.4mm nozzle)
- Minimum wall thickness of rail: 4mm (10 perimeters — very rigid)

At this scale (150mm insertion depth, 500-800g load), a 4x4mm rail is structurally more than adequate. The cartridge weight produces negligible bending on the rails — the dominant force is the user pushing/pulling during insertion and removal.

**Dovetail:**
A trapezoidal rail that is wider at the base than the top, preventing pull-out in two axes. Dovetails are superior for assemblies that must resist separation forces, but they introduce FDM complications:
- Angled faces (typically 55-60 degrees from vertical) create overhangs that degrade surface finish or require supports
- The more contact surfaces and tighter geometry amplify tolerance stack-up
- Thin dovetail tips are fragile on FDM parts

Dovetails are overkill here. The cartridge only needs guidance along one axis (forward/back). Side loading is negligible — the cartridge sits in a dock, not cantilevered. The quick-connect tubes provide all retention once inserted.

**T-slot:**
A rail with a wider head (like an inverted T or mushroom). Provides pull-out resistance like a dovetail but with right-angle geometry that prints cleanly. However, assembly requires either end-loading (the cartridge must slide in from one end) or a two-piece rail — both of which the rectangular profile also requires. T-slots add complexity without benefit at this scale.

### Recommendation

**Use rectangular tongue-and-groove.** It is the simplest to print, the easiest to tune clearance on, and fully sufficient for the forces involved. The enclosure walls constrain the cartridge laterally; the rails provide alignment and prevent the cartridge from tilting or skewing during insertion. They do not need to resist significant separation forces.

### Dimensional Specification

| Feature | Dimension | Notes |
|---------|-----------|-------|
| Rail (tongue) width | 4.0mm | On dock wall |
| Rail (tongue) height | 4.0mm | Protrusion from dock wall |
| Groove width | 4.5mm | On cartridge side; 0.25mm clearance per side |
| Groove depth | 4.5mm | 0.25mm clearance at bottom + 0.25mm extra for debris tolerance |
| Rail length | Full insertion depth (~150mm) | Continuous, no interruptions |
| Number of rails | 2 (one per side) | Symmetric, matching the cartridge groove on each side |

---

## 2. Clearance and Tolerance for FDM

### Clearance Range

The requirements specify 0.2mm minimum clearance for sliding fits. Research across multiple sources converges on the following for FDM with a 0.4mm nozzle:

| Clearance (per side) | Fit Character | Application |
|----------------------|---------------|-------------|
| 0.15mm | Snug sliding — noticeable friction, may stick | Press-to-slide, detent-like |
| 0.20mm | Firm sliding — smooth but requires deliberate force | Minimum for this application |
| 0.25mm | Easy sliding — smooth, confident, minimal wobble | **Target for this cartridge** |
| 0.30mm | Free sliding — noticeably loose, some rattle | Too loose for guided insertion |
| 0.40mm | Sloppy — visible gap, poor alignment | Inappropriate |

**Target: 0.25mm clearance per side (0.5mm total gap across the rail width).** This is the 1x nozzle-width rule (0.4mm nozzle, round slightly down because a well-calibrated Bambu H2C holds tighter tolerances than average FDM printers). This produces a slide that feels guided and deliberate without binding.

At 150mm insertion depth, even 0.25mm per side allows only ~0.19 degrees of angular play — the cartridge cannot visibly tilt or wobble during insertion.

### FDM Layer Orientation and Surface Finish

Layer orientation has a significant impact on rail friction:

- **Layers parallel to the sliding direction:** The surface the rail slides against is smooth (the side of continuous extrusion lines). This is the ideal orientation. Friction is at its lowest because the motion runs along the layer lines, not across them.
- **Layers perpendicular to the sliding direction:** The surface has a staircase texture (layer lines running across the motion path). This dramatically increases friction and produces a gritty, stuttering feel during insertion. Avoid this.
- **Quantitative difference:** Layer-line surface roughness on FDM parts is typically Ra 10-30 micrometers on side walls (layers parallel to motion) versus Ra 50-100+ micrometers on staircase surfaces (layers perpendicular). The parallel case is 3-5x smoother.

**This means:** Both the dock (with rails) and the cartridge (with grooves) should be printed so that layer lines run parallel to the insertion axis. For a cartridge that slides in horizontally (front-to-back), both parts should be printed with the insertion axis aligned with the XY plane (horizontal on the build plate). See Section 6 for specific orientation.

### Calibration Protocol

Before committing to the full cartridge print, print a short (30mm) test section of the rail and groove at clearances of 0.20, 0.25, and 0.30mm per side. The tightest one that slides freely without binding at room temperature is the correct clearance for the full-length part.

---

## 3. Draft and Entry Taper

### The Problem

At 0.25mm clearance per side, blind alignment of a 150mm-long rail into a 150mm-long groove is difficult. The user cannot see the rails during insertion (the cartridge blocks the view). Without a lead-in, the user must align the cartridge to within 0.25mm before any part of the rail engages the groove — a frustrating experience.

### Recommended Taper

Add a **chamfered lead-in on both the rail and the groove entry:**

| Feature | Specification |
|---------|---------------|
| Taper angle | 30 degrees from the rail/groove face |
| Taper length on rail tip | 5mm (both sides and top of the rail tip) |
| Taper length on groove entry | 5mm (matching chamfer on groove mouth) |
| Effective capture zone | ~5.8mm per side at the entry point (5mm x tan(30) + 0.25mm clearance) |

A 30-degree chamfer at 5mm length provides roughly 2.9mm of additional capture zone per side beyond the nominal clearance. This means the user can be off by nearly 3mm in alignment and the chamfers will still guide the cartridge onto the rails smoothly.

The 30-degree angle is shallow enough to guide smoothly (no abrupt engagement), steep enough to fit in 5mm of length, and well within FDM overhang limits (30 degrees from the face is 60 degrees from horizontal — no support needed).

### Additional Alignment Feature

Consider a **wider funnel chamfer** (2-3mm, 45 degrees) at just the very entry of the groove mouth. This provides a coarse initial capture even before the precision taper engages. Total lead-in zone: ~8mm from first contact to full rail engagement.

---

## 4. Retention During Slide-In

### The Scenario

The vision states that the quick-connect tubes provide all retention once inserted. But between the moment the user starts sliding the cartridge in and the moment the tubes engage the quick connects, the cartridge could slide back out from:
- The enclosure being slightly tilted
- The user releasing the cartridge before tubes engage
- Vibration

### Analysis: Is Gravity + Friction Sufficient?

With the cartridge sliding in horizontally and the enclosure sitting on a counter or under a sink:

- Cartridge weight: 500-800g (5-8N)
- Rail friction force (PETG on PETG, dynamic CoF ~0.25-0.35): 1.3-2.8N per rail face in contact
- At 0.25mm clearance, the cartridge rests on the bottom rail surfaces under gravity, providing normal force
- Total friction resistance to sliding back: roughly 2.5-5.5N across all contact surfaces

This friction alone is marginal — it will hold the cartridge stationary but a light bump could dislodge it. However, the insertion motion is a single deliberate push. The distance between full rail engagement and tube engagement is likely only 10-20mm (the tube stubs protrude into the dock). The user's hand is on the cartridge the entire time.

### Recommendation: Simple Printed Detent Bump

Add a small **printed detent bump** on each rail, positioned at the fully-inserted location:

| Feature | Specification |
|---------|---------------|
| Bump geometry | Hemisphere or half-cylinder, 0.5mm tall above rail surface |
| Bump width | 2mm along the rail |
| Position | At the full-insertion point (last 5mm of rail) |
| Matching groove | A slight relief (0.3mm extra depth) in the groove at the corresponding position |
| Engagement force | ~3-5N to push past (user feels a subtle click) |
| Retention force | ~2-3N to pull back past (enough to prevent gravity/vibration slide-out) |

This provides:
1. **Tactile feedback** — the user feels a click when the cartridge reaches full insertion, confirming correct position
2. **Passive retention** — holds the cartridge in place while the user connects tubes, or if the enclosure is bumped
3. **Zero additional parts** — printed as part of the rail geometry, no springs or bearings needed

The bump is small enough (0.5mm) that it does not cause binding during insertion — the 5mm entry taper on the bump itself (shaped like a speed bump, not a wall) lets the cartridge glide over it with moderate force. At once-per-year removal cycles, wear on the bump is negligible.

### Alternative: No Detent

If the tube quick-connects engage within the first 5-10mm of full insertion, and the user is instructed to push until tubes click, the detent may be unnecessary. The quick-connect insertion force itself (~5-10N per connector, 20-40N total for 4 connectors) provides strong tactile and physical confirmation. The detent is a low-cost insurance policy — worth including, easy to remove from the design if testing shows it's superfluous.

---

## 5. Wear and Cycle Life

### Usage Profile

The cartridge is removed approximately once per year for pump replacement. Over a 10-year product life, that is roughly 10 insertion/removal cycles — an extremely low-wear application.

### Material Comparison for Rail/Groove Surfaces

| Property | PLA | PETG | ABS |
|----------|-----|------|-----|
| Dynamic CoF (plastic-on-plastic) | 0.20-0.35 | 0.25-0.35 | 0.35-0.45 |
| Wear resistance (sliding) | Moderate | Good | Good (best in one study at 0.1mm layers) |
| Moisture sensitivity | Low (but brittle over time) | Low | Low |
| Creep resistance | Poor (deforms under sustained load at room temp) | Good | Good |
| UV resistance | Poor | Moderate | Moderate (ASA is better) |
| Temperature resistance | Low (softens ~55C) | Good (~75C) | Good (~100C) |
| Impact toughness | Low (brittle) | Good | Good |
| Printability | Excellent | Good | Good (needs enclosure) |

### Recommendation: PETG

**PETG is the best choice for both the cartridge and dock rail surfaces.** Rationale:

1. **Adequate friction coefficient** — low enough for smooth sliding, high enough to provide some natural retention
2. **Good wear resistance** — at 10 cycles over the product lifetime, even PLA would survive, but PETG provides margin
3. **No creep** — PLA under sustained load (the cartridge resting on rails permanently) can slowly deform at room temperature over months/years. PETG does not.
4. **Temperature tolerance** — under a sink or on a counter in a kitchen, ambient temperatures can reach 35-40C in summer. PLA softens at 55C with very little margin. PETG is comfortable to 75C.
5. **Not brittle** — PLA becomes brittle over time, especially with UV exposure. A brittle rail that snaps during the once-per-year cartridge removal is a product failure. PETG remains tough.
6. **No enclosure needed for printing** — unlike ABS, PETG prints reliably on the Bambu H2C without a heated chamber.

ABS would also work but requires more careful print conditions and offers no meaningful advantage over PETG for this application. PLA should be avoided — its creep and brittleness over time are unacceptable for a structural feature in a consumer appliance.

### PETG+PTFE Consideration

Specialty PETG/PTFE filaments (90% PETG, 10% PTFE) exist and offer lower friction coefficients. For a once-per-year sliding operation, this is unnecessary — standard PETG slides well enough. If the cartridge were removed weekly, PETG/PTFE would be worth evaluating.

---

## 6. Print Orientation for Rails

### Core Principle

FDM parts are weakest between layers. A rail that could shear off along a layer boundary during cartridge insertion or removal is a critical failure mode. The print orientation must ensure that forces on the rail load it across many layers, not along a single layer boundary.

### Dock (Rails)

The dock is part of the enclosure interior. The rails protrude inward from the side walls.

**Preferred orientation: Print the dock with the insertion axis horizontal (lying on the build plate).**

- The rails protrude in the Z direction (upward from the build plate) or in the XY plane
- If the dock wall is printed vertically (wall face parallel to build plate), the rail protrudes horizontally from the wall. Layers stack vertically through the wall and rail together. Shear forces on the rail during cartridge insertion load across dozens of layer bonds simultaneously — very strong.
- Layer lines run parallel to the insertion direction, giving the rail's sliding surface the smoothest possible finish.

**Orientation to avoid:** Printing the dock so that layers stack along the insertion axis. This would make the rail's sliding surface a staircase of layer edges (rough, high friction) and would make the rail weakest exactly in the direction of insertion/removal force.

### Cartridge (Grooves)

The cartridge is a box-like housing with grooves cut into its side walls.

**Preferred orientation: Print the cartridge on its back face (the face with the 4 quick-connect holes down on the build plate), so the insertion axis is vertical (Z).**

Wait — this conflicts with the surface finish requirement (layers perpendicular to insertion = rough groove surface). Re-evaluating:

**Preferred orientation: Print the cartridge on its side, so the insertion axis is horizontal (in XY).**

- Groove channels run along the X or Y axis on the build plate
- Layer lines inside the groove run parallel to the insertion direction — smooth sliding surface
- The groove walls are formed by perimeters (strong, continuous extrusion lines), not layer boundaries
- The cartridge side walls are loaded in compression during rail engagement — layers stack perpendicular to the compression, which is the strongest orientation

**Trade-off:** Printing on the side may require supports for internal features (pump mounting bosses, quick-connect housings). This is acceptable — the groove surfaces and external faces are the cosmetic/functional surfaces and they will be support-free in this orientation.

### Summary Table

| Part | Print Orientation | Insertion Axis | Layer Lines vs. Sliding Direction | Rail/Groove Strength |
|------|-------------------|----------------|-----------------------------------|---------------------|
| Dock | Wall face on build plate or upright | Horizontal (XY) | Parallel (smooth) | Layers bridge across rail — strong |
| Cartridge | On its side | Horizontal (XY) | Parallel (smooth) | Groove walls are perimeters — strong |

---

## 7. Failure Modes

| Failure Mode | Cause | Mitigation |
|-------------|-------|-----------|
| Rail snaps off dock wall | Layer delamination if printed with layers along rail protrusion axis | Print dock so layers bridge across the rail root (see Section 6) |
| Groove edge chips during insertion | Brittle material (PLA) or sharp groove edges | Use PETG; add 0.5mm fillets on all groove edges |
| Cartridge binds mid-insertion | Clearance too tight, thermal expansion, or debris in groove | Use 0.25mm clearance; add 0.5mm extra depth at groove bottom for debris; test at multiple temperatures |
| Cartridge wobbles excessively | Clearance too large | Stay at 0.25mm per side; test before committing |
| Cartridge slides out before tubes engage | No retention, enclosure tilted | Add printed detent bump at full-insertion position |
| Rail wears smooth over time | Repeated insertion cycles | Negligible at 10 cycles/lifetime with PETG |
| Creep deformation of rail under cartridge weight | PLA under sustained load | Use PETG (no measurable creep at room temperature under this load) |
| Misalignment during blind insertion | User cannot see rails | 5mm entry tapers + 3mm funnel chamfer provide ~6mm capture zone |

---

## 8. Summary of Recommendations for the Vision

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| Rail profile | Rectangular tongue-and-groove | Simplest to print and tune; sufficient for guided insertion with no separation loads |
| Rail cross-section | 4mm x 4mm rail; 4.5mm x 4.5mm groove | 0.25mm clearance per side; structurally adequate for 800g cartridge |
| Clearance | 0.25mm per side (0.5mm total gap) | Smooth but not wobbly; 1x nozzle width rule for well-calibrated Bambu |
| Entry taper | 30-degree chamfer, 5mm long on rail tips and groove mouths | Provides ~3mm capture zone for blind alignment |
| Retention | Printed 0.5mm detent bump at full-insertion point on each rail | Tactile click + passive hold until tubes engage; no extra parts |
| Material | PETG for both dock and cartridge | Best balance of friction, wear, creep resistance, and printability |
| Print orientation | Both parts with insertion axis horizontal in XY | Layer lines parallel to sliding = smooth surface; rail root bridges across layers = strong |
| Calibration | Print 30mm test section at 0.20/0.25/0.30mm clearance before full part | Validate on actual printer with actual material |
