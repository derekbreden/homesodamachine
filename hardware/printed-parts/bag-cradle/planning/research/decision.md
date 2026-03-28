# Bag Cradle Design Decision

## Recommendation: Tilted Shallow Tray with Open Cap Channel

The cradle is a shallow, wide tray tilted so the cap end is the gravitational low point. The bag sits in the tray under gravity. The cap end of the tray has an open channel that lets the spout and tubing exit without bending. No active compression, no springs, no clips on the bag itself.

---

## 1. Support Geometry

**A shallow rectangular tray with gently curved floor, not contoured to the bag.**

The tray interior is approximately 200 mm wide (10 mm clearance on the 190 mm bag) and 360 mm long (10 mm clearance on the 350 mm bag). The floor has a gentle concave curve across the width — just enough to keep the bag centered and prevent it from sliding side-to-side. This is not a lens-shaped cradle matched to the bag's cross-section; it is a wide, shallow dish.

**Why generic, not contoured:**
- The research is clear: generic supports work for flexible bags (BIB racks, GOJO housing, Kangaroo hook). Contouring solves the insertion problem, not the drainage problem.
- A contoured cradle matched to a full bag would fight the bag as it empties and changes shape. The bag needs freedom to collapse naturally.
- A generic tray accepts manufacturing variation in bag fill level and shape.
- Simpler to print: a shallow tray with gentle curvature is one continuous surface, no thin walls or undercuts.

**Sidewall height:** 25–30 mm. Tall enough to contain the bag at its thickest (the low/cap end will bulge to 40–50 mm, but the bag spreads wider than the tray floor so the sides just keep it from rolling off). Not so tall that installing the bag is difficult.

---

## 2. Mounting Angle

**15–20 degrees from horizontal, cap end lower.**

This is the vision's "diagonal" mounting interpreted conservatively. At 15–20 degrees:
- Gravity pulls liquid toward the cap/outlet reliably. Even at 15 degrees, a 350 mm bag has a 90 mm elevation drop from sealed end to cap end — more than enough to migrate liquid.
- The bag stays in the tray under its own weight. No risk of sliding out (friction of soft film on printed surface is high, and the tray sidewalls contain it).
- Two bags stacked at this angle inside a 400 mm tall enclosure leaves room for the funnel above and pump cartridge below.
- Steeper angles (30+) would work for drainage but waste vertical space and risk the bag sliding toward the cap end aggressively, bunching up.

**Why not vertical hanging (the dominant small-bag pattern):**
- The vision places two bags one above the other inside a 220 x 300 x 400 mm enclosure. Hanging two 350 mm bags vertically requires 700 mm of height before you account for the funnel, displays, or pump. The enclosure is only 400 mm tall.
- The tilted tray stacks two bags in about 200 mm of vertical space (two trays, each roughly 60 mm tall including bag, offset diagonally), leaving 200 mm for everything else.

---

## 3. Outlet / Cap End Treatment

**An open-ended channel that lets the spout protrude past the tray edge.**

The cap end of the tray does not have a wall. Instead, the tray floor extends about 20 mm past where the bag body ends and then terminates. The spout and attached tubing hang off the end of the tray, pointing downward (since the cap end is the low point). A semicircular notch (30–35 mm diameter) in the tray floor at the cap end accommodates the spout collar so the bag can sit flat without the spout lifting the bag off the tray surface.

**Kink prevention:** The tubing exits the spout pointing in the same direction gravity is pulling — downward and toward the back of the enclosure. There is no bend required. The tubing routes straight down from the spout to the pump/valve manifold below. The key principle from the research: tubing should exit near the support structure, not traverse a long unsupported span.

A printed tubing guide clip on the underside of the tray routes the tube along the tray's structural ribs to the enclosure wall, preventing any unsupported span where the tube could snag or kink during bag installation.

---

## 4. Drainage

**Gravity to outlet at the low point, assisted by the peristaltic pump's suction.**

This system has both mechanisms the research identified:
- The 15–20 degree tilt ensures the cap/outlet is the gravitational low point (Theme 1 from the research).
- The peristaltic pump provides active suction (Theme 3), which compensates for any residual pooling.

**Anti-collapse at the outlet:** The Platypus spout is a rigid 28 mm threaded collar. Unlike the Scholle IPN BIB fitments that need textured anti-collapse features, the Platypus spout's rigid collar holds the bag film away from the opening for the first 15–20 mm. Combined with pump suction, this should be sufficient. If testing reveals film collapse blocking the spout at low fill levels, the mitigation is a small printed insert (a star-shaped or cross-shaped spacer) that threads into the 28 mm opening and keeps the film from sealing over the port. This is a contingency, not part of the initial design.

**Last-drop performance:** The tilted tray means the last liquid pools directly at the spout. The bag film collapses from the high (sealed) end toward the low (cap) end, which is exactly the right direction. No liquid gets trapped at the far end of the bag.

---

## 5. Installation

**Lay the bag in the tray, spout-end first. Route the tubing. Done.**

1. User holds the bag by the sealed end (top, which is the high/front end of the tray).
2. Lowers the spout end into the tray's cap channel, letting the spout drop through the open end.
3. Lays the rest of the bag down into the tray.
4. Routes tubing through the clip on the tray underside.

**Removal:** Disconnect tubing from the downstream fitting. Lift the bag by the sealed end. The spout end slides out of the open channel.

**No clips, latches, or fasteners touch the bag.** The bag sits in the tray under gravity. The tray sidewalls prevent it from rolling out. The tilt angle and friction prevent it from sliding. This matches the BIB rack pattern (box sits on shelf, gravity holds it) and is the simplest possible installation.

**Why no retention mechanism:** The bag is inside an enclosed appliance. It is not subject to jolts, vibration, or inversion. Gravity is sufficient. Adding clips or straps would complicate installation and create pinch points on the thin film.

---

## 6. Attachment to Enclosure

**Snap-fit rails on the enclosure interior walls.**

The tray has two lateral tabs (one on each long side) that slide into horizontal rail channels molded into the enclosure's inner walls. The rails are angled at the 15–20 degree mounting angle so the tray is tilted correctly by the rail geometry alone — no angle adjustment, no loose parts.

**Rail design:** Each rail is a horizontal slot (approximately 3 mm wide, 5 mm deep) running front-to-back on the enclosure interior wall. The tray tabs are 2.8 mm thick with a slight barb that snaps past a detent at the fully-inserted position, providing positive retention with tool-free removal (push tab inward to release detent, slide tray out).

**Why rails instead of posts, screws, or adhesive:**
- Rails align with the vision's snap-fit assembly philosophy (everything assembles by pressing together).
- Rails distribute load along the full length of the tray, which matters when supporting 2 kg of liquid.
- The slide-in motion is natural: user slides the tray in from the front (or top, depending on enclosure access), same axis as bag installation.
- Two rails, one on each side, prevent any rocking or rotation of the tray.

**Structural consideration:** The tray supports 2 kg of water concentrated at the low end. The rail attachment at the low (back) end of the tray bears most of this load. The enclosure wall at this point should have a reinforcing rib or thickened section to handle the concentrated load without creep over time (PETG or ABS recommended for the enclosure walls near the rail mounts).

---

## Material Recommendation

**PETG for the tray.** It has better long-term moisture resistance than PLA, adequate stiffness, and prints well on the H2C. PLA would work short-term but may creep under constant 2 kg load in a warm under-sink environment. ABS or ASA are also fine but offer no advantage over PETG here and are harder to print.

---

## What Would Change This Recommendation

1. **The enclosure turns out to be significantly smaller than 220 x 300 x 400 mm.** If vertical space shrinks below 350 mm, the tilted tray approach may not leave room for two bags plus the funnel and pump. The mitigation would be steeper tilt (trading horizontal footprint for vertical), or switching to a vertical hanging arrangement that requires a taller, narrower enclosure.

2. **The Platypus bag film seals over the spout at low fill.** If testing shows the pump cannot draw the last 10–20% of liquid because the film collapses onto the spout opening, the anti-collapse insert (threaded star spacer) becomes a required part rather than a contingency. This would add one small printed part per bag.

3. **The user cannot access the tray from the front or top of the enclosure.** The slide-in rail system assumes the tray can be inserted along its long axis. If the enclosure opens only from the side or has obstructions, the rail orientation would need to change, or the attachment would switch to vertical drop-in posts.

4. **The bag needs to be compressed to increase flow rate.** The current design relies on gravity plus pump suction, which should be adequate for flavoring (small volumes, not time-critical). If higher flow rates are needed (e.g., for the cleaning cycle fill), a hinged compression lid could be added to the tray. This would be a significant complexity increase and should only be pursued if testing shows flow rate is insufficient.

5. **The 28mm cap interface changes.** The spout notch and tubing routing assume the Platypus 28mm threaded spout. If a different bag is used (different spout size, spout on the side instead of the end), the cap channel geometry would need redesign but the tray concept remains the same.
