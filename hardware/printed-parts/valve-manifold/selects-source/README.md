# Selects-source assembly

The manifold's front end as one node: the SOURCE pair over the SELECTS pair, and
the junction that joins them.

| Column | Above | Below |
|---|---|---|
| West | V-A — tap water | V-C — channel A select |
| East | V-B — hopper | V-D — channel B select |

[fluid-topology](/hardware/topology/fluid-topology.md) asks for a single node with
four leaves on it. Every mode opens exactly one of V-A · V-B and exactly one of
V-C · V-D, so the only traffic the node carries is **one source to one select** —
which pairs of leaves share a fitting inside it is a fact about the fitting, not
about the circuit.

## The H

Two trays a [65.6](STACK_PITCH) mm `tray_stack_pitch` apart put the four ports in two
COLUMNS. A Tee takes two ports lying in line, so each column is one Tee's **run**,
and the two branches face each other with one length of tube between them.

```
    V-A ──┬────────────── V-B        source tray
          │              │
        (tee)══crossbar══(tee)       the junction
          │              │
    V-C ──┴────────────── V-D        selects tray
```

Verticals first, then the bar that joins them. The kitchen edition runs the same
shape between its `source-select` and `bag-circuit` assemblies — a Tee inline on
each of two columns, standing on the line its two collets make — with the branches
leaving for the two pumps instead of meeting each other.

`../two-valve-tray/` says where this comes from: *"a Y-divider takes two ports side
by side, a Tee takes one above the other, and that is the tray's pose in the
enclosure rather than anything the tray declares."* Both trays here are in the pose
that makes it a Tee.

## Geometry

Origin = the column pair's centre in X, the trays' own centre in Y, Z = 0 at the
selects tray's valve mounting plane. Forward is −Y; all four junction ports face
that way.

- **The columns stand [4.94](COLUMN_SPREAD) mm off their own seats**, and the fitting is
  the whole reason. Two branches facing each other need
  [40.14](FACING_SPAN) mm — `2 × ` [20.07](BRANCH_REACH) — between their body centres before
  there is any tube at all, against a valve seat pitch of [34.25](SEAT_PITCH). So the
  columns sit [44.14](COLUMN_PITCH) mm apart and the crossbar is the [4](CROSSBAR) mm left over.
  Give the junction a tee compact enough to fit between the seats and the columns
  come home to their ports, crossbar longer for it — the layout reads the fitting,
  so it moves when the fitting does.
- **The columns stand [8](LEG_LEAD) mm forward of the collet plane**, which is one leg lead:
  a radius of tangent for the corner and one more so that tangent lands off the
  stub's end rather than on it. Each leg goes straight out on axis for exactly that,
  then turns down the column in one gentle move that carries the spread with it —
  so the spread costs no corner of its own.
- **The tee sits midway down the pitch**, leaving [12.73](TEE_STANDOFF) mm between each run
  collet face and the port plane it reaches. Its run half-length is [20.07](RUN_HALF).
- **Five lengths of tube**, [87.75](TUBE_TOTAL) mm of stock: two down each column, one across.

Both of the H's guards raise rather than fudge: a crossbar shorter than a butted
joint's exposed tube, and a run collet the stack pitch has pushed too near a port
plane to turn a leg in.

## Paths

Port to port, tube plus the fitting bodies the path passes through — `paths()`
quotes all four the same way:

| Mode | Through | Port to port |
|---|---|---|
| Tap → channel A | column west, one tee's whole run | [82.02](STRAIGHT_PATH) mm |
| Hopper → channel B | column east, one tee's whole run | [82.02](STRAIGHT_PATH) mm |
| Tap → channel B | half a run, both branches, the crossbar | [126.2](CROSSED_PATH) mm |
| Hopper → channel A | the same, mirrored | [126.2](CROSSED_PATH) mm |

The two straight modes are one column and nothing else: the crossbar carries only
the crossed pair. All four combinations exist — which pair is short is a property
of which valves share a column, not of what the node can reach.

## Boundary

`boundary_collets()` is the four AFT collets — the ones the H does not take. V-A-I
takes the flow regulator, V-B-I the hopper drain, V-C-O and V-D-O leave for the two
pump-inlet junctions. Everything forward of the trays belongs to this assembly.

## Open

- **The tee is a stand-in.** `../../../reference/tee-connector/` is McMaster
  51175K143, not the BOM's John Guest PP0208E, and its branch reach is the single
  number holding the columns off their seats. A measured PP0208E is what settles
  whether the spread is real or an artifact of the file that happened to be
  available.
- **Nothing seats the tees.** They hang on their tube like the enclosure's own six.
  A column that wants a cradle wants it from the tray under it, which carries no
  fitting today.
- **This is not the pack.** The enclosure builds its own front end from Y-dividers
  (`../../enclosure/enclosure-assembly/_contents`); this assembly stands beside it,
  reads its stack pitch and its tee, and is not placed in it.

Generated by `selects_source_assembly.py` → `selects-source-assembly.step`.
Regenerate with:

    tools/cad-venv/bin/python hardware/printed-parts/valve-manifold/selects-source/selects_source_assembly.py

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/selects-source/selects_source_assembly.py`
