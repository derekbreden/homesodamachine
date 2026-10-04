# Letter bench sheets

Three 8.5 × 11 inch sheets for the carbonator bench:

1. Drill the blind rod register in both endcaps.
2. Prepare, seat, tack, indicate, purge and establish continuous work contact.
3. Set up the controls, hold the rotation pedal, then pull the laser trigger.

The [PDF](../../../output/pdf/assembly-drill-and-weld-letter.pdf), also on the
[document shelf](https://homesodamachine.com/drawings), has vector
drawings and embedded IBM Plex type. Instructional content is centered at 98%
scale. A separate background layer extends 1/4 inch beyond the paper edges;
its top cobalt and right coral bands extend 1/3 inch inward. The bands fill
the page edges at full scale, with room for borderless crop variation.
The final comic frame shows the pedal down and the gloved finger pulling the
trigger. The finish sequence appears before that frame.

## Sources and scope

[Pressure-vessel fabrication](../pressure-vessel.md) owns the drilling and
closure procedure. [The weld rig](../weld-rotation-rig.md) owns runout,
continuity, rotation and stopping. The [per-weld sequence](../../weld-rotator-guide/46-the-per-weld-sequence.html)
supplies the operating order, with the rig's two-turn continuity check.
The [X1 Pro manual](https://www.xlaserlab.com/pages/xlaserlab-x1-pro-instruction-manual),
pages 11–14, supplies the welder setup and trigger controls.

The drill diagram reads the endcap's numeric constants and shared float datum.
Weld travel and overlap read the rotator interface; practice settings read the
fabrication procedure. Source hashes and the numeric inputs are recorded in
[the manifest](../../../output/pdf/assembly-drill-and-weld-letter.sources.json).
The illustrations are schematic. The page is not a drilling template, and
the gun illustration does not prescribe angle or standoff. Closure root-fusion
and internal-oxidation qualification remain open in the fabrication procedure.

## Build and print

```sh
python3 tools/assembly-letter/build.py
```

Requires ReportLab. The builder is run by hand and generates just these three
sheets; it does not invoke the appliance build, scene rendering, card sync or
publish lanes. A changed source expression outside its narrow arithmetic
reader, changed named drill/spacer, or changed practice-recipe structure
requires review before rendering.

Print one copy, single-sided, portrait, color, high quality, Letter borderless,
using the Epson photo-paper media profile. Load Letter photo stock in the
rear feeder and select **rear** explicitly. The main cassette can contain
plain Letter stock. Content scaling is already in the PDF; print at 100%
without another 98% reduction. Example for the ET-8550 queue:

```sh
lp -d EPSON_ET_8550_Series -n 1 \
  -o PageSize=Letter.Fullbleed -o MediaType=photographic-glossy \
  -o InputSlot=rear -o media-source=rear -o Duplex=None -o sides=one-sided \
  -o ColorModel=RGB -o cupsPrintQuality=High -o print-quality=5 \
  -o print-scaling=none -o number-up=1 \
  output/pdf/assembly-drill-and-weld-letter.pdf
```

After submission, check the Epson's native job attributes for
`media-source=rear`, zero media margins and single-sided photo quality.
Printer job completion establishes that the sheets ran; edge coverage and
visual balance are physical observations. The reported fit of this setup
is the basis for the 98% content scale.
