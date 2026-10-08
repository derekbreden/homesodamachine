# Umbilical plug and socket exploration

One push connects the umbilical to the appliance: a plug on the umbilical's machine end carries
all four tubes and the faucet display's contacts, and a socket in the back wall receives it. This
is concept geometry. Nothing here is in the build, the BOM or the production enclosure.

![Machine side, plug, plugged in, behind the face, through the counter](renders/one-plug-umbilical.png)

[`one-plug-umbilical.html`](one-plug-umbilical.html) is the same five views to turn in 3D.

## The concept

| | |
| --- | --- |
| Plug | Ø[32.49](UMB_PLUG_D) end to end. Four 1/4″ stubs stand [24.5](UMB_STUB) mm proud of its face. |
| Countertop | The plug passes the 1-3/8″ (Ø34.93) hole the umbilical drops through ([`faucet_assembly.countertop_hole_diameter`](/hardware/faucet-layout/faucet_assembly.py)) with [1.22](UMB_COUNTER_SIDE) mm a side. |
| Socket | Ø[33.09](UMB_SOCK_D), [15](UMB_SOCK_DEPTH) mm deep, in a [60](UMB_PLATE_W) mm patch of PET-GF back wall. |
| Tubes | A [16.13](UMB_PITCH) mm square seen from outside: FLAVOR top left and top right, TAP bottom left, DRAIN bottom right. Face holes are the [tube collar's](/hardware/printed-parts/faucet/tube-collar/tube_collar.py) Ø[6.68](UMB_BORE) bore. |
| Unions | Four John Guest [PP0408W](/hardware/reference/jg-pp0408w/) side by side at one depth, collets [8.5](UMB_WALL) mm behind the face, [1.03](UMB_UNION_GAP) mm between neighbours. |
| DRAIN | Its 4 mm tube steps up to a 1/4″ stem inside the plug ([neoFit 4 mm × 1/4″ stem reducer](https://www.freshwatersystems.com/products/neofit-acetal-black-stem-reducer-4mm-5-32-tube-x-1-4-stem)), so all four unions are the same part. |
| Pogo | The [YYFKGCP pair](/hardware/reference/yyfkgcp-pogo-4p/) stands on end between the tube columns: spring pins in the socket, pads on the plug. Each half takes two M1.4 × 4 × Ø2.3 heat-set inserts and two M1.4 × 8 socket-head screws through its ears, as on the [pump cartridge](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md). |
| Magnets | One [K&J SB443-IN](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet) (1/4 × 1/4 × 3/16 in, N42, magnetized through thickness) each side of each half, four per umbilical, centred [9.0](UMB_MAG_X) mm out between the tube pairs. Its pole face sits flush and bare. Each side of the bar carries a 1.6 mm groove, 0.79 mm deep, starting 1.6 mm behind the face; the pocket prints [1.5](UMB_RAIL_H) mm rails into both grooves. N faces out on one side and S on the other, so an inverted plug repels. |

**Fitting the bars.** Each half prints with its face standing vertical, so the bars' grooves run
up and down. At one pause both bars slide down their rails, and the next layers print over them,
so they can neither leave the face nor slide back out.

## What sets the sizes

- **Plug diameter** is held under the countertop hole. That leaves no room on the face for an
  RC62: Ø19.05 with [1.5](UMB_WEB) mm webs puts the tube holes [14.37](UMB_RC62_HOLE_R) mm out and the face at [38.4](UMB_RC62_FACE_D) mm or more.
- **Tube pitch.** Each bar sits between a tube pair with [1.5](UMB_WEB) mm of PET-GF to both holes, which
  makes the square [16.13](UMB_PITCH) mm and leaves the unions' Ø15.1 collet rings [1.03](UMB_UNION_GAP) mm apart.
- **Face depth.** The pogo's ear screws sit 10.22 mm from centre, between the union rings, so the
  rings start behind the screw tips: [8.5](UMB_WALL) mm of PET-GF in front of the collets.

The narrowest clearances in [`scene.py`](scene.py)'s own check: inserts [0.20](UMB_CLR_INSERT) mm behind the pogo's
ear plate, unions [1.03](UMB_UNION_GAP) mm apart, screws [1.24](UMB_CLR_SCREW) mm from the unions.

## Not designed

- Releasing the collets when the plug is pulled. A push-to-connect collet holds its tube until
  the release sleeve is pressed.
- Guiding the [24.5](UMB_STUB) mm stubs into the face holes before the plug body enters the socket.
- The plug's internal routing from the four stubs to the sleeved bundle.
- How the carrier behind the face holds the unions.
- The bars' installed pull. K&J rates the SB443-IN at 3.42 lb to a steel plate at contact; the
  pair gets that only while the faces touch, and the four pogo springs push them apart with about
  0.4 lb.

## Rebuild

```sh
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/scene.py
python3 tools/viz/build.py future/umbilical-plug-and-socket-exploration/viz-spec.json --out future/umbilical-plug-and-socket-exploration/one-plug-umbilical.html
```

`scene.py` writes four scene STEPs and their viewer payloads to `out/`, which git ignores, and
prints its clearance check. [`tools/viz/build.py`](/tools/viz/build.py) turns them into the page.

## Sources
[value](NAME) texts are updated by:
- `/future/umbilical-plug-and-socket-exploration/scene.py`
