---
title: One machine, and its first hour on a bench
start: 2026-07-19
end: 2026-08-15
kind: period
lede: Two machine designs ran side by side for eight days and the narrow one survived, and the controller board was powered up for the first time.
---

## Two machines, then one

On 26 July the whole hardware tree was copied into a second edition — a tall narrow machine with the cold core turned a quarter turn so its short axis runs across the cabinet. The two trees then diverged: 290 files apart, 128 of them source.

On 3 August the original counter machine was deleted and the narrow one moved into its place. One content root, one edition. The published silhouette went from 317 × 375 × 337.7 mm to 223 × 481 × 358 mm — 94 mm narrower, 106 mm deeper.

Everything since has been subtraction. The stripped-down Lite edition went on 27 July. The sheet-metal compressor shroud was designed out, replaced by a thermal cutoff held against the compressor's power box by a printed clamp. Capacitive sensing was cut on 10 August, one day after being placed, because no firmware read it. The valve trays, the pump case and the separate front and back panels are gone — eight solenoids and both pumps now stand on the enclosure's own front-top piece, printed wall to wall, and the whole flavor manifold lifts out as one body with the carbonator still full and pressurised.

Per-unit parts cost fell to about $1,282. Both assembly models went from failing their own checks to 96 of 96 gates passing. The gate count grew from 11 to 72 over the same weeks the scores rose.

## The board on the bench

On 3 and 4 August a delivered controller board was powered up for the first time and driven from a bench console.

Confirmed working: the power rails, the microcontroller, USB-C flashing, WiFi at 15 networks, the RS485 loopback at 6 of 6, the buzzer, the status LEDs, the gas divider at 3020 mV, the compressor interlock, and both peristaltic pump drivers turning a real pump on both channels. A touchscreen panel on the board's RS485 link ran a pump remotely and held it to prime across 32 consecutive holds with all 77 frames arriving.

Confirmed dead: the entire I²C bus. Both I/O expanders, the real-time clock, all twelve valve outputs, ten reed inputs and the fan output are unreachable.

The cause is in the project's own drill-file generator, which emitted 135 holes against 152 vias because partial-span vias were dropped. The fab drilled exactly what it was sent.

Ten more assembled boards were ordered the same day, $702.11, with all 152 vias drilled behind an assertion that matches every via one-to-one before any file is written, inner-layer annular rings on three connector pins, and a second-source USB bridge. They shipped on 12 August and reached the Omaha sort facility on the 15th.

## Building one

A 94-card printed bench manual was written — one card per hand operation, from welding the pressure vessel through burn-in and packing, rendered to a print-ready PDF, with a check that fails the build if a card overflows its band. Thirteen letter-size tool-station cards followed: drill press, band saw, laser welder, hydro test, tube bench, braze bench, vacuum and charge, crimp, solder, electrical test, plastic fittings, pour and cure, printers.

The machine now costs itself out. Attended human build time reads 9 h 55 m per unit at $100/hr; machine occupancy reads 94.2 printer-hours per unit, anchored on one measured print of 1142 g in 14 h 22 m.

The purchase ledger became machine-checkable — order number, ordered date and delivered date as their own columns, joined to a committed record of the actual orders. Reconciling it found the ten carrier boards sitting at on-order for six weeks after they had arrived on 3 July.

The CAD tree got a build system on 13 August: 99 build actions, with the dependency graph learned by watching each generator run and recording every file it opens.

## Water, CO2 and a new material

The internal water line was rebuilt to stay at ¼ inch from the backflow preventer to the pump, which wrote off four already-purchased 3/8-inch fittings. Two orders closed the remaining gaps — the flare-to-¼-inch adapter and clamps on 24 July, and the whole rear-wall CO2 chain in one tube size on 11 August.

The enclosure's front-top panel went on the printer in glass-filled PET on 15 August, at 290 °C nozzle, 100 °C bed and 50 °C chamber, with every geometric and profile setting identical to the PETG version.

## The site

The daily feed that ran from 7 March to 28 June was removed on 15 August, along with its routes and its push path. In its place the site carries a build tree: one unit's assembly as a drill-down read off the build order, the procedures, their step headings and the cards, with no list kept by hand.
