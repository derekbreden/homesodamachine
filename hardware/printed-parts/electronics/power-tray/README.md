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
- **Ground-bus tie point** — one M3 boss for the chassis-ground ring-terminal
  stack.

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

## The tray

A flat frame plate (~**116 × 125 mm**, 3 mm floor) with a perimeter stiffening
lip. Local frame: X right, Y deep, Z up; origin at the bottom-left corner.
Zone-B placement and tray-to-enclosure joinery are deferred — this first pass
just gets the loose parts attached to one printed part.

`power_tray.py` → `power-tray.step`; `power_assembly.py` → `power-assembly.step`
(tray + parts seated). Regenerate with `tools/cad-venv/bin/python <script>`.
