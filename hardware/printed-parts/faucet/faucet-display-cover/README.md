# Faucet display cover

The PET-GF shroud follows the Waveshare display and meets the three tube
outlets at one flush front plane. The cover's side walls spread over the
rigid round neck, then its two broad lips seat in shallow side grooves.
The cover seats straight toward the display; no display fasteners are fitted.

The complete enclosure is a fit-and-snap print trial. Assembly force,
retention, repeated operation and the as-printed PET-GF walls need the physical
reading before this joint is treated as validated.

## Geometry

The planar face is [27.5 mm](PLATE_X) wide and [48.49 mm](PLATE_S) long. Its
rounded skin tapers to the skirt around the neck. The bezel is
[1.3 mm](COSMETIC_WALL) thick. The finished rim has a 1 mm minimum cosmetic
section; the front wall is [2 mm](DISPENSE_FACE_T) thick. Two broad 1.3 mm-high retaining lips
continue inward from the side walls. The four metal-foot bearing pads have
3 mm working sections.

The lips follow the neck profile with [0.3 mm](SNAP_ENGAGEMENT) nominal
radial engagement. Their grooves provide 0.15 mm radial clearance and
0.15 mm clearance above the lip tops. The lip bottoms seat on the groove
floors, stopping the cover before its bezel reaches the glass.

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
   and the neck's shallow grooves. Preserve the lip bearing faces and
   groove floors.
2. Lay the display ribbon in the open space below the PCB, toward its southwest
   corner as viewed from the glass, and place the exact
   module on the four metal-foot pads. Keep the ribbon clear of the USB socket
   and underside components.
3. Press the cover squarely toward the display. Its side walls flex outward
   around the cylinder until both lips enter their grooves below the rigid
   retaining shoulders. Confirm both lip bottoms reach their seating floors.
4. Read complete seating, display fit, touch response, retention, permanent
   spreading and any whitening or cracks on the cover. Record the trial result
   before using the snap in a customer assembly.

Customer installation uses the assembled faucet.

## Printing and checks

The broad planar bezel prints face down: +130° about the CAD X axis. The
rounded walls expand gradually toward the open underside. Support access is
through that underside before the display is installed.

`faucet_display_cover.py selftest` checks one valid solid, the planar bezel,
the cosmetic minimum and the lip thickness. The faucet geometry audit checks
actual hardware and tube clearance, normal assembly motion and snap geometry.
Those geometric readings do not measure the printed snap's force or durability.

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py`
