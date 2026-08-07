# Two-valve tray

The manifold's narrow printed cradle. Eight valves, four trays, **one part** — the
same solid printed four times.

| Tray | Valves | The junction they meet at |
|---|---|---|
| Sources | V-A · V-B | Y-A |
| Selects | V-C · V-D | Y-B |
| Bag A | V-E · V-F | Y-E |
| Bag B | V-H · V-I | — (reservoir B's own two mouths) |

The pairing is [fluid-topology](/hardware/topology/fluid-topology.md)'s own: each
pair is the two valves of one circuit node. The manifold's remaining pair —
the NOZZLE GATES, V-G · V-J, which meet at none — takes one
[single-valve tray](/hardware/printed-parts/valve-manifold/single-valve-tray/README.md)
each, and V-K a third. Per-tray grouping is in
[fluid-topology-limbs.mmd](/hardware/topology/fluid-topology-limbs.mmd).

## Geometry

Two of [`single-tray`](/hardware/printed-parts/valve-manifold/single-tray/README.md)'s
cells on one floor plate, cut by that module's own `cut_cell` — four corner-boss
sockets and a port saddle per seat, so the seats cannot drift from the cell they
came from.

- Plate [72.5](PLATE_X) (X) × [40](PLATE_Y) (Y) × [9](PLATE_Z) (Z), spanning **Z [-3](TRAY_BOT_Z) → [6](TRAY_TOP_Z)**.
- Seats at X = ±[17.12](SEAT_X): centers [34.25](PITCH) apart, which is the valve's own declared X
  keep-out — its footprint plus a pad per side. That is as close as two of them
  pack: the modeled envelopes meet on their pads (an exact-contact pair, not an
  overlap) and the real bodies and coils stand [2](BODY_GAP) mm apart.
- Ports run along Y at Z = [11.3](PORT_Z). The port reaches ±[29.5](PORT_HALF) from its valve center, so
  [9.5](COLLET_PROUD) mm of quick-connect collet stands proud of the plate at each end, clear for
  the tube.
- The valve's round boss bottoms on the plate's top face at Z = [6](TRAY_TOP_Z) and carries the
  vertical load; its coil tops out at [56.6](COIL_TOP), and nothing on the tray reaches that
  high.
- A MOUNT EAR off each port face on the tray's centreline — a ⌀[7.2](EAR_D) tongue, full plate
  thickness, its ⌀[3.4](MOUNT_HOLE_D) M3 clearance hole at Y = ±[24.75](EAR_Y), midway between the
  plate's edge and the collet tips, so the ear ends at [28.35](EAR_TIP) and never reaches past the
  ports. The centreline is the one column the seated valves leave open the whole way up —
  tube, posts and spades all a seat's own geometry away — so the screw head and its key
  come down clear. The other half of the joint is a boss printed in whatever carries the
  tray; the aft stand's two live in the foam cap's deck-mount table.

Each cell is symmetric under a half turn about Z, so a valve seats either way
round: the tray locates a valve and never fixes which end of its port is the
inlet.

## Boundary

`port_collets()` is the whole boundary — four bare collet tips, keyed
seat-then-end by sign (`xn-yp` is the −X seat's +Y collet). Nothing is turned
onto any of them.

No fitting seats on this tray: no groove, no wall, no boss reaching a divider or
a tee. Which fitting joins a pair is a question about where the pair's two ports
end up — a Y-divider takes two ports side by side, a Tee takes one above the
other — and that follows the tray's pose in the enclosure, not the tray.

## Open

- **Nothing holds a tray above this one off these coils.** The plate is [9](PLATE_Z) mm of
  floor and the valves stand [56.6](COIL_TOP) mm on it. The enclosure that seats these
  five carries the stack pitch (`_contents.tray_stack_pitch`); the standoff that
  sets it is still owed, and three trays now stand on it. What is under the bottom
  one is the band `_contents.tray_column_floor` measures — service space, with no line
  crossing in it, standing on the refrigeration stratum's roof.
  The two aloft have theirs: their floor is the foam cap's own lid, and their mount
  ears bolt them to columns in its deck-mount table.
- **Nothing holds the valve down.** Sockets, saddle and boss locate it and carry
  it; lifting it out takes no tool. The gap the enclosure's stack pitch leaves over
  a tray's coils is [6](TRAY_TOP_Z) mm — the depth the corner posts stand in the
  sockets — so that lift is available with a tray above this one in place. It is also
  what fixes every tray's pose in the machine: plate up, valves loose in their
  sockets, so a yaw is the only turn any of the five has.
- **All five are placed**, in two stands. THREE make the front column's head column,
  one under the next, and that column is full: under the bottom plate is the
  refrigeration stratum's roof, with less than one stack pitch between them. The
  SOURCE pair — V-A · V-B — stands under the hopper's spout, both inlets aft and both
  outlets forward; the SELECTS pair — V-C · V-D — stands a stack pitch beneath it,
  inlets forward and outlets aft; the BAG-A pair — V-E · V-F — takes the bottom seat
  with its two valves seated opposite ways round, the bag's two ends forward and the
  pump row's two aft. TWO stand aloft, in the loft over the water deck, side by side
  rather than stacked: the BAG-B pair — V-H · V-I — clocked exactly as bag A is, and
  the NOZZLE GATES — V-G · V-J — one pack gap behind it, the one pair that meets at no
  junction and the only one whose outlets leave the machine. Each clocking puts that
  pair's two junction ports SIDE BY SIDE: Y-A and Y-B hang ahead of their pairs on
  their own port planes, and Y-E stands a Tee ACROSS the strip its pair leaves between
  the head column and the pump row. Bag B's pair reaches its reservoir directly and
  meets no junction at all.
  [`enclosure/README.md`](/hardware/printed-parts/enclosure/README.md) has the pack.

Generated by `two_valve_tray.py` → `two-valve-tray.step`; the tray with its two
valves seated is `two_valve_assembly.py` → `two-valve-assembly.step`. Regenerate
with `tools/cad-venv/bin/python two_valve_tray.py`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/two-valve-tray/two_valve_tray.py`
