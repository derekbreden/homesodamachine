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

The PSU, relay, and Wago column **pack flush** against each other (no inter-part
gaps). Off this tray: the **GFCI** (tabled), the **C14 inlet** (back panel), and
the controller modules (a separate controller tray).

A wide-and-shallow alternative is the sibling
[narrow power tray](/hardware/printed-parts/electronics/narrow-power-tray/) (PSU
turned 90°). Both layouts are built by the same `build_tray(L)` engine here, from
a `Layout` of component centres + Z rotations.

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

The floor is a **single solid floor** (3 mm) — the convex outline of every
object's footprint, so it reads as a rough map of the space the parts occupy
while the layout is still being worked. One connected piece, no thin trusses; it
re-derives from the part footprints, so it follows along as things are
rearranged. Local frame: X right, Y deep, Z up; origin at the bottom-left
corner. Zone-B placement, joinery, and any final trim/stiffening are deferred
until the arrangement settles.

`power_tray.py` → `power-tray.step`; `power_assembly.py` → `power-assembly.step`
(tray + parts seated). Regenerate with `tools/cad-venv/bin/python <script>`.
