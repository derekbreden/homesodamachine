# Bag Frame — Mechanism Synthesis

**Date:** 2026-03-29
**Inputs:** hardware/requirements.md, hardware/vision.md, design-patterns.md, platypus-bag-geometry.md, structural-analysis.md
**Next step:** architecture (spatial layout and part breakdown) → specification (per-part geometry definitions)

---

## 1. Mechanism Overview

The bag frame is a two-bag suspension-and-constraint system mounted inside the upper zone of the enclosure. It is not a shelf. It is not two independent cradles. It is one mechanism — visually and structurally — that presents two bags as two equal instances on a shared spine.

Each of the two Platypus 2L bags is cradled from below by a lens-shaped platform, pressed from above by a matching upper cap, and captured at its fold end by a front-wall clip. The two platforms and two caps share a single continuous spine that spans the full width of the enclosure and snaps permanently to the enclosure halves. Viewed from the front, the user sees one organized element with two symmetric bag positions — not two cradles sitting near each other.

The bags are loaded at assembly time and are not user-removable. The upper caps snap closed once and remain closed. The front-wall clips are fixed features of the enclosure or the spine. The tube connections enter from the cap end, buried in the rear-bottom pocket of the enclosure.

---

## 2. Spatial Orientation — Confirmed Numbers

The bags are diagonal at 35° from horizontal, cap end toward the back-bottom, fold end pressed flat against the front wall.

**Bag projected footprint at 35°:**
- Depth (front-to-back): 350 mm × cos(35°) = **287 mm**
- Vertical span per bag: 350 mm × sin(35°) = **201 mm**

**Enclosure allocation:**
- Enclosure: 220 mm wide × 300 mm deep × 400 mm tall
- The bags sit in the upper zone. The two-bag stack height is approximately 110 mm vertical (see Section 6). This leaves approximately 50 mm of headroom within the bag zone for the funnel above.
- Depth: 287 mm diagonal projection < 300 mm enclosure depth. Clearance at the rear wall: ~13 mm. This is tight and is flagged as a conflict (see Section 8).
- Width: Bag flat width 190 mm + 3 mm/side cradle clearance = 196 mm between inner lip faces. Spine walls and enclosure snap interfaces must fit within 220 mm total. Width budget: 220 − 196 = 24 mm for structure on both sides combined (12 mm per side maximum for lip wall, structural rib, and enclosure interface). Workable but requires disciplined geometry.

---

## 3. The Mechanism — Part by Part

### 3.1 The Spine

The spine is the primary structural and visual element. It is a single continuous part that spans the full 220 mm width of the enclosure interior. Both cradle platforms mount to it at defined positions, spaced so the mechanism reads as regular and intentional. The spine's two outer ends engage snap features in each enclosure half — two snap points per end (four total) — making it the first permanent sub-assembly step.

The spine is visible from the front of the mechanism between the two bag positions. This is intentional: the eye reads the spine first, then the bag positions as two equal subdivisions of it. The spine face that is visible carries the same rib language as the enclosure interior panels — parallel ribs at 8–12 mm spacing, 1.5 mm height, running in one direction (transverse).

The spine also carries the two front-wall clip features at its top front edge — one per bag — that capture the folded top ends of the bags against the front enclosure wall.

### 3.2 Cradle Platform (×2, identical parts)

Each cradle is a lens-shaped half-shell — open at the top, concave surface upward, longitudinal ribs on the underside. It snaps onto the spine at its inboard edge at a defined position and contacts the enclosure side wall at its outboard edge via a locating feature.

**Cross-section geometry (the lens profile):**
- Constrained midsection thickness: **27 mm** (midpoint of the 25–30 mm vision range; to be confirmed empirically)
- Bag width: 190 mm flat
- Cradle inner width between opposing side lips: **196 mm** (190 mm + 3 mm per side clearance per design-patterns guidance)
- Arc radius of the lens cross-section: **R = 341 mm** (calculated from the 27 mm sagitta, 190 mm chord — this is a very shallow bowl, sagitta 27 mm across 190 mm)
- The arc profile is the same at both the midsection and the body zone. It shallows toward the fold end as the bag tapers toward its flat-pinned top.

**Depth profile along the bag axis:**
- The cradle is shallowest at the fold end (upper-front): the bag thins toward zero here. The cradle transitions smoothly to a near-flat surface over the last ~50 mm before the front wall.
- The cradle is at its design depth (27 mm sagitta) across the full body zone (~220 mm of active length).
- The cradle deepens at the cap-end (lower-rear) pocket, accommodating the cap and spout protrusion: **pocket depth ~40–45 mm, pocket width ~35–40 mm**. This pocket is a cylindrical or oval recess contoured to the neck taper zone of the bag. The pocket transitions smoothly from the body cradle depth to the pocket depth over the ~50 mm taper zone — a smooth longitudinal curve, not a step.

**Structural specification:**
- Floor wall thickness: **2.0 mm** (required by span analysis — unribbed floor spanning 40 mm transverse cells needs ~2.0 mm)
- Longitudinal ribs on underside: **3 ribs, running the full 280 mm supported length**, spaced ~40 mm transversely
- Rib height: **6 mm** below floor (underside)
- Rib wall thickness: **1.6 mm**
- Side lip height above lowest platform surface: **10 mm** (midpoint of the 8–12 mm range from design-patterns guidance)
- Interior corner radius (floor-to-lip): **3 mm** (per design-patterns guidance: 2–4 mm)
- Lip top edge radius: **1.5 mm** (per design-patterns guidance: 1–1.5 mm)
- The interior corner of the cap-end pocket uses **15–20 mm radius** where the bag seam meets the pocket wall, to prevent stress concentration on the film seams.

**Print orientation:** Face-up (concave surface facing the build plate's print direction — upward). The convex underside rests on the build plate. Ribs print as upward walls. No overhang violations. The snap interface to the spine is on the inboard long edge; snap arms on this edge flex in the X/Y plane.

### 3.3 Upper Cap (×2, identical parts)

Each upper cap is the mirror-surface complement to its cradle platform: same lens cross-section profile (R = 341 mm, same chord), pressing against the top face of the bag. The total gap between cradle floor and cap inner face is **27 mm** at the midsection.

The upper cap is the element that enforces the 25–30 mm constraint and prevents the bag from bulging to its unconstrained 40 mm profile. It therefore must contact the bag face across the full body zone, not just at the perimeter.

**Structural specification:**
- Face thickness: **1.5 mm** (adequate for the ~447 Pa distributed load with grid ribs)
- Rib grid on top face: **3 longitudinal ribs + 2 transverse ribs**, creating ~40 mm × 55 mm cells
- Rib height: **5 mm** above face
- Rib thickness: **1.2 mm**
- The cap face in contact with the bag is smooth — no ribs on the bag-contact side. Any surface texture on this face must not create stress concentrations on the bag film.

**Snap arm geometry (per structural analysis):**
- 4 snap arms per cap (2 per long edge), engaging hooks on the cradle side lips
- Arm length: **20 mm** (from cap perimeter to hook tip)
- Arm thickness: **2.0 mm** (PETG; strain at 1.5 mm deflection = 1.1%, well within 4% limit)
- Arm width: **6 mm**
- Hook height: **1.2 mm**
- Hook lead-in angle: **30°** (camming surface for snap engagement)
- Hook retention face: **90°** (perpendicular undercut — permanent assembly, consistent with vision statement that bags are not user-removed)
- Root fillet: **1.0 mm**

**Engagement sequence (per design-patterns UX guidance):**
1. Cap is offered to the cradle at the midsection and pressed down. The 30° lead-in on the hook cams the arms outward.
2. As the cap travels ~1.5 mm into the locked zone, the hooks clear the cradle lip and the arms spring inward — tactile drop into the locked state.
3. A firm stop as the cap face contacts the bag and the hooks seat behind the cradle lip.
The user feels: approach resistance → drop → stop. No visual confirmation needed.

**Reveal geometry (per design-patterns guidance):**
The cap's perimeter edge sits 1.5–2 mm above the cradle lip top edge when locked, creating a deliberate visible step that reads as "component seated in housing." This step is a design feature, not a tolerance artifact.

**Print orientation:** Face-down (bag-contact face flat on build plate for best surface quality; ribs print upward as walls; snap arms extend outward from the long perimeter edges and flex in-plane with layers, satisfying the requirements.md constraint for snap-fit flex direction).

### 3.4 Front-Wall Fold Clips (×2, integrated into spine or enclosure front wall)

The fold end of each bag — a 15–20 mm tall flat heat-sealed strip, 190 mm wide, ~3–8 mm thick when folded — is captured against the front wall by a simple ledge or tab. This is a low-force interface; the bag does not pull away from the front wall under gravity (the diagonal angle holds it there). The clip's function is to prevent the bag from drifting away from the wall as it empties and the film goes slack.

Geometry: a **5 mm deep slot or tab** integrated into the front wall of the enclosure (or into the spine's front edge). The slot is 190 mm wide and 20 mm tall. The bag fold end slips into the slot from above during assembly and is held by friction and gravity. No active locking required here — the upper cap closure, which presses the bag from above across its full body zone, prevents the fold end from migrating out of the slot.

---

## 4. Fill-Level Behavior and Cradle Accommodation

The research establishes that as the bag empties at 35°, liquid pools to the cap end. The cross-section at the cap zone remains fully loaded (27 mm constrained profile) as long as any significant liquid remains. The liquid-to-air interface migrates upward along the bag axis, and above it the film collapses flat.

**What this means for the cradle:**
- The cap-end pocket must support the full 27 mm (or slightly deeper, unconstrained) profile at all fill levels. The pocket is not a "full bag only" feature — it is always under load.
- The upper cap contacts the bag across the entire body zone from cap-end to fold-end regardless of fill level. At partial fill the upper cap simply rests against collapsed film in the upper zone — this is fine. The constraint is only load-bearing in the liquid-filled zone.
- The cradle side lips (10 mm height) are sufficient to retain the bag at all fill levels including when the bag is empty and the film is fully slack, because the upper cap is closed and holds the film against the cradle surface.
- No special partial-fill geometry is required beyond what serves the full-fill case. The mechanism is fill-level agnostic by design.

---

## 5. Cap-End Pocket Geometry

The Platypus cap + spout assembly protrudes **40–50 mm below the bag body seam**. The pocket in the cradle's lower (rear) end must accommodate this without stressing the bag seam.

**Pocket specification:**
- Pocket axial depth (along bag axis from bottom seam): **50 mm** (matches maximum cap protrusion plus 0–5 mm clearance)
- Pocket radial clearance around cap: The cap body OD is ~30 mm; the cradle pocket inner diameter or equivalent dimension: **38 mm** (30 mm cap OD + 4 mm per side clearance for insertion without force)
- The pocket wall thickness at this zone: **2.0 mm** minimum (same as cradle floor)
- The bottom of the pocket (rear-most point, closest to the enclosure back wall) accommodates the tube connection to the bag cap: the pocket has an opening or slot in its rear face for the tubing to exit toward the enclosure back.
- Tube exit geometry: a **10–12 mm diameter clearance hole** centered in the pocket rear face, sized for 1/4" OD tubing with a John Guest fitting (OD ~12 mm with fitting body). This hole is not a sealing surface — it is clearance only.

The cap pocket is the deepest feature of the cradle and defines the maximum depth the cradle extends toward the enclosure rear wall. Combined with the 287 mm bag projection, this is subject to the rear-wall clearance conflict described in Section 8.

---

## 6. Stack Height and Enclosure Fit — Confirmed

Per the structural analysis, two cradle assemblies stacked vertically consume approximately **110 mm of vertical height** within the enclosure. The bag allocation zone is the upper portion of the 400 mm enclosure, estimated at ~160 mm. This provides **~50 mm headroom** above the upper bag for the funnel.

**Stack accounting (vertical, measured plumb):**

| Element | Thickness (perpendicular to bag face) | Vertical component |
|---|---|---|
| Cradle floor | 2.0 mm | ~1.6 mm |
| Cradle rib zone (underside) | 6.0 mm | ~4.9 mm |
| Bag constrained thickness | 27 mm | ~22 mm |
| Upper cap (face + ribs) | 1.5 + 5 = 6.5 mm | ~5.3 mm |
| Snap arm clearance / inter-bag gap | ~5 mm | ~4.1 mm |
| **Per-bag subtotal** | **~47 mm** | **~38 mm vertical** |
| Two bags | — | ~76 mm |
| Inter-bag spacing on spine (bag edge to bag edge) | ~10 mm | ~8 mm |
| Bottom mounting clearance | ~10 mm | ~10 mm |
| **Total bag zone** | — | **~94 mm vertical** |

The two bags fit within 94–110 mm vertical (accounting for measurement rounding) — well within the ~160 mm allocated zone. The funnel above has at minimum 50 mm clearance. Stack fits.

---

## 7. Bill of Materials

### Printed Parts

| Part | Qty | Material | Print Orientation | Notes |
|---|---|---|---|---|
| Spine | 1 | PETG | Long axis horizontal, snaps facing out | Single part spanning 220 mm width; within single-nozzle build volume (325 × 320 × 320 mm) |
| Cradle Platform | 2 | PETG | Face-up (concave upward) | Both are identical; print together or in sequence |
| Upper Cap | 2 | PETG | Face-down (bag-contact face on build plate) | Both are identical; snap arms flex in-plane |

All three part types are in PETG. No material mixing required. All parts are within the Bambu H2C single-nozzle build volume.

### Hardware

| Item | Qty | Function |
|---|---|---|
| None — no hardware fasteners | — | Entire bag frame is snap-assembled; all retention is by integrated snap geometry |

The bag frame assembly uses zero hardware. Spine snaps to enclosure halves. Cradles snap to spine. Caps snap to cradles. Fold-end clips are geometry integrated into the spine front edge or enclosure front wall. This satisfies the vision requirement for press-together assembly with no fasteners internal to the sub-assembly.

---

## 8. Conflicts with the Vision — Explicit Flags

### Conflict 1: Rear-Wall Clearance

**Finding:** The bag's diagonal projection at 35° is 287 mm front-to-back. The enclosure is 300 mm deep. This leaves only **13 mm** between the bag's cap-end and the rear enclosure wall, before accounting for the cap-end pocket, its walls, the tube connection, and any enclosure-wall thickness.

**Minimum clearance required:** Cap pocket wall (~2 mm) + tube fitting OD (~12 mm) + clearance to enclosure wall (~3 mm) = ~17 mm. The pocket wall and fitting consume more than the available 13 mm.

**Proposed minimum modification:** Two options exist; only one may be chosen after empirical measurement:

Option A — Reduce the diagonal from 35° to approximately 30°. At 30°: depth projection = 350 × cos(30°) = 303 mm — still too deep. At 25°: 350 × cos(25°) = 317 mm — worse. The angle cannot fix this; reducing angle increases depth projection.

Option B — Accept that the bag's effective supported length is **not the full 350 mm flat length** but shorter. The vision says the fold end is "pinned flat against the front wall." If the fold-pinned seal zone (~15–20 mm) and the neck zone (~30 mm) are treated as non-structural overhangs beyond the cradle, the supported span from body-seam to body-seam is closer to **280–290 mm**, not 350 mm. If the front wall contact is not a pin-against-the-face but a pin of the fold end while the bag body hangs free below the pinning point, the diagonal body projection may be shorter. This requires measuring the actual bag.

**Minimum modification proposed:** Verify empirically whether the 287 mm figure is correct for the actual body span. If confirmed, shrink the enclosure's rear clearance zone by accepting the cap-end collar protrudes into the tube routing space, and route tubes laterally rather than straight out from the cap. Do not alter the 35° angle — it is specified by the vision and drives the entire fill-level behavior.

### Conflict 2: Snap Arm Orientation on the Upper Cap

**Finding:** Structural analysis flags that if the upper cap is printed face-down, snap arms extending downward from the cap perimeter would flex in the Z direction — the weakest layer-bond direction per requirements.md. The research resolves this by requiring snap arms to flex in the X/Y plane (in-plane with layers), which means arms must extend outward from the long edges and curl inward horizontally rather than hook downward.

**This is not a conflict with the vision** — the vision does not specify snap arm geometry. It is a constraint that the architecture step must carry forward: upper cap snap arms must be designed as horizontal hooks extending from the long-edge perimeter, not as downward hooks from the face perimeter. This affects the cradle lip geometry (the lip must have a horizontal ledge for the inward-hooking arm to engage, not a vertical groove).

**No vision modification needed.** Flag carried forward for architecture.

### Conflict 3: "Constrained to 25 mm" vs. "25–30 mm"

**Finding:** The vision states the constraint brings midsection thickness to "25–30 mm consistently." The geometry research uses 27 mm as the working value. The structural analysis uses 28 mm. These are estimates; the actual bag behavior under constraint has not been measured.

**This is not a conflict** but an uncertainty. The synthesis uses **27 mm** as the design target. If empirical measurement returns 30 mm, the cradle arc radius changes from R = 341 mm to R = 278 mm (still a shallow bowl, still printable). If the result is 25 mm, R = 412 mm (even shallower). The architecture phase must not commit to a fixed arc radius until the bag has been measured under constraint.

---

## 9. Open Questions — Architecture and Specification Must Address

### Measurements Required Before Geometry is Committed

These dimensions cannot be derived from research. Every item below is a caliper or ruler measurement on the actual Platypus 2L bag (ASIN B000J2KEGY):

| Unknown | Why It Matters | Measurement Method |
|---|---|---|
| Constrained midsection thickness at 27 mm (vs. 25 mm vs. 30 mm) | Sets arc radius R and cradle depth throughout — everything downstream depends on this | Fill bag with 2L water, lay at 35°, apply a flat board on top with light hand pressure, measure gap with calipers |
| Actual body span from bag body seam (above neck) to fold-seam | Sets the cradle's supported length; drives the rear-wall clearance conflict | Lay flat bag, measure from base of taper zone (where width reaches 190 mm) to fold seam |
| Cap + spout protrusion below bag body seam | Sets cap-end pocket depth | Measure from bag body seam to bottom of cap with calipers |
| Cap body OD (actual, not inferred) | Sets pocket inner diameter | Measure cap with calipers; the 29.7 mm from spec may be height, not diameter |
| Taper zone length (from 28 mm neck to 190 mm body width) | Sets where the body cradle profile begins; affects pocket transition geometry | Lay flat bag, mark where body reaches full 190 mm width, measure from neck |
| Fold end thickness when folded flat | Sets required slot depth for the front-wall fold clip | Fold the bag top end flat and measure with calipers |
| Unconstrained midsection at 35°, 2L filled | Confirms the 40 mm vision figure | Fill bag, lay at 35° on a ruler, read midsection thickness |

### Design Decisions for Architecture

1. **Spine-to-cradle interface geometry:** The cradle snaps onto the spine at its inboard long edge. The spine must have a defined slot or rail at the two bag-position heights. The vertical spacing between the two positions (center-to-center) is not yet set — it must be set to the minimum that provides the 10 mm inter-bag clearance confirmed in Section 6, derived from the measured cradle assembly height.

2. **Spine-to-enclosure snap:** The spine snaps to both enclosure halves. The snap interface must be compatible with the enclosure's permanent-snap split-line architecture. This is an inter-sub-assembly interface and must be coordinated with the enclosure design.

3. **Upper cap snap arm lateral vs. hook orientation:** As flagged in Conflict 2, the arm must flex in-plane. The architecture must define the cradle lip ledge geometry that the horizontal hook engages.

4. **Cap-end tube routing:** The tube exits the pocket rear face into the enclosure back zone. Whether the tube goes straight back (requiring the 17 mm rear clearance that may not be available) or turns 90° laterally within the pocket is a routing decision that must be resolved against the rear-wall clearance finding.

5. **Assembly sequence:** Spine snaps to enclosure halves first. Cradles snap to spine from above. Bags are laid into cradles. Upper caps are clicked down. Fold ends are slipped into front-wall slots. Tubes are connected at the cap end. This sequence must be confirmed compatible with the spatial constraints — specifically, whether the tube connection at the cap end is accessible during the cradle-loading step.

6. **Identical vs. mirrored cradle parts:** The bags are one above the other on the same incline. Both bag orientations are identical (both cap-end toward the back-bottom). No mirroring is required — both cradle platforms are printed from the same file. Confirm this by verifying the tubing exits are symmetric.
