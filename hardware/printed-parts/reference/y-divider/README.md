# Y-divider — reference fitting (stand-in)

`y-divider.step` is **McMaster 51055K417**, a 1/4" push-to-connect
drinking-water divider, used as a close stand-in for the **John Guest
PP2308E** two-way divider in the BOM (`hardware/bom.md`) — the part every
Y-junction (Y-A/B/C/D/E/F/G/H/KA/KB) in the
[fluid topology](../../../topology/fluid-topology.md) is built from. It is
not the exact part, but it is geometrically very close for layout work.

## Geometry (measured from the STEP)

Overall body envelope **16.2 × 30.9 × 38.5 mm**. It is a **"trident"**, not
a splayed Y: one **stem** and two **parallel outlets**, all three ports
coaxial along the long (38.5 mm) axis.

In the file's own frame (long axis = Z):

| Port | Opens | Location |
|---|---|---|
| Stem | +Z (top), collet face Z ≈ +19.25 | centered, (0, 0) |
| Outlet 1 | −Z (bottom), collet face Z ≈ −19.25 | (0, −7.35) |
| Outlet 2 | −Z (bottom), collet face Z ≈ −19.25 | (0, +7.35) |

So the two outlets point the **same direction**, **14.7 mm apart**, opposite
the stem. That parallel-outlet shape is why valves feeding a divider can stay
axis-aligned (no fanning) — see `../../valve-manifold/quad-tray/`.

Accepts 1/4" (6.35 mm) OD tube; the 1/4" bore radius is 3.175 mm.
