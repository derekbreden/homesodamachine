# Valve panel

A flat plate carrying four valve seats, running from side wall to side wall inside
`enclosure-front-top`. **It is not a part.** It is that piece's own material, fused the way the
tap-water trough and the flow meter's saddles are — `enclosure._valve_panels` stands one, off
the stations `enclosure_assembly.valve_panel_stations` reads off the placed valves. Nothing
ships under a valve and nothing is billed for one.

The flavour manifold's fold leaves eight of its ten Beduan solenoids standing on two planes,
four to a plane. Each plane gets a panel: [2](PANEL_COUNT) per machine.

| | |
|---|---|
| plate | [217](PANEL_W) wide × [43.6](PANEL_H) × [3](PANEL_T) mm |
| seats | [4](PANEL_SEATS), on the plate's own centreline |
| socket | Ø[7.2](SOCKET_DIA) — a corner post presses in |
| boss | Ø[13.2](BOSS_DIA) |
| seat height | [1](PANEL_SEAT) mm, so every socket floor lands on the plate's own face |
| depth on the deck's plane | [10](PANEL_D) mm, plate and bosses together |
| material, both panels | [78.30](PANEL_VOL) cm³ of `enclosure-front-top` |

## What holds a valve

Four bosses, one under each of the Beduan's corner posts, each carrying a blind socket the post
presses into ([`../../valve-seat/`](/hardware/printed-parts/valve-seat/)). The posts in their
sockets are the whole of the retention — nothing bolts a valve and nothing is bonded — and the
valve's own round body boss lands on the four boss tops, which is what sets its height. The
same seat the cold core's cap lid prints under its three valves.

The plate's height is the seats' own reach off their valves' centres, [18.8](PANEL_REACH) mm,
and one [3](PANEL_MARGIN) mm margin past that. It ends where the last boss does; each valve's
two quick-connect collets and the tube butted into them hang past it in air. The valve's port
runs [4.80](PORT_GAP) mm over the plate's face at its lowest.

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

The two face each other with both decks between them.

## Print

Both panels come off the bed inside `enclosure-front-top`, which prints standing on a Z face. So
a plate stands vertical, wall to wall, and each boss is a horizontal cylinder off it — the same
cantilever the +X wall's mounting bosses print (`enclosure._east_bosses`). PETG, the piece's own
stock ([`bom.md`](/hardware/ledger/bom.md) §7, in the front-pieces row).

## Files

- `valve_panel.py` — the panel's own figures, and one drawn in its own frame for the wall to turn

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the plate
against the valve it holds and the seat it carries.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/valve-panel/valve_panel.py`
