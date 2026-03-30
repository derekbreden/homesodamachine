# Cartridge Build Sequence

Each **step** is one pipeline run producing one STEP file or one modification to an existing STEP file. Each step is the simplest possible thing. Steps are grouped into **phases** (the big arcs of progress). Phases are grouped into **seasons** (the major shifts in what kind of work we're doing).

---

## Season 1: Interior Plates

The flat surfaces inside the cartridge. Each one is a flat panel with holes. Nothing connects to anything else yet.

### Phase 1: Make the plates

1. **Release plate** — flat plate with stepped bores for 4 collet interfaces, 2 guide pins. DONE.
2. **Pump tray** — flat plate with holes for mounting 2 Kamoer KPHM400 pumps (4 screws each, 8 holes total).
3. **Coupler tray** — flat plate with holes/pockets for capturing 4 John Guest union couplers.
4. **Lever** — flat plate with 4 struts extending from it.

### Phase 2: Connect the plates to each other

5. **Release plate v2** — update release plate from 2 struts to 4 struts.
6. **Join lever struts to release plate struts** — design and print the tapered dovetail + snap detent joint between lever struts and release plate struts. This is where the joinery research gets applied.
7. **Test the squeeze mechanism by hand** — lever + struts + release plate, assembled, held together by nothing but the strut joints. Verify it translates, verify the release plate presses collets, verify the lever sits where fingers can reach it. No enclosure, no walls, just the mechanism in your hands.

### Phase 3: Split and rejoin the coupler tray

8. **Split coupler tray into two halves** — determine the split line that allows the couplers to be inserted. Produce two STEP files.
9. **Add dovetail geometry to coupler tray halves** — the tapered dovetail slide that joins them.
10. **Add snap detent to coupler tray halves** — the prong barbs that lock the halves permanently.
11. **Print and test coupler tray assembly** — two halves snap together, couplers are captured, shoulders provide axial retention.

### Phase 4: Add strut bores to interior plates

12. **Add strut bores to pump tray** — 4 holes sized to the strut cross-section, positioned so the struts pass through cleanly.
13. **Add strut bores to coupler tray** — same, but the coupler tray is two halves, so the bores must align across the split line (or be entirely on one half).
14. **Full interior dry fit** — lever + struts + release plate, passing through pump tray and coupler tray. Everything held in alignment by the bores. Verify the mechanism still translates smoothly with all interior plates present.

---

## Season 2: Walls

The 6 flat panels that form the cartridge box. Each one is a flat panel. The side walls get rails, everything else is just flat with maybe a hole or two.

### Phase 5: Make the walls

15. **Left wall** — flat panel, correct outer dimensions. Protruding rails on the interior face for: front panel, back panel, bottom panel, top panel, pump tray, coupler tray. Rails are the only features. No detents, no retention.
16. **Right wall** — mirror of left wall.
17. **Back panel** — flat panel with 4 holes for tube stubs. Outer dimensions sized to fit the left/right wall rails.
18. **Front panel** — flat panel with rectangular hole in lower half. Outer dimensions sized to fit the left/right wall rails.
19. **Bottom panel** — flat panel, no features. Outer dimensions sized to fit the left/right wall rails.
20. **Top panel** — flat panel, no features. Outer dimensions sized to fit the left/right wall rails. This is the last piece that goes in during assembly.

### Phase 6: Test fit the box

21. **Print all 6 panels and slide them together** — verify everything fits the rails, verify the box holds its shape by gravity and friction alone. Nothing locks. Panels may slide back out. That's fine.
22. **Slide interior plates into the assembled box** — verify pump tray and coupler tray fit their rails inside the box. Verify the mechanism (lever + struts + release plate) still translates with the walls present.
23. **Full assembly dry fit** — everything together for the first time. Interior mechanism, interior plates, all 6 walls. Identify what doesn't fit, what binds, what needs clearance.

### Phase 7: Front and back panel features

24. **Refine front panel hole** — after dry fit, adjust hole position and size so the user's fingers actually reach the lever comfortably. This may take multiple prints.
25. **Refine back panel holes** — after dry fit, verify tube stubs actually pass through and reach the quick connects with the release plate in its resting position.

---

## Season 3: Joinery

Nothing new gets designed. Everything that exists gets joined properly so it stays together.

### Phase 8: Wall-to-wall retention

26. **Add detent geometry to left wall rails** — tapered dovetails or snap detents on the rails so the front, back, bottom, and top panels lock at end of travel.
27. **Add matching detent geometry to front, back, bottom, top panels** — the receiving features for the wall detents.
28. **Print and test wall retention** — panels click in, don't slide back out. Iterate on tolerances.

### Phase 9: Interior plate retention

29. **Add detent geometry to interior plate rails** — pump tray and coupler tray lock into their side wall rails.
30. **Print and test interior plate retention.**

### Phase 10: Strut bore refinement

31. **Add bosses around strut bores in pump tray** — reinforce the bores now that we know the exact strut dimensions and clearances from prototyping.
32. **Add bosses around strut bores in coupler tray** — same.
33. **Print and test mechanism with bosses** — verify the added material doesn't bind the struts, verify alignment is tighter.

---

## Season 4: Refinement

Everything works mechanically. Now make it feel like a product.

### Phase 11: Cosmetics and UX

34. **Front panel exterior surface treatment** — the palm-push surface the user touches. Texture, radii, visual design.
35. **Lever surface treatment** — the finger-pull surface. Smooth or lightly textured for finger comfort.
36. **Side wall exterior surface treatment** — the surfaces visible when the cartridge is partially ejected from the enclosure.
37. **Cartridge-to-enclosure track refinement** — the exterior protruding tracks on the side walls that ride in the enclosure bay channels. Smooth sliding, correct clearances.

### Phase 12: Spring return and final mechanism tuning

38. **Add spring pockets** — wherever the return springs end up living (TBD based on interior plate positions and available space).
39. **Tune squeeze force** — adjust spring rate, strut friction, bore clearances so the squeeze feels right.
40. **Final full assembly test** — everything together, mechanism works, panels locked, cartridge slides in and out of enclosure bay (once the enclosure bay exists).

---

## What is NOT in this sequence

- The enclosure (the outer device housing) — that's a separate build sequence
- The bag cradle system — separate
- Electronics mounting — separate
- Valve mounting — separate
- Any part that is not the pump cartridge
