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
| post in the plate | [6.000](PANEL_GRIP) mm, all of it |
| air round the port | [1](PANEL_PORT_SLIP) mm, the box's own figure for air round a body |
| socket to port channel | [1.115](PANEL_WEB) mm — **measured**, [265](PANEL_WEB_PCT)% of a [0.42](PANEL_EXTRUSION) mm bead |
| material, both panels | [162.79](PANEL_VOL) cm³ of `enclosure-front-top` |

## What holds a valve

Four blind sockets, one under each of the Beduan's corner posts, the post pressed into it
([`../../valve-seat/`](/hardware/printed-parts/valve-seat/)). The posts in their sockets are the
whole of the retention — nothing bolts a valve and nothing is bonded — and the valve's own round
body boss lands **on the plate's own face**, which is what sets its height. Every valve on either
plate seats the same way.

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

## The wall between a socket and the port channel

The sockets run down the valve's own axis and the port channel across the plate on its Y, and
where they pass each other is the thinnest material in the plate: [1.115](PANEL_WEB) mm.
`web()` measures it rather than striking it off the radii — the two features' axes come closest
above the socket's own top, so arithmetic answers for a cylinder that is not there.

**Read that against the nozzle, not against zero.** These plates are `enclosure-front-top`'s
material, so they come off the enclosure exterior's own bead of [0.42](PANEL_EXTRUSION) mm
([`enclosure/print-log.md`](/hardware/printed-parts/enclosure/enclosure/print-log.md)), and the
web is [265](PANEL_WEB_PCT)% of one. A wall thinner than a bead is not a thin wall, it is
absent, and a solid states material at any width — so `panel-web` is the one check on this
plate that reads what the machine can lay rather than what the model draws.

## Where the two go

Read off the placed valves at every build, never stated — `manifold_layout` folds the pack and
[`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) stands it on the
refrigeration base's crown, so where a deck lands is that stack's arithmetic. `valve_panel_decks`
groups the valves no cap cradle holds by the plane each stands on and hands back one panel per
plane, and the `panels-hold` gate reads every valve against the plate under it.

| panel | valves | stands |
|---|---|---|
| `valve-panel-aft` | V-C, V-D, V-G, V-J | aft of its deck, bosses facing forward |
| `valve-panel-fore` | V-E, V-F, V-H, V-I | forward of its deck, bosses facing aft |

The two face each other with both decks between them, and both are the same plate: a valve is
held one way in this machine, wherever it stands.

## Print

Both panels come off the bed inside `enclosure-front-top`, which prints standing on a Z face. So
a plate stands vertical, wall to wall — and **nothing stands off it**. A sunk socket is a blind
hole in solid material and a port channel is a notch that runs up the plate's own section, so
there is no overhang in this feature and no support in it to pick out. That is what the
thickness buys: a boss on a standing plate is a Ø13.2 cylinder cantilevered into air, with its
own underside to bridge and its root standing on nothing, and this plate carries thirty-two of
them. PETG, the piece's own stock ([`bom.md`](/hardware/ledger/bom.md) §7, in the front-pieces
row).

## Open items

1. **`panel-web` is the only bound on this plate that reads what a nozzle can lay.** Everything
   else about it — the sockets' clearance, the channel's floor, the seats' pitch, the margin past
   the last seat — is read against a solid, and a solid states material at any width. The plate
   comes off one [0.42](PANEL_EXTRUSION) mm bead, so a feature the model draws thinner than one
   reads green in every check but that one. `EXTRUSION_W` is named once in the whole tree.

## Files

- `valve_panel.py` — the panel's own figures, and one drawn in its own frame for the wall to turn

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the plate
against the valve it holds and the seat it carries.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/valve-panel/valve_panel.py`
