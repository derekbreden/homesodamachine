# Hopper

Pour-to-refill funnel at top of enclosure. PETG structural funnel with removable food-grade silicone insert.

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for coordinates.

---

## 3D Printed Part: Hopper Funnel Body

- **Type:** 3D printed
- **Material:** PETG (structural, does not contact food — silicone insert does)
- **Envelope:** ~100mm top opening diameter x ~70H mm
- **Features:**
  - Top opening: ~100mm diameter
  - Bottom outlet: ~10mm diameter (connects to 1/4" barb fitting)
  - Funnel capacity: ~200-300ml
  - Curved/asymmetric funnel profile: shallow at front, deeper toward back. Profile follows void above lens-shaped bag profile.
  - Interior surface: smooth for silicone insert seating
  - Mounting flange at top rim for attachment to top panel
  - Drain fitting boss at bottom center: 1/4" barb or push-connect
- **Interfaces:**
  - Seats into 100mm hole in top panel from below
  - Flange rests on panel underside, M3 screws into heat-set inserts (3 points, 120 degrees apart)
  - Position: top-front of enclosure, centered at approximately X=106, Y=~40, Z=322-392
  - Bottom outlet connects to hopper feed tube, routed to valve v5/v7
  - Silicone insert drops in from above
- **Quantity:** 1
- **Open:** Exact funnel curvature — depends on physical bag profile at 35 degrees

## Purchased Part: Hopper Silicone Insert

- **Material:** Platinum-cured food-grade silicone (FDA compliant)
- **Envelope:** ~98mm top diameter x ~65H mm
- **Features:**
  - Flexible funnel matching PETG body interior
  - Removable for dishwasher cleaning
  - Bottom opening: ~8mm, mates to funnel body outlet
  - Lip at top rim prevents falling through
- **Quantity:** 1 (spare recommended)
- **Open:** Custom mold vs off-the-shelf trimmed. Wall thickness: ~2mm.

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Hopper integration research:** `research/hopper-integration.md`
- **Top panel:** `../../enclosure-shell/planning/parts.md`
- **Valve routing (v5/v7):** `../../../planning/research/valve-architecture.md`
