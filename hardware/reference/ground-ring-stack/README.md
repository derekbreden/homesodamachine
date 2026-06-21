# Chassis-ground ring-terminal stack — reference solid

The physical realization of the single-point **ground bus**: the bolted stack
that *is* the bus. There is no copper bar — a copper bar distributes ground
along a run or across many tap points, and this appliance has ~5–6 home-run
bonds landing at one spot. Instead, every green bond ends in a ring terminal and
they all clamp together under one M3 screw on the [power tray](/hardware/printed-parts/electronics/power-tray/)'s
heat-set ground boss. The lugs are bolted to each other, so they are
equipotential — the **stack is the bus**, and the dielectric (plastic) boss it
sits on is electrically irrelevant; it only provides the clamp reaction and
holds the earthed thread.

`ground-ring-stack.step` is a generated stand-in built to make the boss's
purpose legible in the assembly. **Cables are intentionally omitted** — only the
ring tongues and crimp barrels are shown; the green 16 AWG wire crimps into each
barrel and routes off to its chassis-ground target.

## What lands here

The single-point chassis ground per [`/hardware/assembly/wiring.md`](/hardware/assembly/wiring.md)
step 1 and [`/hardware/assembly/electronics-shelf.md`](/hardware/assembly/electronics-shelf.md)
step 3 — one green ring-terminal bond per exposed-metal part:

- Pressure vessel
- Compressor body
- Compressor shroud (run AC-6)
- Faucet under-counter SS plate
- PSU chassis (run AC-2 G)
- the C14 inlet's earth feed (G Wago → bus)

This is a **Class I** appliance ([`/business/regulatory.md`](/business/regulatory.md),
UL 943): the stack is earthed through the C14 cord, so a basic-insulation fault
clears to ground (breaker) and a leak trips the onboard GFCI at 6 mA. The bonds
do not merely tie the metal parts to each other — they tie that bonded node to
building earth.

## Geometry

| | mm |
|---|---|
| Lugs in the fan | **6**, fanned 60° apart, rising one tongue thickness each |
| Ring-terminal tongue | ⌀**8.0** eye, ⌀**3.2** bore, **0.8** thick |
| Crimp barrel | ⌀**4.2** × **6.0** stub (no wire past it) |
| Tooth washer | ⌀**7.0** × **0.8** over the top lug |
| Screw | M3 SHCS, ⌀5.5 × 3.0 head; ~6 mm thread into the boss insert |

Frame: Z up, screw axis on Z, origin at the **landing surface** (the boss top).
Rings stack upward; the shank runs down (−Z) into the heat-set insert. Drop at
the tray's `gnd` boss top (`floor_t + gnd_boss_h`) in the assembly. The boss
takes a **ruthex M3 heat-set insert** (⌀4.0 melt-in bore, 6 mm deep) — the same
M3 SHCS + insert idiom as every other module on the shelf. Regenerate with
`tools/cad-venv/bin/python ground_ring_stack.py`.
