# Faucet assembly guide

[Open the display wiring on page 2](https://homesodamachine.com/read/faucet-assembly-guide/faucet-assembly-guide.pdf#page=2)
or [open the complete local PDF](faucet-assembly-guide.pdf).

18 illustrated Letter pages for building the faucet, connecting its Waveshare
ESP32-S3-Touch-LCD-1.47 display, and finishing the permanently attached
umbilical. The working pictures, short actions and check at each operation
follow the [weld-rotator guide](../weld-rotator-guide/README.md).
The complete PDF appears on the [document shelf](https://homesodamachine.com/drawings).

## Display wiring at a glance

Look directly at the **back of the PCB**, glass facing away from you, with
**USB-C at the top**. The first four pads down the **left** are the four
connections. This is a bench orientation; rotate the loose display to match.

**Installed in the faucet, USB-C points toward the dispense face.** The opposite
end points up the gooseneck. The side-section inset below and the installation
pictures on page 12 show that orientation.

![Rear pad map with USB-C up on the bench; installed side section shows USB-C toward the dispense face and the opposite end up the gooseneck](display-wiring.svg)

All four conductors are **black**. Before separating the ribbon, add a white
index mark to **one edge at both free ends**. That edge is **C1**; count C1-C4
across the ribbon from it. These identities stay with the wires through the
vent bungs, display solder joints and wall-end plug.

| Ribbon wire | Display pad / P1 pin | RJ11 plug and jack pin | Jack's printed USOC label | Main board J3 pin / net |
| --- | --- | ---: | --- | --- |
| C1, marked edge | VBUS / P1-1, +5 V | 2 | White/orange | 3 / V5 |
| C2 | GND / P1-3, 0 V | 3 | Blue | 4 / GND |
| C3 | TXD / P1-5, GPIO43 display TX | 4 | White/blue | 2 / IO35, main RX |
| C4 | RXD / P1-7, GPIO44 display RX | 5 | Orange | 1 / IO33, main TX |

![Contact-side plug orientation and the numbered RiteAV jack punchdown slots, with black wire identities and J3 destinations](sig6-connector-wiring.svg)

**Plug:** gold contacts face you, nose up, cable down, latch on the far side.
The six positions read **1-6 left to right**. Insert **C1, C2, C3, C4 into
positions 2, 3, 4, 5**, respectively; positions 1 and 6 are empty. The C1 mark
is on the left edge in this view. Crimp a 3-prong 6P4C plug; shim the final
15 mm so its strain-relief bar grips the ribbon jacket.

**RiteAV jack:** punchdown side up, plug opening toward the bottom of the
picture. Land **J3 3/V5 in jack 2, J3 4/GND in jack 3, J3 2/IO35 in jack 4,
and J3 1/IO33 in jack 5**. The blue/orange colors belong to the jack's printed
terminal legend; the 22 AWG inboard wires are black. Punch them down with
their insulation intact, trim outward and refit the dust cover. Leave jack
terminals 1 and 6 open. J3's PCB silk reads **GND, V5, IO35, IO33** from left
to right with the component side up and J3 at the lower edge; the corresponding
physical pin numbers are **4, 3, 2, 1**.

P1 has odd pin numbers down the left and even numbers down the right. UART
is 3.3 V TTL, 921600 baud, 8N1. Leave the remaining pads open. Make the joints
with J3 and USB disconnected, after the continuously insulated display leads
have passed through both seated vent bungs. Solder only at the dry PCB ends.
Page 3 covers the joint, continuity and powered flavor-response check; page 12
covers fitting the wired display and cover without trapping the leads.

Page 2 and page 15 carry the same complete connection table. The page-3
continuity check verifies those specified connections before power is applied.

## Page map

| Pages | Work |
| --- | --- |
| 1 | Overview and linked operation map |
| 2-3 | Rear display pad map, direct solder joints, continuity and response |
| 4 | Matching Sculpted/Industrial kit and Black/White tube-cut table |
| 5-7 | Cleanup, base inserts, donor, printed lever, TPU thimble and soda tube |
| 8-10 | Individually insulated wires, pre-threaded bungs, curved pusher, drain setting |
| 11-12 | Dry neck joint, underside screws, beverage ends, wired display and cover |
| 13-14 | Gasket, captive donor washer/nut, White flavor unions and blue supply |
| 15-17 | Wall plug, foam/braid, four collars, final inspection and packing |
| 18 | Clickable sources and physical evidence scope |

For a complete build, follow pages 4-17 in order. Pages 2-3 are the electrical
reference used after the vent bungs are seated and before the display is
enclosed. The pictures are original vector schematics; the cover uses the
installation guide's committed CAD overview. The rear diagram preserves the
manufacturer's pad order. Printed picture size is not a dimension or template.

## Sources and physical scope

- [Faucet and umbilical procedure](../assembly/faucet-and-umbilical.md):
  cuts, gasket, retained hardware, supply, braid and packing.
- [Shell assembly](../printed-parts/faucet/faucet-shell/ASSEMBLY.md):
  donor and lever seating, neck/base closure, USB-C toward the dispense face,
  display motion and clearance. The shell's USB keepout and assembly's display
  placement define the installed orientation.
- [Vent-seal assembly](../printed-parts/faucet/asse-vent-seals/README.md):
  two retained bungs, continuously insulated wires, curved perimeter pusher
  and the nominal 8.0 ± 0.2 mm D setting from the tool-contact flange face.
- [Waveshare rear interface layout](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47)
  and [P1 schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-Schematic.pdf),
  reviewed 2026-10-08: physical orientation, pad identities and pin numbers.
- [Faucet link firmware](../../firmware/src_faucet/base_link.cpp) and
  [main-board pins](../../firmware/src_appliance/pins.h): GPIO43 TX / GPIO44 RX,
  crossed to IO35 RX / IO33 TX, at 921600 baud.
- [Inboard SIG-6 wiring](../assembly/wiring.md): J3 loom through the rear jack.
- [Main-board connector implementation](../pcb/pcba/parts.tsx) and
  [J3 placement](../pcb/pcba/pcba.tsx): physical J3 pin numbers and silk order.
- [RiteAV mpn46181 jack](https://www.riteav.com/products/riteav-rj11-phone-black-punchdown-type-keystone-jack-10-pack)
  and [Leviton's six-contact USOC terminal-color table](https://leviton.com/content/dam/leviton/network-solutions/product_documents/instruction_sheet/Leviton-IST-41106-41108-Voice-Grade-Jacks.pdf):
  jack terminal identities. The SIG-6 net assignment is the table above.

The [cover acceptance](../printed-parts/faucet/faucet-display-cover/physical-acceptance.json)
and [lever acceptance](../printed-parts/faucet/lever-replica/physical-acceptance.json)
retain their identified physical articles and accepted fit/operation scope.
The guide does not establish retention force, cycle life, complete current
[vent containment](../printed-parts/faucet/vent-qualification/README.md), or the
maximum clampable countertop thickness. The 38 mm routing envelope is a
tube/cable route allowance; the actual retained washer/nut/shank stack controls
mounting engagement. Physical records remain the authority for acceptance.

## Build by hand

```sh
python3 tools/faucet-assembly-guide/build.py
```

The builder uses ReportLab, Pillow and Poppler (`pdftoppm`) with the shared
Letter furniture in `tools/assembly-guides/common.py`. It reads selected
procedure figures without importing or executing CAD. It writes:

- `hardware/faucet-assembly-guide/faucet-assembly-guide.pdf`
- `hardware/faucet-assembly-guide/faucet-assembly-guide.cover.png`
- `hardware/faucet-assembly-guide/faucet-assembly-guide.pdf.json`
- `hardware/faucet-assembly-guide/display-wiring.svg`, from the PDF's same drawing
- `hardware/faucet-assembly-guide/sig6-connector-wiring.svg`, from the page-15 drawing
- `output/pdf/faucet-assembly-guide.pdf`, the identical delivery copy
- `output/pdf/faucet-assembly-guide.sources.json`, source hashes and wiring provenance

These are committed document assets. This guide has no CAD/Bazel target,
automatic regeneration, hook or machine-build check. `render.yaml` deploys
its committed directory so the shelf can serve it. Review the affected
operation deliberately when a part, fit, procedure or pin assignment changes.
Render the resulting pages and inspect the pictures and text before publishing.

Print Letter, single-sided, color, one-up at **100% / no scaling**. The body is
already centered at 98%; the full-scale cobalt/coral bleed is separate.
The [shop-guide index](../assembly/guides/README.md#epson-letter-photo-printing)
has the Epson rear-feeder settings.
