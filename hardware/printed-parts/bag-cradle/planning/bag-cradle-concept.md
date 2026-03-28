# Bag Cradle — Conceptual Architecture

## The Design

Each bag cradle is a single-piece shallow rectangular tray printed in PETG, tilted 15-20 degrees by the enclosure's snap-fit rail geometry. The cap end sits at the gravitational low point (back-bottom of enclosure). The sealed end of the bag rests at the high point (toward the front wall). Two identical cradles mount one above the other on angled rails molded into the enclosure's interior side walls. The bag simply lies in the tray under gravity. No clips, straps, or fasteners touch the bag.

---

## 1. Piece Count and Split Strategy

**One piece per cradle. Two cradles total (identical).**

The tray footprint is approximately 210 x 370 mm (bag plus clearance). The H2C single-nozzle bed is 325 x 320 x 320 mm. The 370 mm length exceeds the 320 mm bed dimension by 50 mm, so the tray cannot print flat in its longest orientation.

**Resolution: print diagonally.** The bed diagonal is approximately 456 mm. A 210 x 370 mm tray placed at roughly 40 degrees on the bed fits within the 325 x 320 mm rectangle. The tray is shallow (sidewalls 25-30 mm), so the 320 mm Z limit is irrelevant. Diagonal placement does waste some bed area, but the part is a single continuous print with no seams, no fasteners, and no assembly. That tradeoff is worth it.

If diagonal placement proves too tight with skirt/brim margins, the fallback is a two-piece tray split across the width at the midpoint, joined by a printed tongue-and-groove snap along the split line. But start with one piece.

## 2. Join Methods

**Snap-fit lateral rails on the enclosure walls.**

Each tray has a tab running along each long edge (left and right sides). These tabs slide into horizontal rail channels molded into the enclosure's interior walls. The rails are angled at the mounting angle (15-20 degrees from horizontal), so the tray's tilt is defined entirely by the enclosure geometry -- no shims, no angle adjustment.

Each tab is approximately 2.8 mm thick with a small barb that clicks past a detent at full insertion, providing positive retention. To remove, the user presses the tab inward (deflecting it ~1 mm) to clear the detent and slides the tray out toward the front of the enclosure.

Two rails per tray, one on each enclosure side wall, distribute the 2 kg liquid load along the full tray length and prevent rocking. The back (low) end of each rail should have a reinforced wall section on the enclosure, since the weight concentrates there.

## 3. Seam Placement

**No seams in the single-piece version.** The tray is one continuous print.

If the two-piece fallback is needed, the split line runs across the width at approximately the midpoint of the tray length. This seam is on the interior floor of the tray, hidden under the bag. It has no visual or functional consequence -- the bag rests on top of it, and liquid does not pass through the tray (the tray is not a sealed vessel).

Either way, seams are a non-issue. This is an interior part that lives inside a closed enclosure. The user sees it only during bag installation, and then only briefly.

## 4. User-Facing Surface Composition

The user interacts with the cradle during one operation: installing or removing a bag. During that operation, the user sees and touches:

- **Tray interior floor:** a gently concave surface (shallow curve across the 210 mm width) that centers the bag. The concavity is subtle -- maybe 3-5 mm of dish across the full width. The floor is otherwise flat along its length.
- **Tray sidewalls:** 25-30 mm tall, slight outward draft for easy bag placement. The sidewalls contain the bag laterally but do not grip it.
- **Cap channel:** the cap end of the tray has no end wall. Instead, the floor extends 15-20 mm past the bag body and terminates in a semicircular notch (~32 mm diameter) that accommodates the Platypus spout collar. The spout and tubing exit through this open end, pointing downward.
- **Tab edges:** the snap-fit tabs along the long sides are visible but utilitarian. They read as structural flanges, not decorative elements.

The user never touches the tray's underside or the rail interface. Those surfaces are purely structural.

## 5. Design Language

**Functional print quality is appropriate. No finishing required.**

This is an interior part inside an enclosed appliance. The user opens the enclosure, drops in a bag, and closes it. The cradle does not contribute to the product's external appearance. Layer lines, slight surface roughness, and visible infill patterns on the underside are all acceptable.

That said, the tray interior floor (the one surface the user looks at during installation) should be printed face-up so the top surface gets the smoothest finish. This is also the natural print orientation (tray open-side-up), so no conflict with manufacturability.

Material color: match the enclosure interior. If the enclosure is printed in black PETG, the cradles should be black PETG. Visual consistency matters even for interior parts, because the user sees the cradle and enclosure walls together during bag installation.

## 6. Service Access Strategy

**Front-loading. The tray slides in and out from the front of the enclosure.**

The enclosure's front panel (or a hinged/removable section of it) provides access to the bag compartment. The user reaches in, slides the tray forward to disengage the rail detents, and pulls it out. Bag replacement can be done with the tray removed (easiest) or with the tray in place (lay bag in from above if there is clearance above the tray).

**Bag installation sequence:**
1. Slide tray out (optional but easier).
2. Lay bag in tray, spout-end first into the cap channel.
3. Let the bag body settle into the tray floor.
4. Route tubing through the printed clip on the tray underside, down to the pump/valve manifold.
5. Slide tray back into rails until it clicks.

**Bag removal:** reverse the sequence. Disconnect tubing at the quick-connect downstream of the spout. Lift bag by sealed end. Spout slides out of the open channel.

The upper cradle is accessed the same way as the lower. The rail positions are staggered so the upper tray clears the lower tray during insertion/removal. If front access proves too tight, the alternative is top access through the funnel area, but front access is strongly preferred because it matches the slide-in rail axis.

## 7. Manufacturing Constraints

**Print orientation:** open-side-up (tray sitting normally on the bed). This puts the smooth top surface on the tray interior floor and requires zero supports. The sidewalls print as vertical walls, the floor prints as flat layers, and the snap-fit tabs print as horizontal extensions of the sidewalls.

**Supports:** none required. The tray is an open-top shape with no overhangs exceeding 45 degrees. The cap channel notch is a semicircle cut into the floor edge, not a bridge. The concave floor curvature is gentle enough (3-5 mm dish over 210 mm width) to print without support.

**Bed fit:** 210 x 370 mm tray printed diagonally on a 325 x 320 mm bed. The diagonal of the bed is ~456 mm. The tray diagonal is ~425 mm. It fits, but with modest margins. A test print of the bounding rectangle should confirm clearance with brim/skirt.

**Material:** PETG. Better creep resistance than PLA under constant 2 kg load in a potentially warm under-sink environment. Prints well on the H2C without enclosure. No special settings needed beyond standard PETG profile (bed 70-80C, nozzle 230-250C).

**Wall thickness:** 2.5-3 mm for the tray floor and sidewalls. This provides adequate stiffness for the 2 kg load without excessive print time. The snap-fit tabs can be thinner (2 mm body + 0.8 mm barb).

**Print time estimate:** roughly 3-4 hours per tray at 0.2 mm layer height, 15-20% infill, 3 walls. Two trays total, so 6-8 hours of print time for the pair.
