# Sculpted faucet display cover

The PET-GF shroud follows the Waveshare display and meets the three tube
outlets at one flush front plane. The cover's side walls spread over the
rigid round neck, then its two broad lips seat against the roots of side grooves.
The display and cover slide onto the tip together, then seat toward the neck.
No display fasteners are fitted.

The [physical trial](../../fixtures/faucet-display-snap/print-log.md) establishes
solid construction, useful give and spring, firm snap seating and retention
for its two identified PET-GF covers. The [acceptance record](physical-acceptance.json)
preserves the successful STL and reported results. The current cover matches the
27 mm vent-bearing neck and has a different STL. Both identified current white
covers [broke during assembly](prints/2026-10-17-cooling-off-prepared-mark2/reported-failure.json),
including display loading. The [fan-off cooling trial](prints/2026-10-17-cooling-off-prepared-mark2/physical-result.json)
passed normal display loading and cover installation. Its acceptance belongs
to the identified pre-clearance-change STL. The current seat and bezel add
1.50 mm outward clearance while retaining the neck snap datums.
Numerical force and cycle life have not been measured.

The [lowered-head fit review](fit-review/2026-10-24/README.md) records the
October 24 black Sculpted cover's installation failure and a working Industrial
control on the same tip. Its corrected print variant includes two local switch
pockets in the tip and 0.50 mm extra Sculpted cover reach with matching arch
relief. This variant retains the lowered display and four foot recesses; its
physical fit is separate from the earlier accepted covers above.

The corrected black head's [October 25 physical record](../industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/physical-result/physical-result.json)
reports very good fit with the display, tubes and wiring. Its visible front-corner
opening is the subject of the [skirt-overlap print trial](corner-overlap-review/2026-10-25/README.md).
The extended-skirt cover's [physical approval](prints/2026-10-25-front-overlap-black-mark2/physical-result/physical-result.json)
accepts its working fit and appearance, including the remaining visible gap.
No further iteration on that gap is requested. The
[production source set](../industrial/production-selection.json) identifies the
exact approved cover and matching lowered tip for subsequent Industrial prints.

## Geometry

The planar face is [27.5 mm](PLATE_X) wide and [48.49 mm](PLATE_S) long. Its
rounded skin tapers to the skirt around the neck. The bezel is
[1.3 mm](COSMETIC_WALL) thick. The finished rim has a 1 mm minimum cosmetic
section; the front wall is [2 mm](DISPENSE_FACE_T) thick. Two broad [3 mm](LIP_HEIGHT)-high retaining lips
continue inward from the side walls. The four metal-foot bearing pads are
[3 mm](FOOT_PAD_WIDTH) along the display and 3.25 mm across it, with
inner faces flush to the open channel, and [3.5 mm](FOOT_PAD_DEPTH) deep.

The rear wall closes within the rounded skirt outline. Its inner face is
vertical at the display's rear clearance plane; its lower edge slopes upward
across the curved neck opening. The lower rear skirt extends
[1.2 mm](REAR_SKIRT_EXT) aft along s, with its front edge and planar bezel
at their shared display datums. Its rear opening follows
s = [42.1 mm](REAR_TRIM_S0) + [0.6](REAR_TRIM_DS_DN) × n.
The underside remains open.

The lips follow the neck profile with [1.2 mm](SNAP_ENGAGEMENT) nominal radial
engagement in [1.2 mm](GROOVE_DEPTH)-deep grooves. The seated lip and groove
roots share a contact surface. The relaxed print pulls each wing inward by
[1.25 mm](WING_PRELOAD) at the lip top and [1.488 mm](WING_BOTTOM_PRELOAD) at
its bottom. This inset tapers to zero at the bezel's inner face.
The grooves leave [0.48 mm](GROOVE_ROOF_CLEARANCE) above the lip tops and
[0.3 mm](GROOVE_END_CLEARANCE) at their ends. The lips' inner upper and lower
corners carry [0.25 mm](LIP_INNER_EDGE_RELIEF) chamfers. Their central curved
faces contact the groove roots under preload, and the remaining flat lower
lands seat on the groove floors before the bezel can reach the glass.

The standalone STEP, STL and print project contain the relaxed shape.
The faucet assembly shows the nominal seated fit surface. That surface
does not predict the closed cover's elastic deformation, insertion force
or long-term preload.

The window is [20.5 mm](WINDOW_X) × [40.5 mm](WINDOW_S). Its lip overlaps the
module housing and leaves [0.1 mm](COVER_OVER_FACE) above the glass. The display
feet sit at n = [11.6 mm](DISPLAY_FEET_N). The measured device and corrected
vendor component envelopes leave 1.80064 mm between the flavor tubes and
the limiting USB-C housing. The underside over the tubes is open; four small
pads support the metal feet.

The frame is the shell's `_tip_frame`: x is lateral, s runs up the final
neck tangent from the tube exit, and n points toward the display face. The
lower enclosure rim is at s = 0. The cover's lower opening follows the circular
neck, so the parting line stays below the display face.

## Assembly trial

1. Remove supports and stringing from the open cover, its two broad lips
   and the neck's retaining grooves. Preserve the lip bearing faces and
   groove floors.
2. Spread the cover's broad side walls far enough for the display housing to
   pass the retaining lips. Support the display squarely inside the cover with
   its face aligned to the aperture. Route the ribbon toward the southwest
   corner as viewed from the glass, clear of the USB socket and underside
   components, with slack for the assembly motion.
3. Approach from the tube-outlet end with the display and cover held together
   [9.5 mm](DISPLAY_INSTALL_LIFT) above their seated position. Slide along the
   gooseneck to align the module with its four metal-foot pads, then lower the
   pair squarely toward the neck. Both lips enter their grooves below the
   retaining shoulders. The wings remain spread from their relaxed positions.
   Confirm the feet rest on their pads and both lip bottoms reach their seating
   floors, with the ribbon in its passage.
4. Read complete seating, display fit, touch response, retention, permanent
   spreading and any whitening or cracks on the cover. Record the trial result
   before using the snap in a customer assembly.

Customer installation uses the assembled faucet.

## Printing and checks

The approved production cover uses black PET-GF, **Bambu’s 0.20 mm first bed
layer and 0.24 mm later layers**, with no fine bands. Its
[cover-only project](faucet-display-cover-petgf.3mf) retains the accepted −50°
pose, localized cooling, supports and Mark2 trim.
Prepare it with:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/prepare_print_project.py
```

The preparer uses the exact approved STL in the production source set. It does
not submit a print. The identified historical white covers below retain their
own geometry and print scope.

The white PET-GF cover prints bezel up at −50° about the CAD X axis, using
0.24 mm layers. Its lower skirt and lip seating lands face the bed; the flat
upper retaining lands face up. The inner bezel receives support accessible
through the open underside before the display is installed. The visible front
wall and outer bezel remain clear of the bed.
The [saved STEP land witness](lower-land-lint-check.json) measures 160.56 mm²
across the two flat lower lands and confirms their bed-facing normals and
height in that print pose. The named cosmetic and lower-land slope findings
are answered beside the published mesh.

`faucet_display_cover.py selftest` checks one valid solid, the planar bezel,
the cosmetic minimum and the lip thickness. The current [display-clearance reading](../sculpted/prints/2026-10-17-localized-cooling-display-clearance-mark2/display-clearance.json)
and [retention reading](../sculpted/prints/2026-10-17-localized-cooling-display-clearance-mark2/display-retention.json)
bind the raised seat, hardware clearance, display loading, axial approach and
snap geometry. The [rear-opening reading](../sculpted/prints/2026-10-17-localized-cooling-display-clearance-mark2/rear-opening-rim.json)
measures complete rim boundaries and material sections in both nominal seated
and relaxed shapes. The [full faucet audit](../faucet-shell/centered-vent-check.json)
retains the geometry hashes and electronics reading for its identified inputs.
Those geometric readings do not measure the printed snap's force or durability.
The [physical trial log](../../fixtures/faucet-display-snap/print-log.md)
records the reported print and retention observations.

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py`
