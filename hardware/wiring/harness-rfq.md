# Harness RFQ

The vendor-facing package for the appliance's ten low-voltage cable assemblies — everything a
cable-assembly shop needs to quote and build them without reading the rest of this repo. It is the
*outsourced* view of [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md):
same assemblies, same terminations, restated as a wire list with pin-level from/to.

Branch geometry is [`harness-branches.mmd`](/hardware/wiring/harness-branches.mmd) — send it with
this file. Board pin map is [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), canonical.

## Scope

**In:** ten assemblies — J1, J2, J3, J4, J5, J6, J7, J9, J11, J13.

**Out:** the J10 12 V inlet (2 × 16 AWG, ferrules, on-shelf) and every AC mains run (AC-1…6, 16 AWG
+ 18 AWG SJOOW), built in place per [`wiring.md`](/hardware/assembly/wiring.md).

Everything in this RFQ is 22 AWG or 28 AWG.

### The WAGO fan-outs are built in-house

The five branch nodes in the table below are **excluded from the quote**. A vendor supplies each
affected assembly as its trunk only — every board-side conductor run to its full length and
terminated at the device end — and the lever nut and its branch legs are made off here. A 221 lever
nut takes no crimp and no tooling, and on the one assembly priced both ways the fan-out was 45 % of
the assembled cost.

So: quote the wire lists below as written, and ignore the `— … branch` rows.

## Build quantity

Quote **25, 50, and 100 sets** (a set = all ten assemblies).

## Workmanship standard

**IPC/WHMA-A-620, Class 2.** Every assembly 100% continuity- and isolation-tested pin-to-pin against
its wire list below, including the deliberate non-connection at J2 contact 3.

## Materials

| Item | Spec | Notes |
|---|---|---|
| Signal / actuator wire | 22 AWG stranded tinned-copper **silicone**, 600 V, **black** | all ten assemblies except J3 — **see Open question 1, the gauge is not settled** |
| Ribbon | 28 AWG 4-conductor jacketed ribbon, black | J3 only |
| Board-end housings | JST **XH**, 2.5 mm pitch, female crimp housing + contacts | XHP-*n* per assembly; "XH2.54" is the series name, the pitch is 2.50 mm |
| Device-end tabs | Female Faston disconnects, **6.3 mm and 4.8 mm** | at 20–24 AWG these are TE **2178438-1** (250 / 6.3 mm) and **170214-2** (187 / 4.8 mm); per-device size map not yet recorded |
| Screw landings | Insulated bootlace ferrules, DIN, 22 AWG | J5 relay terminals, J9 display terminals |
| Fan-out splices | **WAGO 221-420** (10-way) and **221-415** (5-way) | supplied loose or made off, see below |
| Sleeve | Black PET expandable braided, 1/4" / 1/2" / 3/4" per assembly | both cut ends finished with black heat-shrink |
| Ties | Black UV-nylon, flush-cut, no proud tail | |

Every conductor is black. Identification is **by assembly name at the housing** (heat-shrink
marker), not per-conductor. Do not substitute a color code.

### The WAGO fan-outs are in-assembly splices

Five assemblies terminate a shared rail in a WAGO 221 lever nut at the **device end**, not at the
board: one rail conductor rides the trunk and explodes at the manifold or reservoir. The nut body
press-fits into a well printed in the enclosure wall. Do not substitute heat-shrink butt splices.

| Assembly | Nut | Ways used | Feed | Branches |
|---|---|---|---|---|
| J1 MANIFOLD A | 221-420 | 9 of 10 | `COM` | 8 valve `+` |
| J2 MANIFOLD B | 221-415 | 5 of 5 | `COM` | V-I, V-J, fan, V-K `+` |
| J4 SENSORS | 221-415 | 4 of 5 | `GND` | 1-wire bus, flow meter, moisture plate |
| J6 REEDS A | 221-415 | 5 of 5 | `GND` | 4 reeds |
| J7 REEDS B | 221-420 | 7 of 10 | `GND` | 6 reeds |

## Board-end contact order

**Read contact order from this table, not from conductor names elsewhere.** Two connectors are
numbered opposite to how their signals read: J1 runs `OUT8`→`COM`, and J6 runs `GND`,`RA4`…`RA1`.
Contact 1 is the pin-1 end of the housing.

| Conn. | Housing | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| J1 MANIFOLD A | XHP-9 | `OUT8` | `OUT7` | `OUT6` | `OUT5` | `OUT4` | `OUT3` | `OUT2` | `OUT1` | `COM` |
| J2 MANIFOLD B | XHP-6 | `COM` | `FAN` | **empty** | `OUT3` | `OUT2` | `OUT1` | | | |
| J3 FAUCET | XHP-4 | `GND` | `V5` | `IO35` | `IO33` | | | | | |
| J4 SENSORS | XHP-7 | `3V3` | `GND` | `V5` | `IO25` | `IO26` | `IO27` | `IO23` | | |
| J5 RELAYS | XHP-4 | `GND` | `V5` | `IO2` | `IO19` | | | | | |
| J6 REEDS A | XHP-5 | `GND` | `RA4` | `RA3` | `RA2` | `RA1` | | | | |
| J7 REEDS B | XHP-7 | `RB1` | `RB2` | `RB3` | `RB4` | `CLO` | `CHI` | `GND` | | |
| J9 DISPLAY | XHP-4 | `B` | `A` | `GND` | `V12` | | | | | |
| J11 GAS | XHP-4 | `GND` | `V5` | `DOUT` | `AOUT` | | | | | |
| J13 PUMPS | XHP-4 | `AM2` | `AM1` | `BM2` | `BM1` | | | | | |

### J2 contact 3 is deliberately empty

J2's wafer is 6-way; only five conductors are populated. `OUT4` is a routed spare that drives no
valve. **Crimp five contacts into an XHP-6 in their labelled positions and leave contact 3 empty.
Do not close the gap.** Contact 3 is mid-housing, not on an end — a loom filling 1–5 consecutively
lands every conductor one position off, which puts the shared 12 V rail on a driver output. Verify
the empty cavity at final test.

### J4 and J7 share a housing

Both are XHP-7. A swap would put J4's `3V3`/`V5` onto J7's reed inputs. **Label both at the
housing.**

## Wire lists

Lengths are conductor cut lengths from the board contact to the device termination, service loop
excluded — add your standard allowance. They are design targets from the enclosure layout, not yet
measured against a built enclosure.

### J1 — MANIFOLD A · XHP-9 · 3/4" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1–8 | `OUT8`…`OUT1` | valves V-H…V-A, one each | ~450 mm | female Faston |
| 9 | `COM` | 221-420 at the manifold | ~300 mm | ferrule |
| — | 8 × `COM` branch | 221-420 → each valve `+` | ~150 mm | ferrule / female Faston |

Trunk is 300 mm to the manifold, then a 150 mm fan-out per valve. Low-side switching: `COM` carries
shared 12 V to every valve `+`; each valve `−` returns on its own `OUT`.

### J2 — MANIFOLD B · XHP-6, 5 populated · 1/2" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `COM` | 221-415 at the manifold | ~300 mm | ferrule |
| 2 | `FAN` | condenser fan `−` | ~400 mm | female Faston |
| 3 | — | **empty, do not populate** | — | — |
| 4 | `OUT3` | valve V-K `−` at the aft strip | ~500 mm | female Faston |
| 5 | `OUT2` | valve V-J `−` | ~450 mm | female Faston |
| 6 | `OUT1` | valve V-I `−` | ~450 mm | female Faston |
| — | 4 × `COM` branch | 221-415 → V-I, V-J, fan, V-K | 150 / 150 / 100 / 200 mm | ferrule / female Faston |

All four branches leave the 221-415 at the manifold, 300 mm along the trunk.

### J3 — FAUCET · XHP-4 · 28 AWG 4-conductor ribbon

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `GND` | faucet display GND | ~1 m | per display, see Open questions |
| 2 | `V5` | faucet display 5 V | ~1 m | " |
| 3 | `IO35` | display TX | ~1 m | " |
| 4 | `IO33` | display RX | ~1 m | " |

Straight-through 4-conductor ribbon up the umbilical, no branch. TTL UART; ESD clamping is on the
board, so no cable-end component is required.

### J4 — SENSORS · XHP-7 · 1/4" sleeve · three-way branch

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `3V3` | 1-wire temp bus | ~600 mm | per device |
| 2 | `GND` | 221-415 on the −X wall aft | ~600 mm | ferrule |
| 3 | `V5` | flow meter | ~150 mm | per device |
| 4 | `IO25` | flow meter pulse | ~150 mm | per device |
| 5 | `IO26` | 1-wire data | ~600 mm | per device |
| 6 | `IO27` | moisture sensor DO | ~600 mm | per device |
| 7 | `IO23` | moisture sensor switched VCC | ~600 mm | per device |
| — | 3 × `GND` branch | 221-415 → 1-wire, flow meter, moisture | short pigtails | ferrule |

The flow-meter leg (contacts 3, 4) leaves the trunk at ~150 mm; the other two legs run on to ~600 mm.

### J5 — RELAYS · XHP-4 · 1/4" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `GND` | relay #1 and #2 GND | ~150 mm | ferrule, teed to both |
| 2 | `V5` | relay #1 and #2 VCC | ~150 mm | ferrule, teed to both |
| 3 | `IO2` | relay #2 IN | ~150 mm | ferrule |
| 4 | `IO19` | relay #1 IN | ~150 mm | ferrule |

`V5` and `GND` tee at the relay screw terminals — **no WAGO on this assembly.**

### J6 — REEDS A · XHP-5 · 1/4" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `GND` | 221-415 at reservoir A | ~600 mm | ferrule |
| 2–5 | `RA4`…`RA1` | reservoir A level reeds 4…1 | ~600 mm | reed leads |
| — | 4 × `GND` branch | 221-415 → each reed | short pigtails | ferrule |

Note the reversed order: contact 2 is `RA4`, contact 5 is `RA1`.

### J7 — REEDS B · XHP-7 · 1/4" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1–4 | `RB1`…`RB4` | reservoir B level reeds 1…4 | ~600 mm | reed leads |
| 5 | `CLO` | carbonator low reed | ~600 mm | reed leads |
| 6 | `CHI` | carbonator high reed | ~600 mm | reed leads |
| 7 | `GND` | 221-420 at the cold-core end | ~600 mm | ferrule |
| — | 6 × `GND` branch | 221-420 → each reed | short pigtails | ferrule |

Same XHP-7 as J4 — label at the housing.

### J9 — DISPLAY · XHP-4 · 1/2" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `B` | display RS485 B | ~1 m | ferrule |
| 2 | `A` | display RS485 A | ~1 m | ferrule |
| 3 | `GND` | display 7–36 V input GND | ~1 m | ferrule |
| 4 | `V12` | display 7–36 V input + | ~1 m | ferrule |

**`A` and `B` twisted pair** over the run; `V12`/`GND` ride the same sleeve.

### J11 — GAS · XHP-4 · 1/4" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `GND` | MQ-6 GND | ~600 mm | per device |
| 2 | `V5` | MQ-6 VCC | ~600 mm | per device |
| 3 | `DOUT` | MQ-6 digital trip | ~600 mm | per device |
| 4 | `AOUT` | MQ-6 analog | ~600 mm | per device |

Straight-through, no branch.

### J13 — PUMPS · XHP-4 · 1/2" sleeve

| Contact | Signal | To | Length | Termination |
|---|---|---|---|---|
| 1 | `AM2` | pump A motor tab 2 | ~400 mm | female Faston |
| 2 | `AM1` | pump A motor tab 1 | ~400 mm | female Faston |
| 3 | `BM2` | pump B motor tab 2 | ~400 mm | female Faston |
| 4 | `BM1` | pump B motor tab 1 | ~400 mm | female Faston |

Two differential H-bridge pairs, no shared rail and no fan-out. The pumps ride a cartridge that
withdraws from the enclosure, so these four run **unbroken** from housing to motor tab, and the
length must hold with the cartridge drawn fully out — do not shorten.

## Open questions for the vendor

1. **Wire gauge into the XH housings — open, and we want your read.** The schedule says 22 AWG
   silicone. 22 AWG silicone does not pass crimp-compatibility checks into JST XH: the XH contact's
   22–30 AWG rating is a conductor rating, and silicone's insulation OD at 22 AWG is over what the
   barrel closes on. The same 22 AWG passes into XH in UL 1007, UL 1015, UL 1061 and ThermoThin, and
   silicone passes into XH from 24 AWG down. **Please quote the option you would actually build**,
   from: (a) 24 AWG silicone on the XH looms, (b) 22 AWG thin-wall (UL 1061 or similar), (c) 22 AWG
   silicone with a different board-side connector family. Current draw on these looms is negligible
   except MANIFOLD A `COM`, which carries ≤ ~1.4 A over ~300 mm.
2. **Faston sizes.** `cable-assemblies.md` calls for both 6.3 mm and 4.8 mm disconnects; the
   per-device map is not yet recorded. Quote against a stated assumption and we will confirm before
   release.
3. **WAGO nuts — supplied or made off?** Preference is made off as part of the assembly. If your
   process cannot land a lever nut in-line, quote with the nut supplied loose and the branch
   conductors ferruled to length.
4. **Device-end terminations on J3, J4, J11.** Sensor and display leads land per device rather than
   on a standard terminal. Quote these as flying leads, tinned and ferruled, unless you would rather
   we specify a mating connector.
5. **28 AWG ribbon.** Confirm you can crimp XH contacts onto 28 AWG, or propose the gauge you would
   rather run in the umbilical.

## Sources

Derived from, and kept consistent with:

- [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) — fabrication view
- [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) — run table, lengths
- [`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) — contact order, canonical
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 — stock and part numbers
