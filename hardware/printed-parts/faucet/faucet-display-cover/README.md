# Sculpted faucet display cover

The PET-GF shroud follows the Waveshare display and meets the three tube
outlets at one flush front plane. The cover's side walls spread over the
rigid round neck, then its two broad lips seat against the roots of side grooves.
The display and cover slide onto the tip together, then seat toward the neck.
No display fasteners are fitted.

The complete enclosure is a fit-and-snap print trial. Assembly force,
retention, repeated operation and the as-printed PET-GF walls need the physical
reading before this joint is treated as validated.

## Geometry

The planar face is [27.5 mm](PLATE_X) wide and [48.49 mm](PLATE_S) long. Its
rounded skin tapers to the skirt around the neck. The bezel is
[1.3 mm](COSMETIC_WALL) thick. The finished rim has a 1 mm minimum cosmetic
section; the front wall is [2 mm](DISPENSE_FACE_T) thick. Two broad [3 mm](LIP_HEIGHT)-high retaining lips
continue inward from the side walls. The four metal-foot bearing pads are
[3 mm](FOOT_PAD_WIDTH) square and [2 mm](FOOT_PAD_DEPTH) deep.

The rear wall closes within the rounded skirt outline. Its inner face is
vertical at the display's rear clearance plane; its lower edge slopes upward
across the curved neck opening. The underside remains open.

The lips follow the neck profile with [1.2 mm](SNAP_ENGAGEMENT) nominal radial
engagement in [1.2 mm](GROOVE_DEPTH)-deep grooves. The seated lip and groove
roots share a contact surface. The relaxed print pulls each wing inward by
[1.25 mm](WING_PRELOAD) at the lip top and [1.513 mm](WING_BOTTOM_PRELOAD) at
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
feet sit at n = [10.1 mm](DISPLAY_FEET_N). The measured device and corrected
vendor component envelopes leave 0.30064 mm between the flavor tubes and
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
   [8.5 mm](DISPLAY_INSTALL_LIFT) above their seated position. Slide along the
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

The cover stands on its front wall: +40° about the CAD X axis. The retaining
faces and inner bezel print vertically. Support access is through the open
underside before the display is installed.

`faucet_display_cover.py selftest` checks one valid solid, the planar bezel,
the cosmetic minimum and the lip thickness. The faucet geometry audit checks
actual hardware and tube clearance, display loading, lifted axial assembly
motion, the final seating stroke and snap geometry.
Those geometric readings do not measure the printed snap's force or durability.
The [physical trial log](../../fixtures/faucet-display-snap/print-log.md)
records the reported print and retention observations.

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py`
