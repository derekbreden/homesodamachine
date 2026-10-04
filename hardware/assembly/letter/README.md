# Letter bench sheets

Three 8.5 × 11 inch sheets for the carbonator bench:

1. Drill the blind rod register in both endcaps.
2. Prepare, seat, tack, indicate, purge and establish continuous work contact.
3. Set up the controls, hold the rotation pedal, then pull the laser trigger.

The [PDF](../../../output/pdf/assembly-drill-and-weld-letter.pdf) has vector
drawings and embedded IBM Plex type. Its colored edge bands extend to the
paper edges; essential content stays within a borderless-print safe area.
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
using the Epson photo-paper media profile. Let automatic tray selection use
the loaded Letter photo stock. Example for the ET-8550 queue:

```sh
lp -d EPSON_ET_8550_Series -n 1 \
  -o PageSize=Letter.Fullbleed -o MediaType=photographic-glossy \
  -o InputSlot=auto -o Duplex=None -o sides=one-sided \
  -o ColorModel=RGB -o cupsPrintQuality=High -o print-quality=5 \
  -o print-scaling=none -o number-up=1 \
  output/pdf/assembly-drill-and-weld-letter.pdf
```
