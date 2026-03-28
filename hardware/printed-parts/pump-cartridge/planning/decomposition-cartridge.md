# Pump Cartridge — Sub-Component Decomposition

Step 6d evaluation for all 5 cartridge printed parts.

---

## Part 1: Cartridge Tray — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-cartridge.md.**

**Rationale:** Despite being the most complex part in the assembly, the cartridge tray is a single geometric paradigm: prismatic extrude-and-cut with cylinder unions. Every feature falls into one of these categories:

- **Box/U-shape body** — extrude a rectangle, cut the interior to form walls and floor. Pure 2.5D.
- **Pump pockets** — rectangular cuts from the top (open-top pockets). Prismatic.
- **Fitting bores** — cylindrical through-holes in the rear wall, drilled along Y. Prismatic cuts.
- **Entry funnels** — conical countersinks around each bore on the outboard face. Revolved profiles cut from the rear wall, but each is a simple cone-to-cylinder transition — achievable with a revolved cut profile, which CadQuery handles natively.
- **Registration boss sockets** — tapered blind holes in the rear wall. Same technique as entry funnels (revolved profile cut).
- **Motor nub pockets** — cylindrical blind holes in the rear wall inner face. Simple cuts.
- **Guide posts** — cylinders protruding from the rear wall outboard face. Union of cylinders.
- **Heat-set insert bosses with standoff ribs** — cylinders on the floor + rectangular rib extrusions connecting them to bracket height. Cylinder unions + box unions.
- **Push rod channels** — U-groove cuts along the inner faces of the side walls. Rectangular prismatic cuts.
- **Push rod transfer slots** — rectangular through-slots in the rear wall. Prismatic cuts.
- **Rail ribs** — rectangular extrusions on the outer side walls. Prismatic additions.
- **Lever bearing holes** — cylindrical blind holes in the side walls. Prismatic cuts.
- **Lid detent ridges** — small rectangular protrusions on outer side walls. Prismatic additions.
- **Bezel snap tab pockets** — small rectangular recesses. Prismatic cuts.
- **Electrical contact pad pockets** — shallow rectangular recesses on the outboard face. Prismatic cuts.

No feature requires sweeps, lofts, helical geometry, or multi-axis curved surfaces. The revolved profiles (funnels, sockets) are axially symmetric around the bore center axis (parallel to Y), which is a single-paradigm operation in CadQuery using the revolved-profile-cut technique documented in the STEP generation standards.

All features are tightly coupled to the tray body — the rear wall bores, funnels, sockets, guide posts, and transfer slots all share the same 8.5 mm wall. The side walls contain bearing holes, channels, ridges, and ribs that reference the same wall surfaces. Decomposing would create problematic composition boundaries through the wall thickness.

The feature count is high (~20 distinct features), but each is a straightforward extrude, cut, or cylinder union. A well-structured CadQuery script with clear sections (one per feature) and the mandatory feature planning table will manage this complexity. The validation suite (point-in-solid probes for every feature) provides the safety net.

---

## Part 2: Cartridge Lid — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-cartridge.md.**

**Rationale:** The lid is a flat plate (140 x 121 x 4 mm) with four cantilever snap-fit hooks extending from the perimeter edges. This is a single geometric paradigm:

- **Plate body** — box extrusion.
- **Snap-fit hooks** — thin rectangular cantilever arms extending downward from plate edges, with 45-degree lead-in ramps at the tips. Each hook is a small box + angled cut at the tip. Prismatic.

Total feature count: 5 (plate + 4 hooks). Trivially within a single CadQuery agent's scope.

---

## Part 3: Lever — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-cartridge.md.**

**Rationale:** The lever combines a flat paddle, two pivot stubs, two cam lobes, and a detent spring tab. All features are either prismatic (paddle, tab) or cylindrical (stubs, cam discs):

- **Paddle face** — flat rectangular plate, 120 x 40 x 4 mm. Extrude-and-cut with a fillet on the grip edge.
- **Pivot stubs** — two cylinders (6 mm diameter, 5 mm long) at each end. Cylinder unions.
- **Cam lobes** — two eccentric discs (8 mm radius, 4 mm thick) positioned inside the pivot stubs. Cylinder unions placed at the eccentric offset from pivot center.
- **Detent spring tab** — thin cantilever (12 x 2 x 1.5 mm) extending from the paddle bottom edge. Rectangular extrusion with a rounded tip.
- **Structural bar** connecting paddle to cam/pivot regions — prismatic or cylindrical sections along X.

No sweeps, lofts, or helical geometry. The cam lobes are simple offset cylinders, not involute cams or complex profiles. The eccentric offset (3 mm in +Z from pivot center) is just a translated cylinder.

Total feature count: ~7. All prismatic/cylindrical. Well within a single agent's scope.

---

## Part 4: Release Plate — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-cartridge.md.**

**Rationale:** The release plate is a flat plate (120 x 50 x 3 mm) with four stepped through-bores and two edge guide slots. This is the textbook example of a single-paradigm part:

- **Plate body** — box extrusion.
- **Stepped bores (x4)** — revolved profile cuts (3-stage stepped bore: tube clearance, collet hugger, body end relief). CadQuery's revolved profile technique handles this directly.
- **Guide slots (x2)** — rectangular edge slots open on the plate edge. Prismatic cuts.
- **Transfer tabs (x2)** — small rectangular protrusions on the rear face. Box unions.

Total feature count: 9. All prismatic or revolved-profile. Trivially within scope.

---

## Part 5: Front Bezel — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-cartridge.md.**

**Rationale:** The bezel is a rectangular frame (140 x 5 x 70 mm) with a central cutout, detent notches, and snap tabs:

- **Frame body** — box extrusion.
- **Lever paddle cutout** — rectangular through-cut with a 0.5 mm rebate step around the perimeter. Two prismatic cuts (outer cut-through + rebate pocket).
- **V-notches (x2)** — small V-shaped cuts on the inner face. Prismatic cuts (triangular cross-section extruded along Y or simple angled cuts).
- **Snap tabs (x2)** — small rectangular protrusions. Box unions.
- **Corner fillets** — standard CadQuery fillet operations on edges.

Total feature count: ~8. All prismatic. Trivially within scope.

---

## Summary

| Part | Decision | Rationale |
|------|----------|-----------|
| 1. Cartridge Tray | PASS THROUGH | All features are prismatic/cylindrical (extrude, cut, cylinder union). High feature count but single paradigm throughout. Tight geometric coupling across wall surfaces makes decomposition counterproductive. |
| 2. Cartridge Lid | PASS THROUGH | Flat plate + 4 snap-fit hooks. Trivially simple. |
| 3. Lever | PASS THROUGH | Paddle + stubs + eccentric discs + tab. All prismatic/cylindrical. |
| 4. Release Plate | PASS THROUGH | Flat plate + stepped bores + edge slots + tabs. Textbook single-paradigm part. |
| 5. Front Bezel | PASS THROUGH | Rectangular frame + cutout + notches + tabs. Trivially simple. |

All 5 parts proceed directly to Step 6g (STEP generation) with the full parts-cartridge.md specification. No sub-component decomposition is needed for any part in this assembly.
