# Vision

## 1. Values

1. **This is a consumer product, a kitchen appliance.**

2. **User experience is paramount in all things.**

3. **Ease and simplicity of 3D printing and assembly is always the second consideration after UX**


## 2. An architecture the user imagines

- The outer enclosure is 220 mm x 300 mm x 400 mm
- It is printed in two halves, snapped together permanently. The user never opens the enclosure.
- Every single interior piece has specific snap connecting points on those outer two halves, so that the entire thing is assembled by pressing things together
- The 2L bags are mounted one above the other, diagonally, such that the "cap" is at the back and bottom of the enclosure, and the "top" of each bag is pinned flat against the front wall of the device
- The funnel is shaped to be directly on top of the bags
- The bags are each supported by their own lens shaped platform that fits their natural liquid filled shape, and are constrained from above identically, such they have no freedom of movement as they fill and unfill. Without this constraint, the bottom portion may rise to 40mm height, but with the constraint they remain at 25mm - 30mm more consitently throughout their midsection, and please remember, they are diagonal at 35 degrees, with the cap end down and the other end folded flat against the front wall
- The screens and air switch are in the middle of the front face, directly below the bags
- The pump cartridge is below those, at the front and bottom of the device
- The valves are behind the pump cartridge
- The electronics sit at the back and top of the device
- The back of the device has an inlet and outlet for the refrigerated carbonated water (simply to detect flow, but to make installation an obvious process instead of "attach this flow meter" it is "give us an input and we give you an output")
- The back of the device has an inlet for tap water (for the clean cycle)
- The back of the device has the two outlets for each flavoring dispense
- We provide a matte black faucet with black silicone tubing running parallel along it
- Everything is 1/4" hard tubing with John Guest quick connects, both within the device and the connections I just described, with the lone exception of the foot or so of black silicone tubing that runs along the matte black faucet
- The cartridge itself has 4 quick connects inside of it, and the user squeezes towards them a flat surface (against another flat surface) that pulls a release plate that presses the collets of those 4 quick connects towards the user, so that it can be detached from the 4 tube stubs in the enclosure dock
- When I push the air switch, I feel and hear a click that lets me know the flavor is changed
- The RP2040 display is as easily mounted to the wood panel in front of my sink as is the air switch, and the RP2040 always shows me the real logo of the Coke or Pepsi product I have selected, because the iOS app allowed me to upload over BLE any image I wanted for each flavor.
- I can imagine a user who would be as ecstatic about having the full rotary knob S3 mounted externally as I am personally about having the sleek tiny flat RP2040 there
- I can imagine a user who would be ecstatic to have both simply remain where the factory put them, on the front of the device
- Some users may leave the air switch there even
- Some users may put the device on top of their counter
- Many users may put it under the sink
- It will look and feel amazing no matter where they put it


## 3. On the cartridge specifically

- The release plate is inside of the cartridge, and the quick connects are even further inside the cartridge than that
- When I say the release plate is inside the cartridge, I want to be very clear - the cartridge should NOT have a release plate sitting outside of it in any way - it is important that this entire mechanism is hidden from the user. It is important that to them, the cartridge is a "black box" (with 4 holes on the back barely big enough for the tubes, and protruding tracks on each side that slide into matching channels in the enclosure bay, and the "squeeze" mechanism inset on the front for them to hold and squeeze). Everything that the user can see has a purpose the user can understand at a glance.
- The user will need to pull the release plate towards them somehow (with their fingers), and so they will need leverage to push against (with their palm), but both surfaces can be perfectly flat and that will still provide the satisfying user experience we seek.
  - The surface the users palm pushes against must eventually be attached to whatever the quick connects are mounted in
	- The surface the users fingers pull must eventually be attached to the release plate
	- The release plate must be able to move towards the quick connect collets
	- The user's hand is palm-up during the squeeze — fingers curl upward to pull the release surface while the palm pushes against the cartridge body. 
- For putting it back in, there is no need to worry about the collets at all, regardless of their position the tubes can be pushed into the quick connects and proper mechanisms in the quick connects will ensure the the cartridge will no longer be able to be removed (without of course pushing the collets again)
- The pumps each mount to a flat surface via 4 screws surrounding the motor cylinder — the measurements and photos in the repo have the exact dimensions.
- The coupler tray is two separate pieces (flat surfaces) that lock permanently together via tapered dovetails and snap detents. The geometry of the John Guest union couplers requires this — the couplers cannot be inserted into a one-piece tray. The two halves capture the narrow center section of each coupler, with the wider shoulders providing axial retention.
- These two interior flat surfaces (pump tray, coupler tray) slide into protruding tracks on the cartridge walls
- The cartridge enclosure is 6 flat panels assembled into a box (back, left, right, front, bottom, top). The front and back slide into protruding rails on the left and right sides. The bottom slides into protruding rails on the left and right sides. And then, eventually, as the last step of assembly, the top slides into protruding rails on the left and right sides.
- The lever itself is just a flat surface, with struts extending through the two interior panels (which hold it in alignment, roughly enough, especially if we use 4 struts), and those struts connect to the release plate, held in alignment in a similar way.
- The front panel is just a flat panel with a rectangular hole in it. The user's fingers reach through that hole to contact the release plate's pull surface. The release plate isn't mounted in the front panel — it's held in alignment by the interior plates (pump tray, coupler tray) which have bores that the struts pass through. The front panel is dumb — it's a wall with an opening.
- The struts (connecting the lever and release plate) go through each of the two interior plates (which guide them and support them and keep them in alignment). The interior plates are the alignment mechanism, not the front panel.

## 4. Cartridge Build Sequence

---

### Season 1: Interior Plates

The flat surfaces inside the cartridge. Each one is a flat panel with holes. Nothing connects to anything else yet.

#### Phase 1: Make the plates

1. **Release plate** — flat plate with stepped bores for 4 collet interfaces, 2 guide pins. DONE.
2. **Pump tray** — flat plate with 2 motor bores (~37mm, for the motor cylinder to pass through) and 8 screw holes (4 per pump, M3, in a 50mm square pattern around each motor bore). The screws approach from the motor side — you cannot reach them without the motor bore. No strut bores — those come in Phase 4.
3. **Coupler tray** — flat plate with holes/pockets for capturing 4 John Guest union couplers. No strut bores — those come in Phase 4.
4. **Lever** — flat plate with 4 struts extending from it. Plain rectangular struts — no dovetail or joint geometry on the strut ends yet. That comes in Phase 2.

#### Phase 2: Connect the plates to each other

5. **Release plate v2** — update release plate from 2 struts to 4 struts.
6. **Join lever struts to release plate struts** — design and print the tapered dovetail + snap detent joint between lever struts and release plate struts. This is where the joinery research gets applied.
7. **Test the squeeze mechanism by hand** — lever + struts + release plate, assembled, held together by nothing but the strut joints. Verify it translates, verify the release plate presses collets, verify the lever sits where fingers can reach it. No enclosure, no walls, just the mechanism in your hands.

#### Phase 3: Split and rejoin the coupler tray

8. **Split coupler tray into two halves** — determine the split line that allows the couplers to be inserted. Produce two STEP files. Plain flat mating faces at the split — no dovetail geometry yet. That comes in step 9.
9. **Add dovetail geometry to coupler tray halves** — the tapered dovetail slide that joins them.
10. **Add snap detent to coupler tray halves** — the prong barbs that lock the halves permanently.
11. **Print and test coupler tray assembly** — two halves snap together, couplers are captured, shoulders provide axial retention.

#### Phase 4: Add strut bores to interior plates

12. **Add strut bores to pump tray** — 4 holes sized to the strut cross-section, positioned so the struts pass through cleanly.
13. **Add strut bores to coupler tray** — same, but the coupler tray is two halves, so the bores must align across the split line (or be entirely on one half).
14. **Full interior dry fit** — lever + struts + release plate, passing through pump tray and coupler tray. Everything held in alignment by the bores. Verify the mechanism still translates smoothly with all interior plates present.

---

### Season 2: Walls

The 6 flat panels that form the cartridge box. Each one is a flat panel. The side walls get rails, everything else is just flat with maybe a hole or two.

#### Phase 5: Make the walls

15. **Left wall** — flat panel, correct outer dimensions. Protruding rails on the interior face for: front panel, back panel, bottom panel, top panel, pump tray, coupler tray. Interior rails are the only features. No detents, no retention, no exterior tracks for the enclosure bay — those come in Season 4.
16. **Right wall** — mirror of left wall.
17. **Back panel** — flat panel with 4 holes for tube stubs. Outer dimensions sized to fit the left/right wall rails. No detent geometry — that comes in Phase 8.
18. **Front panel** — flat panel with rectangular hole in lower half. Outer dimensions sized to fit the left/right wall rails. No detent geometry — that comes in Phase 8.
19. **Bottom panel** — flat panel, no features. Outer dimensions sized to fit the left/right wall rails.
20. **Top panel** — flat panel, no features. Outer dimensions sized to fit the left/right wall rails. This is the last piece that goes in during assembly.

#### Phase 6: Test fit the box

21. **Print all 6 panels and slide them together** — verify everything fits the rails, verify the box holds its shape by gravity and friction alone. Nothing locks. Panels may slide back out. That's fine.
22. **Slide interior plates into the assembled box** — verify pump tray and coupler tray fit their rails inside the box. Verify the mechanism (lever + struts + release plate) still translates with the walls present.
23. **Full assembly dry fit** — everything together for the first time. Interior mechanism, interior plates, all 6 walls. Identify what doesn't fit, what binds, what needs clearance.

#### Phase 7: Front and back panel features

24. **Refine front panel hole** — after dry fit, adjust hole position and size so the user's fingers actually reach the lever comfortably. This may take multiple prints.
25. **Refine back panel holes** — after dry fit, verify tube stubs actually pass through and reach the quick connects with the release plate in its resting position.

---

### Season 3: Joinery

Nothing new gets designed. Everything that exists gets joined properly so it stays together.

#### Phase 8: Wall-to-wall retention

26. **Add detent geometry to left wall rails** — tapered dovetails or snap detents on the rails so the front, back, bottom, and top panels lock at end of travel.
27. **Add matching detent geometry to front, back, bottom, top panels** — the receiving features for the wall detents.
28. **Print and test wall retention** — panels click in, don't slide back out. Iterate on tolerances.

#### Phase 9: Interior plate retention

29. **Add detent geometry to interior plate rails** — pump tray and coupler tray lock into their side wall rails.
30. **Print and test interior plate retention.**

#### Phase 10: Strut bore refinement

31. **Add bosses around strut bores in pump tray** — reinforce the bores now that we know the exact strut dimensions and clearances from prototyping.
32. **Add bosses around strut bores in coupler tray** — same.
33. **Print and test mechanism with bosses** — verify the added material doesn't bind the struts, verify alignment is tighter.

---

### Season 4: Refinement

Everything works mechanically. Now make it feel like a product.

#### Phase 11: Cosmetics and UX

34. **Front panel exterior surface treatment** — the palm-push surface the user touches. Texture, radii, visual design.
35. **Lever surface treatment** — the finger-pull surface. Smooth or lightly textured for finger comfort.
36. **Side wall exterior surface treatment** — the surfaces visible when the cartridge is partially ejected from the enclosure.
37. **Cartridge-to-enclosure track refinement** — the exterior protruding tracks on the side walls that ride in the enclosure bay channels. Smooth sliding, correct clearances.

#### Phase 12: Spring return and final mechanism tuning

38. **Add spring pockets** — wherever the return springs end up living (TBD based on interior plate positions and available space).
39. **Tune squeeze force** — adjust spring rate, strut friction, bore clearances so the squeeze feels right.
40. **Final full assembly test** — everything together, mechanism works, panels locked, cartridge slides in and out of enclosure bay (once the enclosure bay exists).

---

### What is NOT in this sequence

- The enclosure (the outer device housing) — that's a separate build sequence
- The bag cradle system — separate
- Electronics mounting — separate
- Valve mounting — separate
- Any part that is not the pump cartridge