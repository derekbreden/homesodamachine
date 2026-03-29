# Pump Cartridge — Conceptual Architecture

## 1. Piece Count and Split Strategy

**5 printed parts, 1 sliding sub-assembly:**

| # | Part | Role |
|---|------|------|
| 1 | **Tray** | Structural backbone. Open-top box holding all precision geometry: fitting pockets in the rear wall, guide posts for the release plate, pump mounting bosses with heat-set insert pockets, motor cradles, tube routing channels, and T-rail tongues on both outer side walls. |
| 2 | **Lid** | Flat panel snapping onto tray top edges. Closes the torsion box, retains tubes, stiffens the assembly. No fasteners — snap tabs only. |
| 3 | **Front bezel** | The only surface the user sees and touches. Flat outer palm rest, finger channel openings on left and right edges. Snaps onto the tray and lid front edges. Separate so it can be reprinted for color/texture without reprinting the tray. |
| 4 | **Release plate** | Small sliding plate (~55 x 55 x 5 mm) with 4 stepped bores engaging the dock-facing collets. Rides on 4 guide posts rising from the tray rear wall. Connected to pull tabs via two rigid linkage rods running along the tray inner side walls. |
| 5 | **Floor plate** | Optional removable bottom panel under the pump zone only. 2x M3 screws into heat-set inserts. Exists only if pumps cannot be installed from above before the lid goes on — decide during prototyping. If eliminated, part count drops to 4. |

**Why this split:** The tray concentrates every alignment-critical feature (fitting bores, guide posts, rail tongues, pump boss spacing) into one part, eliminating cross-part tolerance stack-up. The lid and front bezel are cosmetic/structural shells with no precision interfaces. The release plate must slide, so it is inherently separate. The floor plate is an escape hatch for assembly sequence flexibility.

**Linkage rods** are either printed integral with the release plate (T-shaped hooks at each end) or cut from 4 mm PETG rod stock. They run through guide slots in the tray side walls and attach to pull-tab paddles that sit inside the front bezel's finger channels.

---

## 2. Join Methods

| Joint | Method | Rationale |
|-------|--------|-----------|
| Lid to tray | Snap tabs (4 per long edge, engaging detent ridges on tray walls) | Tool-free open/close for tube routing during assembly. Adequate retention — the cartridge is enclosed in the dock during use. |
| Front bezel to tray + lid | Snap tabs (2 per side wall, 1 on floor, 1 on lid edge) | Same tool-free philosophy. The bezel is the last part installed and the first removed for service. |
| Pumps to tray floor | M3 x 8 mm SHCS into M3 x 5.7 mm brass heat-set inserts (2 per pump, 4 total) | Factory bracket has M3 holes at 49.45 mm c-c. Heat-set inserts give reliable threads in PETG. |
| Floor plate to tray | 2x M3 screws into heat-set inserts in tray floor ribs | Infrequent access — screws are acceptable. |
| John Guest fittings to tray rear wall | Press-fit on 9.31 mm center body into 9.5 mm bores | Body end shoulders (15.10 mm) capture axially. Zero fasteners. Rigid in all 6 DOF. |
| Release plate to guide posts | Sliding clearance fit (3.5 mm posts, 3.7-3.8 mm bores) | 1.5 mm travel, negligible friction. |
| Linkage rods to release plate / pull tabs | Printed hook-and-slot | Captive once the front bezel is installed. No fasteners. |
| Blade terminals to dock | Press-fit male blades on dock; crimped female spades on pump wires inside cartridge | Self-wiping, blind-mate during rail insertion. |

**Fastener budget:** 4 M3 screws for pumps + 2 M3 screws for floor plate (if used) = 4-6 total screws. Everything else is snap-fit, press-fit, or sliding fit.

---

## 3. Seam Placement

Three visible seams on the assembled cartridge:

1. **Lid-to-tray seam** — runs horizontally along both long sides at the top edge. Hidden from the user: the cartridge sits in the dock with the lid facing upward, inside the enclosure. Never seen.

2. **Front bezel-to-tray seam** — runs around the perimeter of the front face where the bezel meets the tray side walls and lid. This is the only seam potentially visible to the user (when the cartridge is pulled out). Treated with a **step-lap joint**: the bezel overlaps the tray walls by 1.5 mm, creating a shadow line rather than a flush butt joint. The shadow line reads as intentional and hides any gap from FDM tolerance.

3. **Floor plate seam** (if floor plate exists) — underside of the cartridge. Never visible in use (cartridge rides on rails, bottom faces downward into the dock).

**No seam crosses a precision interface.** The fitting pockets, guide posts, and rail tongues are all integral to the tray. The only seam the user might ever see (front bezel) is cosmetic-only.

---

## 4. User-Facing Surface Composition

The user interacts with the cartridge only during removal and insertion. What they see and touch:

**Front bezel (the only visible surface):**
- Flat outer face with a subtle convex palm contour (1-2 mm crown over 72 mm height). Smooth, matte finish.
- Left and right finger channels — open vertical slots (25 mm deep x 15 mm wide) exposing the pull-tab paddles inside.
- Pull tabs are flat paddle surfaces (30 mm tall x 15 mm wide) with a light horizontal rib texture for grip.

**Visual hierarchy:**
1. The palm surface dominates — it is the largest flat area and communicates "push here."
2. The finger channels are recessed voids on each side — they communicate "reach in here" through negative space, not labels or icons.
3. Nothing else is visible. The fittings, tubes, pumps, rails, and electrical contacts are all behind the bezel or inside the dock. The interaction is languageless: a flat face with two side slots.

**During insertion:** The user sees only the front bezel and the T-rail edges on the sides. The rails guide the hand naturally — the cartridge can only move in one direction.

---

## 5. Design Language

**Material:** PETG throughout. Slight flex absorbs insertion/removal forces without cracking. Good layer adhesion for snap features. Resistant to the moisture environment near a sink.

**Corners:** All external corners on the front bezel have 2 mm fillets. Internal corners (tray, lid) have 1 mm fillets for printability and stress relief. The front bezel's edges where it meets the finger channels have 3 mm fillets — the user's fingers curl around these edges during the squeeze.

**Surface finish:** The front bezel prints with its outer face on the build plate for the best surface quality (smooth, slight glass-like sheen from the PEI sheet). All other parts print in their natural orientations without cosmetic concern — they are internal.

**Color:** Single color (matte black to match the enclosure dark theme). The front bezel could be a contrasting color (dark navy, matching the app theme) if visual differentiation is desired — the separate-bezel split strategy enables this at zero cost.

**What makes this a product, not a prototype:** The interaction is the design. There are no exposed screws on user-facing surfaces. No labels. No visible fasteners. The palm-and-squeeze gesture is the entire interface. The T-rails make insertion feel guided and precise, like a battery clicking into a power tool. The click at end-of-travel confirms seating. The squeeze-release confirms disconnection. Every tactile moment is deliberate.

---

## 6. Service Access Strategy

Tiered by frequency:

| Tier | Event | Frequency | Access method |
|------|-------|-----------|---------------|
| 1 | Cartridge removal/insertion | Once per 1-2 years | Squeeze front bezel, slide out on rails. No tools. |
| 2 | Tube re-routing or fitting replacement | Rare (damage repair) | Pop front bezel off (snap-fit), pop lid off (snap-fit), full access to tubes and fittings. No tools. |
| 3 | Pump replacement within cartridge | Rare (motor failure) | After lid removal, unscrew 2x M3 per pump, lift pump out. Requires M3 hex key. If floor plate is used, remove 2x M3 screws from bottom first. |
| 4 | Release plate service | Extremely rare | After front bezel and lid removal, slide release plate off guide posts. Linkage rods detach from pull tabs when bezel is removed. |

**The user never opens the enclosure to service the cartridge.** The cartridge is the serviceable unit. Within the cartridge, snap-fit shells provide tool-free access to everything except the pump mounting screws.

---

## 7. Manufacturing Constraints

**Printer:** Bambu H2C. Single nozzle build volume 325 x 320 x 320 mm. All parts fit comfortably.

| Part | Print orientation | Approximate size | Supports needed | Notes |
|------|-------------------|------------------|-----------------|-------|
| Tray | Open top facing up | 160 x 155 x 72 mm | Minimal (T-rail overhangs may need support, or design as 45-degree chamfer undercuts) | Largest part. All precision bores in Z axis for best accuracy. |
| Lid | Flat, top face up | 160 x 155 x 4 mm | None | Simple flat panel with snap tabs on edges. |
| Front bezel | Outer face on build plate (upside down) | 160 x 72 x 15 mm | Minimal (finger channel interiors may need support, or print standing up with seam on interior) | Cosmetic surface gets best finish from build plate contact. Alternative: print standing up for support-free finger channels, accept visible layer lines on palm surface. |
| Release plate | Flat in XY | 55 x 55 x 5 mm | None | Stepped bores in Z for best circularity. Critical tolerance part — print at 0.1 mm layer height. |
| Floor plate | Flat | ~80 x 60 x 4 mm | None | Simple panel. |

**Material selection:** PETG for all parts. Not PLA (too brittle for snap features, poor moisture resistance). Not ABS/ASA (unnecessary for indoor kitchen use, warping risk on the tray). PETG gives the right balance of toughness, printability, and slight flex for snap-fit features.

**Critical tolerances:**
- Release plate stepped bores (6.5 / 9.8 / 15.5 mm) — tightest feature in the design. The 6.5 mm through-hole has only 0.19 mm engagement lip per side against the collet ID. Print at 0.1 mm layers, verify with a test print before committing to the full plate.
- T-rail tongues — 0.3 mm clearance per side against dock channels. Standard FDM tolerance.
- Fitting press-fit bores (9.5 mm for 9.31 mm center body) — 0.19 mm interference. Achievable with PETG's slight compliance.
- Guide post bores (3.7-3.8 mm for 3.5 mm posts) — 0.2-0.3 mm clearance. Standard.

**No part exceeds 160 mm in any dimension.** The tray at 160 x 155 x 72 mm is well within the 325 x 320 x 320 mm build volume. All parts can print one at a time or batched (the lid, bezel, release plate, and floor plate could share a single print bed).
