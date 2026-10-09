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

![Rear display view, USB-C at top: VBUS, GND, TX and RX are the top four left pads](display-wiring.svg)

| Display pad | P1 pin | Function | Main board J3 |
| --- | ---: | --- | --- |
| VBUS | 1 | 5 V power input | V5 |
| GND | 3 | 0 V return | GND |
| TXD | 5 | GPIO43, display transmit | IO35, main board receive |
| RXD | 7 | GPIO44, display receive | IO33, main board transmit |

P1 has odd pin numbers down the left and even numbers down the right. UART
is 3.3 V TTL, 921600 baud, 8N1. Leave the remaining pads open. Make the joints
with J3 and USB disconnected, after the continuously insulated display leads
have passed through both seated vent bungs. Solder only at the dry PCB ends.
Page 3 covers the joint, continuity and powered flavor-response check; page 12
covers fitting the wired display and cover without trapping the leads.

The procedure specifies the four SIG-6 nets but does not publish a modular
contact-to-net assignment. Page 15 traces the actual plug and jack to the J3
endpoints by continuity and records the build's contact identities. The
telephone or T568B color diagram does not specify this harness.

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
  donor and lever seating, neck/base closure, display motion and clearance.
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
