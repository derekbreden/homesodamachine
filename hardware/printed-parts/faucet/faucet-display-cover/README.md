# Faucet display cover

The PET-GF shroud follows the Waveshare display and meets the three tube
outlets at one flush front plane. Two concealed snap receivers engage the
shell's long cantilevers. The cover seats straight toward the display;
there are no display fasteners or sliding assembly step.

The complete enclosure is a fit-and-snap print trial. Assembly force,
retention, repeated operation and the as-printed PET-GF roots need the physical
reading before this joint is treated as validated.

## Geometry

The planar face is [27.5 mm](PLATE_X) wide and [47.5 mm](PLATE_S) long. Its
rounded skin tapers to the skirt around the neck. The bezel is
[1.3 mm](COSMETIC_WALL) thick; the checked curved cosmetic wall is at least
1.19 mm. The snap arms, their anchors, the receiver seats and the four
metal-foot bearing pads have 3 mm working sections.

The window is [20.5 mm](WINDOW_X) × [40.5 mm](WINDOW_S). Its lip overlaps the
module housing and leaves [0.1 mm](COVER_OVER_FACE) above the glass. The display
feet sit at n = [10.1 mm](DISPLAY_FEET_N). The measured device and corrected
vendor component envelopes leave 0.30064 mm between the flavor tubes and
the limiting USB-C housing. The underside over the tubes is open; four small
pads support the metal feet.

The frame is the shell's `_tip_frame`: x is lateral, s runs up the final
neck tangent from the tube exit, and n points toward the display face. The
front bezel edge is at s = 0. The cover's lower opening follows the circular
neck, so the parting line stays below the display face.

## Assembly trial

1. Remove supports and check that each cantilever is free along its full
   compliant length. Leave the rounded roots and the inward travel stops intact.
2. Route the display ribbon through its side corridor and place the exact
   module on the four metal-foot pads. Keep the ribbon clear of the USB socket
   and underside components.
3. Press the cover straight toward the display. Its two receiver ledges pass
   the lead-ins and engage by [0.3 mm](SNAP_ENGAGEMENT). The arms are unloaded
   in the seated position, with 0.15 mm normal clearance at the retaining faces.
   The receiver bottoms stop on the chassis seats before the bezel can load
   the glass.
4. Read complete seating, display fit, touch response, retention and any root
   whitening or cracks on the printed enclosure. Record the trial result
   before using the snap in a customer assembly.

Customer installation uses the assembled faucet.

## Printing and checks

The broad planar bezel prints face down: +130° about the CAD X axis. The
rounded walls expand gradually toward the open underside. Support access is
through that underside before the display is installed.

`faucet_display_cover.py selftest` checks one valid solid, the planar bezel,
the cosmetic minimum and the receiver stock. The faucet geometry audit checks
actual hardware and tube clearance, normal assembly motion and snap geometry.
Those geometric readings do not measure the printed snap's force or durability.

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.py`
