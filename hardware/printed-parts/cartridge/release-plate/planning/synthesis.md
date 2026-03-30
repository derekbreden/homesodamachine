# Release Plate Mechanism — Design Synthesis

**Sources synthesized:** design-patterns.md, collet-release-force.md, guide-geometry.md, john-guest-union geometry, kamoer-kphm400 geometry, requirements.md, vision.md

---

## 1. The Mechanism from the User's Perspective

The user approaches the cartridge with one hand, palm up. The palm presses flat against the front face of the cartridge body — a matte surface with light embossed texture (0.3–0.5mm raised diamond or hex pattern, 0.4mm tall minimum to hit the FDM printability floor). The fingers curl upward and contact a surface that is inset into the front face — not a button sitting proud of the body, not a lever sticking out, just a recessed pull zone that the finger pads naturally find when the hand assumes this posture. The user squeezes: palm pushes, fingers pull. Resistance builds over roughly 5–6mm of pull travel. At about 6mm, four simultaneous clicks transmit through the cartridge body and into the palm. The resistance drops sharply. The user's hand continues the motion, pulling the cartridge forward out of the bay on its protruding tracks.

From outside, the cartridge shows: a matte-textured front face with one inset pull zone occupying most of the face width, four barely-visible tube holes on the rear face, and protruding tracks on both sides that ride in matching channels in the enclosure bay. Everything else is inside.

When the user pushes a new cartridge in, it slides on the tracks until the four tube stubs in the enclosure's dock enter the quick-connect fittings on the cartridge rear wall. The cartridge snaps the final 3–5mm home (via a dock snap feature — addressed in the cartridge body specification, outside this document's scope), the front face aligns flush with the enclosure face, and the click confirms full seating. The user does not interact with the collets or the release plate at all during insertion.

---

## 2. The Mechanism from the Mechanical Perspective

### What moves and what is fixed

**Fixed:** The cartridge body rear wall, which holds four John Guest PP0408W fittings pressed into it via their 9.31mm central bodies. The rear wall is the structural anchor for the entire mechanism.

**Moving:** The release plate — a single flat PETG plate that translates forward (toward the user) by up to 3mm along two guide pins, simultaneously pressing the rear-facing collets of all four fittings inward (toward the back of the cartridge, which is inward relative to the rear-facing port).

**Orientation clarification:** The fittings are mounted in the rear wall with their long axes horizontal and perpendicular to the rear wall face (i.e., parallel to the cartridge's front-to-back depth axis). The dock tube stubs enter from the rear (outside the cartridge) and engage the rear-facing port of each fitting. The release plate is positioned between the front face of the cartridge and the fitting rear wall. The release plate's stepped bores face rearward, toward the fitting rear ends. When the plate translates forward, the plate's inner lips push the rear-facing collets forward (toward the user) — which is inward relative to the rear-facing port, releasing the dock tube stubs.

### Force flow

User finger pull force → release plate pull surface → plate body → inner lips on stepped bores → collet annular end faces → collet spring compression → collets depress → tube stubs release.

Simultaneously: user palm push force → cartridge body front face → cartridge body rigid structure → no movement (the body is fixed to the enclosure via its protruding tracks).

The net squeeze produces a clamping force between palm and fingers. The 60 N required to depress all four collets simultaneously (4 × 15 N design value) is comfortably within the capability of healthy adult users applying a one-time brief squeeze in the palm-up posture. The comfortable one-time squeeze force for the 5th–95th percentile adult range is 80–200 N, giving a 1.3×–3.3× margin with no mechanical advantage required.

### Spring return

After the user releases the squeeze, two compression springs — one at each guide pin boss — push the release plate back to its resting position, clearing the collets so they re-extend and are ready to grip tube stubs on re-insertion. Spring total return force: 2 N. This is imperceptible to the user during the squeeze (the spring opposes the pull with a force that is 3% of the collet release force at peak).

---

## 3. Critical Dimensions

All values are derived directly from the research documents.

### Plate travel and stroke

| Parameter | Value | Source |
|---|---|---|
| Collet travel per side (PP0408W) | 1.33mm | John Guest geometry, caliper-verified |
| Required plate travel (with margin) | 2.3mm minimum | collet-release-force.md Section 5 |
| Designed plate travel | 3.0mm | 0.7mm margin over minimum |
| Manufacturing variation allowance built into margin | 0.3mm collet protrusion + 0.3mm fitting coplanarity | collet-release-force.md Section 5 |

### Stepped bore geometry (per fitting, 4 identical bores)

The stepped bore is a three-diameter concentric feature machined into the release plate face that faces the fittings. From outermost to innermost (front of plate to rear of plate):

| Feature | Designed diameter | Rationale |
|---|---|---|
| Outer bore (clears body end, 15.10mm OD) | 15.6mm | 15.10mm + 0.5mm FDM clearance allowance |
| Inner lip bore (hugs collet, 9.57mm OD) | 10.07mm | 9.57mm + 0.5mm FDM clearance allowance |
| Tube clearance hole (passes through plate) | 6.50mm | Between 6.30mm tube OD and 6.69mm collet ID; 0.20mm over tube, well within 0.39mm design window |

**Outer bore depth (the counterbore that admits the body end before contact):** 1.3–1.5mm. This depth sets the over-travel stop: at resting position (collet extended), the body end shoulder (15.10mm OD annular ring) sits 1.3–1.5mm away from the outer bore face. At full collet depression (1.33mm travel), the outer bore face contacts the body end shoulder. The fitting's own body shoulder becomes the hard stop. No separate stop feature needed.

**Inner lip axial depth (the bore section that hugs the collet OD):** 2.0mm minimum. This depth keeps the collet square during the full 1.33mm depression stroke, preventing collet canting that would cause incomplete tube release.

**Summary of bore step depths from rear face of plate:**

- Zone 1 (outer bore, 15.6mm diameter): 1.3–1.5mm deep — admits body end, provides over-travel stop surface
- Zone 2 (inner lip, 10.07mm diameter): continues inward 2.0mm beyond Zone 1 — hugs collet OD, prevents canting
- Zone 3 (tube clearance, 6.50mm diameter): through-hole — passes tube, contacts collet annular face at its inner edge

The collet annular face (from collet ID 6.69mm to collet OD 9.57mm, area = 36.8 mm²) is contacted by the plate material between Zone 2 and Zone 3 at the step transition. The bearing stress at this face is 0.41 MPa at design load — 17× below PETG compressive yield. No material concern.

### Guide pins

| Parameter | Value | Source |
|---|---|---|
| Pin diameter (designed) | 5.0mm | guide-geometry.md Section 2 |
| Bore ID in cartridge body (designed) | 5.5mm | guide-geometry.md Section 4 |
| Effective as-printed clearance per side | ~0.15mm | guide-geometry.md Section 4 |
| Minimum pin engagement length in bore | 28mm | guide-geometry.md Section 1 binding ratio |
| Pin length (plate face to tip) | ≥30mm | 28mm engagement + 2mm travel clearance |
| Bore depth in cartridge body | ≥30mm | matches pin length |
| Pin arrangement | Diagonal corners of plate | guide-geometry.md Section 3 |
| Max tilt from clearance play | 0.31° | guide-geometry.md Section 4 |

Pins are integral to the release plate (printed as one piece). Bores are integral to the cartridge body rear wall structure (printed as part of the body). No metal pins needed.

### Return springs

| Parameter | Value | Source |
|---|---|---|
| Spring count | 2 (one per guide pin) | guide-geometry.md Section 5 |
| Spring type | Cylindrical helical compression, music wire (302 SS) | guide-geometry.md Section 5 |
| Wire diameter | 0.3–0.4mm | guide-geometry.md Section 5 |
| Spring coil OD | 7–8mm | guide-geometry.md Section 5 |
| Free length | 8–10mm | guide-geometry.md Section 5 |
| Spring rate | ~0.7 N/mm per spring | guide-geometry.md Section 5 |
| Force at full deflection | ~1 N per spring, 2 N total | guide-geometry.md Section 5 |
| Spring pocket diameter in cartridge body | 8mm | guide-geometry.md Section 5 |
| Spring pocket depth in cartridge body | 10mm | guide-geometry.md Section 5 |

Springs seat in pockets in the cartridge body rear wall structure, concentric with or adjacent to the guide pin bores. The release plate face closes the pocket when assembled. No spring retention clip needed.

### Grip inset and UX geometry

| Parameter | Value | Source |
|---|---|---|
| Finger contact surface inset from body face plane | 10mm | design-patterns.md Section 3; blade ejector reference |
| Gap between pull surface perimeter and body face | 0.6–1.0mm, uniform, sharp edges both sides | design-patterns.md Section 1 |
| Pull surface position relative to body face | Inset 0.5–1.0mm (flush to slightly recessed, never proud) | design-patterns.md Section 1 |
| Pull surface width (proportion) | Fill most of cartridge front face width | design-patterns.md Section 1 Makita guidance |
| Pull edge chamfer/radius | 3mm radius on the rearward edge of the pull zone | design-patterns.md Section 3; cassette tape reference |
| Palm surface texture | Matte with 0.3–0.5mm raised diamond or hex emboss | design-patterns.md Section 3 |
| Pull surface texture | Smooth or very lightly textured — finger pads slide during curl | design-patterns.md Section 3 |
| Force to initiate travel | 10–20 N | design-patterns.md Section 2 |
| Peak force at 5–6mm travel | 15–60 N (spring + 4 collets) | collet-release-force.md Section 2; design-patterns.md Section 2 |
| Force drop at release | Sharp, 30–50% drop as collets clear their internal stops | design-patterns.md Section 2 Milwaukee M18 reference |
| End-of-travel | Outer bore contacts body end shoulder — firm stop, no free travel | guide-geometry.md Section 6 |

---

## 4. Release Plate Form

### Overall dimensions

The plate's outer dimensions are driven by: the 4-fitting arrangement (derived in Section 5 below), the guide pin placement outside the fitting pattern, and the 1.2mm structural wall minimum on all sides.

**Approximate plate dimensions: 75mm wide × 65mm tall × 5mm thick** (nominal; final dimensions resolve from the fitting arrangement layout in Section 5).

The 5mm thickness provides:
- Zone 1 outer bore: 1.3–1.5mm deep
- Zone 2 inner lip bore: 2.0mm deep (cumulative 3.3–3.5mm from rear face)
- Zone 3 tube clearance through-hole: remaining ~1.5mm
- Full through-plate path for tube clearance holes: the tube clearance hole (6.50mm) continues through the full plate thickness so tubes can pass freely

**Print orientation:** Plate face parallel to build plate (XY plane). This orients the layer lines parallel to the plate face, which is the correct orientation for the collet bores to print accurately and for the plate to resist the squeeze force in-plane (not across layers). The guide pins extend in the Z direction (upward from build plate) — verified as the correct orientation for pin strength per requirements.md.

### Stepped bore arrangement (4 bores)

See Section 5 for fitting spacing. The four bores are arranged to match the four fitting positions in the rear wall. Each bore is a concentric three-diameter feature as specified in Section 3.

### Guide pin bosses

Two cylindrical bosses (solid, integral to the plate) protrude from the front face of the plate, positioned at diagonally opposite corners — top-left and bottom-right (or top-right and bottom-left). Each boss:
- Diameter: 5.0mm
- Length from plate front face: 30mm minimum
- Wall at boss base: the boss must have ≥1.2mm of plate material between its base circle and the nearest stepped bore feature

The pins point toward the front of the cartridge (toward the user) and slide in bores in the cartridge body forward wall. This means the cartridge body must have sufficient depth forward of the fitting rear wall to accommodate 30mm of pin travel.

**Cartridge front-to-back depth constraint from pin length:** The pin length (30mm from plate front face) plus the plate thickness (5mm) plus the gap between the plate rear face and the fitting rear wall (set by the outer bore depth of ~1.5mm at rest) means the distance from the cartridge body front face to the fitting rear wall must be at least 30mm + 5mm + 1.5mm = 36.5mm. This is a constraint on the cartridge body depth specification.

### Pull surface connection

The front face of the plate (the face pointing toward the user) is the pull surface. It is not a separate component — it is the plate face itself. The user's finger pads contact this face directly. The face is smooth to lightly textured (low friction for finger curl). The perimeter of this face, where it meets the gap with the surrounding cartridge body face, has sharp edges (no fillet on the release plate side; the cartridge body side of the gap may have a subtle chamfer for appearance). The pull zone — the inset area the fingers actually contact — is the plate face itself, inset 10mm from the surrounding cartridge body face plane.

**How the inset is achieved:** The cartridge body front face protrudes forward 10mm relative to the plane of the release plate front face. The release plate travels within a pocket in the cartridge body that is 10mm deep, measured from the cartridge body front face plane to the release plate front face at rest. The gap between the plate perimeter and the pocket walls is 0.6–1.0mm uniform, creating the designed parting line.

The rearward edge of the pull zone (the edge the finger pads curl against when pulling) has a 3mm radius. This is the edge that bears finger pad pressure during the squeeze and must not feel sharp.

### Spring pocket locations

Two spring pockets in the cartridge body rear wall structure, one per guide pin position. Each pocket is 8mm diameter, 10mm deep, positioned concentric with or immediately adjacent to the guide pin bore. The spring sits loosely in the pocket; the plate front face closes it. No retention feature needed.

---

## 5. Fitting Arrangement in the Rear Wall

### Fitting count and assignment

Four PP0408W fittings: 2 pumps × (1 inlet + 1 outlet) = 4 fittings. The two pumps are side-by-side in the cartridge (Kamoer KPHM400: 62.6mm wide × 62.6mm tall × ~116mm deep). The rear wall of the cartridge contains the four fitting pockets.

### Pump pair horizontal footprint

Two pumps side by side: 2 × 62.6mm = 125.2mm total width, plus mounting clearance. The enclosure interior is 220mm wide. The pump pair occupies ~125mm + ~10mm clearance = ~135mm of the enclosure width, leaving ~85mm for tubing runs and structure. The cartridge itself is bounded by the enclosure width: maximum ~215mm (allowing for enclosure wall thickness).

### Fitting positions

Each pump has one inlet fitting and one outlet fitting. Both fittings for one pump are positioned in the rear wall at the pump's rear face zone. The two tube connectors on the KPHM400 front face exit offset from center (per the geometry doc: one above center, one below — or left/right). The inlet and outlet tubing runs from the pump head front face to the fitting ports in the rear wall. These runs are internal to the cartridge.

**Recommended fitting layout in rear wall:** Two fittings per pump, arranged vertically (one above center, one below) to match the pump's tube connector exit positions. Horizontal separation between the two pump columns: ~63mm center-to-center (pump width = 62.6mm, minimal inter-pump clearance).

**Fitting center positions (approximate, rear wall view, origin at rear wall center):**

| Fitting | Pump | Role | Approx. X | Approx. Z |
|---|---|---|---|---|
| A | Pump 1 (left) | Inlet | −31mm | +15mm |
| B | Pump 1 (left) | Outlet | −31mm | −15mm |
| C | Pump 2 (right) | Inlet | +31mm | +15mm |
| D | Pump 2 (right) | Outlet | +31mm | −15mm |

Horizontal center-to-center (A-to-C or B-to-D): 62mm. Vertical center-to-center (A-to-B or C-to-D): 30mm.

The release plate's four stepped bores match this 62mm × 30mm center-to-center rectangle.

**Minimum edge-to-edge bore clearance check:** The outer bore diameter is 15.6mm. The edge-to-edge distance between adjacent bores:
- Horizontal: 62mm c-c − 15.6mm = 46.4mm clear — no interference.
- Vertical: 30mm c-c − 15.6mm = 14.4mm clear — no interference.

Both directions have ample clearance. The release plate has robust material between adjacent bores.

### Rear wall fitting pockets

Each fitting is pressed into a pocket in the rear wall via its 9.31mm central body. The pocket geometry:

| Feature | Designed dimension | Rationale |
|---|---|---|
| Center body bore (press-fit) | 9.5mm | 9.31mm + 0.1mm for snug press fit per John Guest geometry doc; verify empirically |
| Center body bore (sliding fit for alignment during assembly) | 9.8mm | 9.31mm + 0.5mm; use if press is too tight for first prototype |
| Shoulder contact face | Flat annular ring on each side of bore | Provides axial location for the 15.10mm body end shoulders |
| Wall depth for center body | 12.16mm | Matches PP0408W central body length |

The rear-facing port of each fitting protrudes rearward from the rear wall face, accepting the dock tube stubs from the enclosure. The dock-side (rear) port collets are not activated by the release plate — they are the permanent dock interface, not user-actuated. The release plate activates the rear-facing collets of the fittings, which are the collets that grip the dock tube stubs. This is the correct configuration: pulling the release plate forward depresses the rear-facing collets, releasing the dock tube stubs.

**Rear wall thickness:** Must accommodate the 12.16mm central body length plus sufficient surrounding structure. Minimum rear wall thickness: 12.16mm + 1.2mm (front face structural wall) + 1.2mm (rear face structural wall) = 14.56mm. Round up to 15mm minimum rear wall thickness.

---

## 6. Conflicts with the Vision

### Conflict 1: "Both surfaces can be perfectly flat" vs. grip inset requirement

**Vision states (Section 3):** "both surfaces can be perfectly flat and that will still provide the satisfying user experience we seek."

**Research finding:** The HP/Dell blade ejector reference (design-patterns.md Section 3) establishes that fingertip-only contact on a shallow surface (2–4mm inset) produces fatigue and uncertain purchase. The minimum effective finger-pad contact depth is 8mm; the recommended target is 10mm. At 0mm inset (truly flat pull surface coplanar with the cartridge body face), the user has no grip surface — fingers would slide off the plate face with no edge to pull against.

**Conflict resolution:** The vision's intent — that the mechanism be invisible and that the grip require no visible hardware — is fully preserved. The modification is minimum: the release plate front face sits 10mm inset from the cartridge body face plane (i.e., inside a 10mm deep pocket). To the user this appears as one recessed zone on the front face, similar to the Makita battery's release panel that fills most of the face. The cartridge body face is the "palm surface" and the inset plate face is the "finger surface." Both are flat. The inset is the only departure from "perfectly flat" — but the vision's text also describes "both surfaces can be perfectly flat," implying a two-surface interaction is expected. A 10mm inset between two flat surfaces is the minimum geometry that makes this interaction work ergonomically.

**Proposed minimum modification:** The cartridge front face has one 10mm deep rectangular pocket occupying most of the face width and at least 30mm of face height. The release plate's front face is the floor of this pocket. Both exposed surfaces (pocket floor = pull surface; surrounding rim = palm surface) are flat. The pocket's rearward edge (the edge the finger pads curl against) has a 3mm radius. This is consistent with the vision's text: "both surfaces can be perfectly flat" describes the surfaces themselves, not their coplanarity.

### Conflict 2: Pin length vs. cartridge depth

**Finding:** The guide pins extend 30mm forward from the release plate front face. The cartridge body front wall must accommodate 30mm of pin bore depth ahead of the plate. Given that the plate itself sits 10mm inset from the cartridge front face, the pins must travel within the 10mm deep pocket region — they extend from the plate front face forward into the cartridge body front wall.

**Check:** The front wall of the cartridge (the wall that forms the pocket) must be at least 30mm thick to provide the full 30mm pin bore. However, the pocket depth is only 10mm (the inset depth). The pins cannot bore into the pocket depth — they must go rearward, not forward.

**Correction:** The pins must extend rearward from the plate rear face (toward the fittings), not forward. The plate translates forward when pulled; the pins (attached to the plate) slide in bores that go through the rear wall structure of the cartridge body rearward of the plate. The pins point toward the rear of the cartridge and are contained within the space between the plate and the fitting rear wall.

**Revised pin geometry:** Pins extend from the rear face of the release plate, pointing rearward. The plate translates forward by 3mm when squeezed; the pins simultaneously travel 3mm forward in their bores. The bores go from the release plate's resting position rearward for 30mm into the cartridge body's internal structure (the walls and intermediate structure between the plate and the fitting rear wall). This requires 30mm of structural depth between the plate resting position and the rear of the cartridge body.

**Constraint:** The total interior depth of the cartridge between the plate rear face (at rest) and the fitting rear wall face is:
- Outer bore depth (plate to body end): 1.5mm at rest
- The fittings extend 12.16mm rearward from the rear wall face into the cartridge interior (the rear-facing body end section)

The pins do not need to extend into the fitting zone — they can stop short of it. The 30mm bore depth runs from the plate resting position rearward through whatever intermediate cartridge body structure exists in that zone. The cartridge interior must be at least 30mm deep between the plate and the rear wall front face. Given the pump depth (~116mm) and the expected cartridge interior depth, 30mm of pin bore space behind the plate is achievable.

**No conflict with the vision.** This is a geometry constraint on the cartridge body specification (which is out of scope for this document), noted here so the cartridge body design accommodates 30mm of structural depth behind the release plate for pin bores.

---

## 7. Bill of Materials (Non-3D-Printed Parts)

| Item | Specification | Qty | Source |
|---|---|---|---|
| John Guest PP0408W 1/4" push-to-connect union | White acetal copolymer, 1/4" OD tubing, straight union | 4 | Plumbing/irrigation suppliers; John Guest distributor |
| Compression return spring | Music wire (302 SS), OD ~7–8mm, wire dia. 0.3–0.4mm, free length 8–10mm, rate ~0.7 N/mm | 2 | McMaster-Carr #9657K series or equivalent commodity spring supplier |
| M3 × 10mm socket head cap screws | Stainless steel, for pump mounting (4 per pump) | 8 | Standard hardware |
| M3 hex nuts | Stainless steel, if tray uses through-hole mounting | 8 (if needed) | Standard hardware |

**Notes:**
- The release plate and guide pins are one printed PETG part. No metal pins.
- The cartridge body (including rear wall with fitting pockets, guide pin bores, spring pockets, front pocket wall) is printed PETG.
- The pull surface and the plate body are one part — no adhesive, fastener, or hinge between them.
- The springs are the only commodity non-hardware parts for the release mechanism itself.

---

## 8. Open Questions

1. **Fitting pocket: press-fit vs. sliding fit.** The 9.5mm press-fit bore for the 9.31mm fitting central body needs empirical calibration on the actual printer. First print should include a test pocket at 9.5mm, 9.6mm, and 9.8mm to determine which provides secure retention without cracking the fitting body. If none achieves secure retention, a secondary retention feature (a snap arm or retaining lip over the body end shoulder) will be needed.

2. **Fitting pocket retention direction.** The dock tube stubs push the fittings forward (toward the user) during insertion and hold them in place under flow pressure. The press fit must resist this forward force. Confirm the press-fit axial retention force exceeds the dock stub insertion force before finalizing the bore diameter. If insufficient, add a forward-facing shoulder or snap clip on the fitting body end.

3. **Exact vertical positions of tube connector exits on KPHM400 front face.** The geometry doc describes them as "one above center, one below" but does not provide caliper-verified X/Z offsets. These positions determine the exact inlet/outlet fitting placement in the rear wall and must be measured before finalizing fitting layout. The ±15mm vertical offset assumed in Section 5 is a working assumption only.

4. **Exact pump tube connector geometry.** The KPHM400 tube connectors are barbed BPT fittings (4.8mm ID / 8.0mm OD) on the front face. The internal tubing run from pump front face to rear wall quick-connect fittings must route within the cartridge. This routing geometry is out of scope for this document but is a dependency for finalizing cartridge interior volume.

5. **Dock tube stub length.** The tube stubs in the enclosure dock that insert into the fittings must protrude enough to engage the John Guest gripper teeth (industry standard insertion depth ~16mm). Stub length and protrusion must be coordinated with the cartridge rear wall thickness and the fitting's rearward protrusion.

6. **Collet simultaneity tolerance.** The research notes that simultaneous engagement of all four collets requires fitting coplanarity within ~0.2mm and recommends empirical calibration of the latch hook heights (Zebra guidance from design-patterns.md). For the release plate, fitting coplanarity is set by the rear wall pocket depths. A calibration test — four fittings in the rear wall mockup, flat plate applied, tube release depth measured — should confirm the 0.7mm stroke margin before finalizing geometry.

7. **Cartridge body interior depth.** The constraint from Section 6 (30mm of pin bore depth behind the plate) must be verified against the cartridge body interior depth once the pump placement geometry is finalized. The pumps are ~116mm deep; the cartridge must accommodate the pumps plus the ~30mm release plate zone in its front region. Total cartridge interior depth: at minimum ~50mm front zone (release plate + pin bores + fitting depth) plus pump body. This is a cartridge body design constraint outside this document's scope.

8. **Grip pocket width vs. cartridge width.** The vision states the cartridge is in a 220mm wide enclosure. The grip pocket should fill "most of the face width" (design-patterns.md Makita guidance). A pocket spanning ~160mm of a ~200mm wide cartridge front face satisfies this. The exact cartridge width is not yet defined; the pocket width should be set as a proportion (~80% of face width) once the cartridge width is finalized.

9. **Snap-in dock feature.** The design-patterns.md research calls for a snap-in feature that actively draws the cartridge the final 3–5mm to full seating (SD card slot reference) and coincides with the tube engagement force peak (Nespresso reference). This feature is on the cartridge body/dock interface, not the release plate — but it is flagged here because it is essential to the seating UX and must be designed in the cartridge body specification.

10. **Spring sourcing verification.** The spring specification (OD 7–8mm, wire 0.3–0.4mm, free length 8–10mm) is a commodity part per the research, but specific catalog numbers should be verified before the BOM is treated as final. McMaster-Carr #9657K series is the cited reference; confirm availability and exact rate at the time of ordering.
