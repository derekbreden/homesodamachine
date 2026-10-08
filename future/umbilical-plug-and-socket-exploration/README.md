# Umbilical plug and socket exploration

One push connects the umbilical to the appliance: a plug on the umbilical's machine end carries
all four tubes and the faucet display's contacts, and a socket snapped into back-top's rear wall
receives it. These are printable test parts. Nothing here is in the build, the BOM or the
production enclosure.

![Machine side, plug, plugged in, the release section, through the counter](renders/one-plug-umbilical.png)

[`one-plug-umbilical.html`](one-plug-umbilical.html) is the same five views to turn in 3D, with both print plates.

## Machine side

**The socket sits flush in back-top.** Its [47.0](UMB_FACE_W) × [44.6](UMB_FACE_H) mm face fills
a stepped hole: the face's own section for [3](UMB_FLANGE_T) mm, then the body's, so a
[2.5](UMB_LEDGE) mm ledge each side takes the push. Two snap leaves, one each side, ramp through
the hole and catch the wall's inner face by [1.45](UMB_HOOK_OVERLAP) mm. The hole is all back-top
needs: its roofs close on the same 36-degree planes as its other horizontal holes, and it has no
pause. Behind the wall the socket and its retainer reach [81](UMB_SOCKET_DEPTH) mm into the
machine.

**The cup is [34](UMB_CUP_DEPTH) mm deep** with [0.25](UMB_CUP_CLR) mm a side around the plug, so
the plug is [8.2](UMB_CUP_LEAD) mm in and running straight before a stub reaches its hole.

**The floor** carries three Ø[6.6](UMB_HOLE_Q) holes for the 1/4″ tubes and a Ø[4.3](UMB_HOLE_D)
hole for DRAIN's 4 mm tube on a [16.15](UMB_PITCH) mm square, the
[YYFKGCP pogo](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md) spring-pin half on end
between the columns with its two M1.4 inserts and screws, and a
[K&J SB443-IN](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet) bar each side,
[9.0](UMB_MAG_X) mm out, pole face flush and bare, its grooves on printed rails. Each bar keeps
[1.5](UMB_WEB) mm of PET-GF to the tube holes. The pogo halves stand
[0.246](UMB_POGO_GAP) mm apart when the faces meet, as on the pump cartridge.

**The unions float.** Three John Guest [PP0408W](/hardware/reference/jg-pp0408w/) and a neoFit
[AUC44M](https://www.freshwatersystems.com/products/neofit-acetal-black-union-connector-4mm-5-32-tube-x-4mm-5-32-tube)
for DRAIN slide in from the back, [1.05](UMB_CLR_UNION) mm apart, and a retainer screwed over them
(two M3 × 8 into RX-M3x5.7 inserts) stops them [0.5](UMB_NOSE_AIR) mm behind the floor's back face.
Pushing the plug in drives them against the retainer. Pulling it drags each union forward until
its collet sleeve lands on that face, [9.8](UMB_RELEASE) mm behind the floor; the face holds the
sleeve while the body keeps coming, which opens the collet, and the stub slides out. Each union
has [1.83](UMB_FLOAT) mm of travel for it. That is the pump cartridge's fixed release plate
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §4), turned to face the plug.
Under pressure the stub and the machine's tube pull a union both ways at once, so it stays where it
is and both collets keep their grip.

**The plug goes in one way up.** DRAIN's own 4 mm union is the key: a 1/4″ stub cannot enter its
Ø4.3 hole. The bars' polarity and the pogo's own magnets agree with it.

## Plug side

**The plug** is Ø[32.44](UMB_PLUG_D) across its round sides, [30.00](UMB_PLUG_H) mm between its
flats and [52](UMB_PLUG_L) mm long. It drops through the 1-3/8″ countertop hole with
[1.25](UMB_COUNTER_SIDE) mm a side, [0.93](UMB_COUNTER_CORNER) at its flats' corners.

**The tubes are the umbilical's own.** Each passes a slip-fit bore and stands proud of the face,
the 1/4″ tubes [25.8](UMB_STUB_Q) mm and DRAIN [22.8](UMB_STUB_D) mm, 0.5 mm short of their tube
stops. One printed key across the plug between the tube rows bites [0.5](UMB_KEY_BITE) mm into all
four, its lug reaching down to the thinner DRAIN tube. It goes in from the DRAIN side, the only
way it fits.

**The foam stops at the plug.** The soda tube's foam butts against the plug's back face, centred on
its tube, and clears the other three. The braid ends on the foam as it does today. The display
ribbon enters a channel under the top flat and drops to the pogo pad half's tails behind its seat.

## Printing

| Job | Parts | Pause | Print |
| --- | --- | --- | --- |
| [`machine-side`](print/machine-side-mark2.3mf) · [sliced](print/machine-side-mark2.gcode.3mf) | Socket, retainer, wall coupon | Before Z [25.88](UMB_PAUSE_SOCKET): two bars into the cup floor | [2 h 39 min](UMB_TIME_SOCKET), [87](UMB_G_SOCKET) g |
| [`plug-side`](print/plug-side-mark2.3mf) · [sliced](print/plug-side-mark2.gcode.3mf) | Plug, tube key | Before Z [18.68](UMB_PAUSE_PLUG): two bars into the face | [58 min](UMB_TIME_PLUG), [28](UMB_G_PLUG) g |

Both take black PET-GF on [Mark2](UMB_PRINTER)'s left 0.4 mm nozzle with the
[shared profile](/hardware/printed-parts/petgf.3mf), [+0.04](UMB_TRIM) mm trim, supports off,
four walls and 25 % infill. Every overhang closes on a 36-degree plane or lies over a bar, so
neither job has supports. The socket stands on its flats with the cup on its side, the plug lies
upside down on its top flat, and the coupon stands roof-down on its foot as back-top does.

At each pause, slide a bar down each slot, grooves on the rails and pole face flush with the
mating face. Looking at the mating face, the left bar shows N and the right bar S, on both parts;
mark each bar's N face with a compass first. The first layer after the pause bridges over the bars
with [0.165](UMB_AIR_SOCKET) and [0.265](UMB_AIR_PLUG) mm of air. Each job's
[`print.json`](print/machine-side-mark2.print.json) records where the slicer put the pause and what
it laid over the bars either side of it.

The wall coupon is 84 × 68 mm of the 6 mm wall with the hole back-top would take, so the snap can
be tried without a back-top.

![Machine-side plate](renders/print-machine-side.png) ![Plug-side plate](renders/print-plug-side.png)

## Hardware for one pair

| Part | Each pair |
| --- | --- |
| [K&J SB443-IN](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet) | 4 |
| John Guest [PP0408W](/hardware/reference/jg-pp0408w/) union | 3 |
| neoFit [AUC44M](https://www.freshwatersystems.com/products/neofit-acetal-black-union-connector-4mm-5-32-tube-x-4mm-5-32-tube) 4 mm union | 1 |
| [YYFKGCP pogo pair](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md) with four M1.4 × 4 × Ø2.3 inserts and four M1.4 × 8 screws | 1 |
| [ruthex RX-M3x5.7](https://www.amazon.com/dp/B08BCRZZS3) insert and M3 × 8 socket-head screw | 2 |

## Assembly

1. Set the M1.4 inserts in both pogo seats, their tops 2 mm behind the ear plate's step, as on the
   [cartridge](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md), and the two M3 inserts in the
   socket's back face.
2. Socket: solder four leads to the spring-pin half, feed them back through the floor's centre
   channel and screw the half down, marked end up. Slide the unions in from the back, the AUC44M
   at DRAIN's corner, and screw the retainer on. Push the socket into the wall from outside until
   both leaves click. The machine's tubes push into the unions' rear collets through the retainer.
3. Plug: feed the ribbon in at the top of the back face and out through the pogo seat, solder it to
   the pad half and screw the half down, marked end up. Push the four tubes through from the back
   to their stub lengths and press the key in from the DRAIN side until it is flush.

## Not established

- Every fit here is geometry: the plug in the cup, the bars on their rails, the leaves in the
  wall, the key's grip. None has been printed.
- Neither neoFit nor John Guest dimensions the AUC44M's collet sleeve. Its back stop assumes a
  sleeve at least 1.0 mm proud, and its 13.0 mm insertion is John Guest's for the PM0404E
  ([DS-PM04](https://docs.rs-online.com/0f8c/0900766b800bd8c0.pdf)), which neoFit lists as its
  equivalent. Check both on the part.
- The force to push four collets on at once, the key's hold on the tubes, and the bars' installed
  pull. K&J rates the SB443-IN at 3.42 lb to steel at contact.
- What the first layer printed over each N42 bar does to it.

## Rebuild

```sh
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/scene.py
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/prepare_prints.py
python3 tools/viz/build.py future/umbilical-plug-and-socket-exploration/viz-spec.json --out future/umbilical-plug-and-socket-exploration/one-plug-umbilical.html
```

[`umbilical.py`](umbilical.py) draws the parts. `scene.py` writes the scene STEPs and viewer
payloads to `out/`, which git ignores, and prints its clearance check.
`prepare_prints.py` writes the two projects from the shared profile, slices them with the
installed Bambu Studio, checks the pause in the emitted G-code and sends nothing to a printer;
`--printer H2C` writes the same jobs with H2C's trim.

## Sources
[value](NAME) texts are updated by:
- `/future/umbilical-plug-and-socket-exploration/prepare_prints.py`
- `/future/umbilical-plug-and-socket-exploration/scene.py`
