# Valve panel

A flat plate with four valve seats **sunk into it**, running from side wall to side wall inside
`enclosure-front-top`. **It is not a part.** It is that piece's own material, fused the way the
tap-water trough, the flow meter's saddles and the pump trays are — `enclosure._valve_panels` stands one, off
the stations `enclosure_assembly.valve_panel_stations` reads off the placed valves. Nothing
ships under a valve and nothing is billed for one.

The flavour manifold's fold leaves eight of its ten Beduan solenoids standing on two planes,
four to a plane. Each plane gets a panel: [2](PANEL_COUNT) per machine.

| | |
|---|---|
| plate | [209](PANEL_W) wide × [43.6](PANEL_H) × [10](PANEL_T) mm |
| seats | [4](PANEL_SEATS), on the plate's own centreline |
| socket | Ø[7.2](SOCKET_DIA) × [7](SOCKET_DEPTH) deep — a corner post presses in |
| behind a socket | [3](SOCKET_FLOOR) mm of plate, one wall |
| port channel | Ø[17](CHANNEL_DIA), [3.20](CHANNEL_DEPTH) deep, out both ends of the plate |
| under a channel | [6.80](CHANNEL_FLOOR) mm of plate |
| seat height | [-6](PANEL_SEAT) mm — the seat is **sunk**, so nothing stands off the face |
| depth on the deck's plane | [10](PANEL_D) mm, the plate and nothing else |
| post over the mounting plane | [6](PANEL_POST) mm — the whole of what a socket can hold |
| face set off its valves | 0 on the still deck, [2.835](PANEL_SETBACK) mm on the travelling one |
| socket, travelling deck | [9.835](PANEL_SOCKET_LONG) mm long — the floor sinks by that figure, the mouth does not move |
| post in the plate at rest | [6](PANEL_POST) mm still, [3.165](PANEL_GRIP) mm travelling |
| material, both panels | [162.79](PANEL_VOL) cm³ of `enclosure-front-top` |

## What holds a valve

Four blind sockets, one under each of the Beduan's corner posts, the post pressed into it
([`../../valve-seat/`](/hardware/printed-parts/valve-seat/)). The posts in their sockets are the
whole of the retention — nothing bolts a valve and nothing is bonded. On the still deck the
valve's own round body boss lands **on the plate's own face**, which is what sets its height;
on the travelling deck it stands off that face and something else does, which is the section
below.

**A boss is material round a socket, and this plate is that material.** It is one socket and one
wall thick, so the seat is sunk into it rather than stood on it: the same
[7.2](SOCKET_DIA) × [7](SOCKET_DEPTH) hole, opening on the face the valve lands on, with
[3](SOCKET_FLOOR) mm of plate behind. The cold core's cap lid, whose lid is thinner than a
socket is deep, stands the bosses instead — one seat, two ways to carry it.

The one thing the face opens for is the valve's own **port**, which hangs
[2.20](PORT_DROP) mm under that face and would otherwise be buried: each seat takes a
Ø[17](CHANNEL_DIA) channel on the plate's own Y, the port's barrel and a
[1](PORT_SLIP) mm slip, [3.20](CHANNEL_DEPTH) deep on [6.80](CHANNEL_FLOOR) mm of floor. The
barrel is longer than the plate is high, so the channel runs clean out of both ends.

The plate's height is the seats' own reach off their valves' centres, [18.8](PANEL_REACH) mm,
and one [3](PANEL_MARGIN) mm margin past that. Each valve's two quick-connect collets and the
tube butted into them hang past it in air.

## The deck that travels

One deck is butted onto the anchor tees of the pump cartridge's release
([`../enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md) "The pump
cartridge and its bay"). Its four valves make the release stroke with the tees they butt, so
**its plate's face is where those valves ARRIVE, not where they rest.** The face stands
[2.835](PANEL_SETBACK) mm — the whole stroke — off the plane a seated body boss would land on,
and each socket's floor sinks by the same figure to [9.835](PANEL_SOCKET_LONG) mm so a post does
not bottom before the travel is spent. The mouth, the radius and the [3](SOCKET_FLOOR) mm of
floor behind are untouched: it is the same plate, standing somewhere else.

**The boss does not touch it at rest.** The valve stands one stroke off, in air, and what sets
its height is the anchor tee it butts — held across its own axis by the printed wall behind the
collet plate (`enclosure._tee_wall`) and free along it. At full release the boss lands on the
face, so the face is the stop that ENDS the stroke rather than the one the valve rests on. This
is the one deck whose valves are located by the manifold rather than by their own plate.

**A post stands [3.165](PANEL_GRIP) mm inside the plate's section at rest**, of the
[6](PANEL_POST) mm it has, reaching its whole length only at full release. The posts in their
sockets are the whole of the retention, so this deck is held LEAST in the state the machine runs
in and most while the cartridge is being pulled out. What the plate actually surrounds is read
rather than subtracted — the port channel crosses close to the sockets here, and a figure struck
off the setback alone would not know it.

**The port travels with the body**, so its channel is struck along the whole sweep instead of
where the port rests (`build_port_channel`): round at both ends, a slot only over the stretch the
port crosses.

## Where the two go

Read off the placed valves at every build, never stated — `manifold_layout` folds the pack and
[`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) stands it on the
refrigeration base's crown, so where a deck lands is that stack's arithmetic. `valve_panel_decks`
groups the valves no cap cradle holds by the plane each stands on and hands back one panel per
plane, and the `panels-hold` gate reads every valve against the plate under it.

| panel | valves | stands | face |
|---|---|---|---|
| `valve-panel-aft` | V-C, V-D, V-G, V-J | aft of its deck, bosses facing forward | on its valves — they stand still |
| `valve-panel-fore` | V-E, V-F, V-H, V-I | forward of its deck, bosses facing aft | one stroke off — its valves travel |

The two face each other with both decks between them. Which one travels is read off the placed
pack at every build and never named here: `valves_on_anchor_tees` says whose valves butt a tee,
so a re-folded manifold moves the setback with it.

## Print

Both panels come off the bed inside `enclosure-front-top`, which prints standing on a Z face. So
a plate stands vertical, wall to wall — and **nothing stands off it**. A sunk socket is a blind
hole in solid material and a port channel is a notch that runs up the plate's own section, so
there is no overhang in this feature and no support in it to pick out. That is what the
thickness buys: a boss on a standing plate is a Ø13.2 cylinder cantilevered into air, with its
own underside to bridge and its root standing on nothing, and this plate carries thirty-two of
them. PETG, the piece's own stock ([`bom.md`](/hardware/ledger/bom.md) §7, in the front-pieces
row).

## Files

- `valve_panel.py` — the panel's own figures, and one drawn in its own frame for the wall to turn

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the plate
against the valve it holds and the seat it carries.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/valve-panel/valve_panel.py`
