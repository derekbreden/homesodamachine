# Power tray (PSU + AC distribution)

The AC-in / 12 V-out block of the Zone-B electronics shelf — the first of the
electronics trays. It carries the mains-side parts on one printed frame:

```
   ┌─────────────────────────────────────────┐
   │  ○        ○      ○ (GND stud)            │
   │    ┌──────┐   ┌────┐                      │
   │    │ PSU  │   │relay│   ◹ ◹ ◹  Wagos —    │
   │    │IRM-90│   │ #1 │    butt in slot,     │
   │    └──────┘   └────┘    angled 45° up     │
   │  ○        ○   ○    ○                      │
   └─────────────────────────────────────────┘
   ○ = M3 heat-set boss (screw mount / ground stud)
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

## Retention

Two idioms, both already used elsewhere in the appliance:

- **PSU and relay #1 — heat-set M3 inserts + SHCS** (the electronics-shelf
  module idiom). The PSU screws down through its four ledge holes onto four low
  bosses — just tall enough to seat an insert, no clearance standoff. Relay #1
  screws onto four taller **standoff bosses** that stand the board off so its
  ~2 mm underside pins clear the floor.
- **Wagos — angled press-fit slots.** Each lug tilts **45° up** toward its wire
  end and drops butt-end-first into a slot that wraps the butt half on five faces
  (both X, both Z, and the −Y end) at one 0.15 mm clearance, open toward the wire
  end. The lug sticks halfway out so the levers and wire ports stay accessible.

The **ground boss** is the same heat-set insert idiom — a safety bond carrying
fault current, so the screw clamps the ring-terminal stack metal-to-metal rather
than relying on a press fit.

## The tray

A flat plate (~**116 × 125 mm**, 3 mm floor) carrying the bosses and slots.
Local frame: X right, Y deep, Z up; origin at the bottom-left corner. Zone-B
placement, tray-to-enclosure joinery, and any floor stiffening are deferred —
this first pass just gets the loose parts attached to one printed part.

`power_tray.py` → `power-tray.step`; `power_assembly.py` → `power-assembly.step`
(tray + parts seated). Regenerate with `tools/cad-venv/bin/python <script>`.
