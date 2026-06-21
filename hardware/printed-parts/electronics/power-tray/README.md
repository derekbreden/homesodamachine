# Power tray (PSU + AC distribution)

The AC-in / 12 V-out block of the Zone-B electronics shelf — the first of the
electronics trays. It carries the mains-side parts on one printed frame:

```
   ┌──────────┬───────────────────────┐
   │          │   ( GND )             │
   │   PSU    │  ┌────┐    ┌──────┐    │
   │ (IRM-90) │  │relay│   │ Wago G│   │
   │  AC end↑ │  │  #1 │   ├──────┤    │
   │  DC end↓ │  │     │   │ Wago N│   │
   │          │  └────┘   ├──────┤    │
   │          │           │ Wago H│   │
   └──────────┴───────────┴──────┴────┘
```

## What mounts here

- **[Mean Well IRM-90-12ST](/hardware/reference/meanwell-irm90/) PSU** — the
  12 V supply; AC mains in one end, the 12 V bus out the other.
- **[Teyleten relay #1](/hardware/reference/teyleten-relay/)** — switches the
  compressor's 120 VAC hot leg.
- **3× [Wago 221-413](/hardware/reference/wago-221-413/)** — the H / N / G AC
  distribution block.
- **[Ground ring-terminal stack](/hardware/reference/ground-ring-stack/)** — the
  single-point chassis ground. One heat-set M3 boss takes a screw that clamps a
  fan of green ring lugs (one per exposed-metal part) into a bolted stack. The
  stack *is* the bus — there is no copper bar — and it's earthed through the C14
  cord (Class I). See [`/business/regulatory.md`](/business/regulatory.md).

Off this tray: the **GFCI** (tabled), the **C14 inlet** (back panel), and the
controller modules (a separate controller tray).

## Retention — press fit throughout

Same idiom as the valve trays and the enclosure:

- **PSU and Wagos** drop into **press-fit pockets** — walls one 0.15 mm
  clearance off the body. The PSU end walls are notched for its terminal wiring;
  each Wago pocket is open on its wire-entry face, with the levers clearing above.
- **Relay #1** presses onto **four posts** that enter its mounting holes (the
  reverse of the valve's posts-into-sockets, since the board has the holes). The
  posts stand the board off so its underside pins clear the floor.

The one exception is the **ground boss** — press fit doesn't apply to a safety
bond carrying fault current. It takes a heat-set M3 insert (the same insert +
SHCS idiom as every module on the shelf), and the screw clamps the ring-terminal
stack metal-to-metal.

## The tray

A flat frame plate (~**116 × 125 mm**, 3 mm floor) with a perimeter stiffening
lip. Local frame: X right, Y deep, Z up; origin at the bottom-left corner.
Zone-B placement and tray-to-enclosure joinery are deferred — this first pass
just gets the loose parts attached to one printed part.

`power_tray.py` → `power-tray.step`; `power_assembly.py` → `power-assembly.step`
(tray + parts seated). Regenerate with `tools/cad-venv/bin/python <script>`.
